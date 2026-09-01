#!/usr/bin/env bash
# ============================================================================
# 10c — SCALED reads benchmark: precision edge across species + near-boundary divergence
# ============================================================================
# For each target species, simulate a same-strain pair and REPS diverged strains at
# several near-threshold divergences, run the REAL wgsim->bowtie2->inStrain pipeline,
# and record popANI per pair. This maps the RESOLUTION LIMIT of the 0.999 threshold:
# a strain diverged < ~0.1% has popANI > 0.999 and is (correctly, but importantly)
# indistinguishable from identical.
#
# RESUMABLE: completed profiles (.IS/.done marker) and comparisons (pairs/*.tsv) are
# skipped, so if WSL SIGTERMs a long run you just relaunch the same command.
#
#   bash scripts/10c_reads_benchmark_scaled.sh <genomes_dir> <outdir> [threads] [coverage] [reps] ["divs"] ["species"]
#   e.g. bash scripts/10c_reads_benchmark_scaled.sh /mnt/d/bioai/refs/genomes \
#           /mnt/d/bioai/results/benchmark_scaled 4 20 3 "0.0005 0.001 0.002 0.003" \
#           "L_crispatus L_iners G_vaginalis"
# ----------------------------------------------------------------------------
set -euo pipefail
GENOMES=${1:?genomes dir (with <species>.fna)}
OUT=${2:?output dir}
THREADS=${3:-4}
COV=${4:-20}
REPS=${5:-3}
DIVS=${6:-"0.0005 0.001 0.002 0.003"}
SPECIES=${7:-"L_crispatus L_iners G_vaginalis"}
READLEN=150

mkdir -p "$OUT"/{ref,reads,profiles,pairs}
cd "$OUT"

mutate () {  # infile outfile rate seed
  python3 - "$1" "$2" "$3" "$4" <<'PY'
import sys, random
inp, outp, rate, seed = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
random.seed(seed); bases = "ACGT"
def mut(seq):
    s = list(seq)
    for i, c in enumerate(s):
        if c.upper() in bases and random.random() < rate:
            s[i] = random.choice([b for b in bases if b != c.upper()])
    return "".join(s)
hdr, buf = None, []
with open(inp) as f, open(outp, "w") as o:
    for line in f:
        if line.startswith(">"):
            if hdr: o.write(hdr + "\n" + mut("".join(buf)) + "\n")
            hdr, buf = line.rstrip() + "_div", []
        else:
            buf.append(line.strip())
    if hdr: o.write(hdr + "\n" + mut("".join(buf)) + "\n")
PY
}

profile_one () {  # name genome_fasta refprefix stb cov seed
  local name=$1 genome=$2 refp=$3 cov=$5 seed=$6
  if [ -f "profiles/${name}.IS/.done" ]; then echo "[10c]   skip (done) $name"; return; fi
  local glen; glen=$(python3 -c "print(sum(len(l.strip()) for l in open('$genome') if not l.startswith('>')))")
  local N; N=$(python3 -c "print(max(1,int($cov*$glen/(2*$READLEN))))")
  wgsim -N "$N" -1 $READLEN -2 $READLEN -e 0.001 -r 0 -R 0 -S "$seed" \
    "$genome" reads/${name}_1.fq reads/${name}_2.fq >/dev/null 2>&1
  bowtie2 -x "$refp" -1 reads/${name}_1.fq -2 reads/${name}_2.fq -p "$THREADS" 2>/dev/null \
    | samtools sort -@2 -o profiles/${name}.bam - && samtools index profiles/${name}.bam
  inStrain profile profiles/${name}.bam "${refp}.fna" -o profiles/${name}.IS -s "$4" \
    -p "$THREADS" --database_mode >/dev/null 2>&1
  touch "profiles/${name}.IS/.done"
  rm -f reads/${name}_1.fq reads/${name}_2.fq profiles/${name}.bam*
  echo "[10c]   profiled $name (cov ${cov}x, N=$N)"
}

compare_pair () {  # outkey nameA nameB stb species divergence rep truth
  local key=$1 a=$2 b=$3 stb=$4 sp=$5 div=$6 rep=$7 truth=$8
  if [ -f "pairs/${key}.tsv" ]; then return; fi
  inStrain compare -i profiles/${a}.IS profiles/${b}.IS -o profiles/cmp_${key}.IS \
    -s "$stb" -p "$THREADS" --database_mode >/dev/null 2>&1 || true
  local GW; GW=$(find profiles/cmp_${key}.IS/output -name "*genomeWide_compare.tsv" 2>/dev/null | head -1 || true)
  if [ -n "${GW:-}" ] && [ -s "$GW" ]; then
    python3 - "$GW" "$a" "$b" "$sp" "$div" "$rep" "$COV" "$truth" > "pairs/${key}.tsv" <<'PY'
import sys
import pandas as pd
gw, a, b, sp, div, rep, cov, truth = sys.argv[1:9]
d = pd.read_csv(gw, sep="\t")
brcol = "percent_compared" if "percent_compared" in d.columns else "percent_genome_compared"
m = d[(d.name1.str.contains(a) & d.name2.str.contains(b)) |
      (d.name1.str.contains(b) & d.name2.str.contains(a))]
if len(m):
    r = m.iloc[0]; pop, br = r["popANI"], r[brcol]
else:
    pop, br = "NA", "NA"
print(f"{sp}\t{div}\t{rep}\t{cov}\t{truth}\t{pop}\t{br}")
PY
  else
    printf "%s\t%s\t%s\t%s\t%s\tNA\tNA\n" "$sp" "$div" "$rep" "$COV" "$truth" > "pairs/${key}.tsv"
  fi
  rm -rf profiles/cmp_${key}.IS
}

seed=1000
for sp in $SPECIES; do
  base="$GENOMES/${sp}.fna"
  if [ ! -f "$base" ]; then echo "[10c] MISSING $base — skipping"; continue; fi
  echo "[10c] ===== species $sp ====="
  cp -f "$base" ref/${sp}.fna
  if [ ! -f "ref/${sp}.1.bt2" ]; then bowtie2-build --threads "$THREADS" ref/${sp}.fna ref/${sp} >/dev/null 2>&1; fi
  python3 - ref/${sp}.fna ref/${sp}.stb <<'PY'
import sys
with open(sys.argv[1]) as f, open(sys.argv[2], "w") as o:
    for line in f:
        if line.startswith(">"):
            o.write(line[1:].split()[0] + "\tbase_genome\n")
PY

  # same-strain pair (control)
  profile_one "${sp}_sameA" ref/${sp}.fna "ref/${sp}" "ref/${sp}.stb" "$COV" $((seed+1))
  profile_one "${sp}_sameB" ref/${sp}.fna "ref/${sp}" "ref/${sp}.stb" "$COV" $((seed+2))
  compare_pair "${sp}_same" "${sp}_sameA" "${sp}_sameB" "ref/${sp}.stb" "$sp" "0.0" "0" "same"

  # diverged strains: REPS each, across the near-boundary divergence sweep
  for div in $DIVS; do
    dtag="d${div/./p}"
    for rep in $(seq 1 "$REPS"); do
      dgen="ref/${sp}_${dtag}_r${rep}.fna"
      dname="${sp}_${dtag}_r${rep}"
      mutate ref/${sp}.fna "$dgen" "$div" $((seed + rep*7))
      profile_one "$dname" "$dgen" "ref/${sp}" "ref/${sp}.stb" "$COV" $((seed + 100 + rep*13))
      compare_pair "${sp}_${dtag}_r${rep}" "${sp}_sameA" "$dname" "ref/${sp}.stb" "$sp" "$div" "$rep" "diff"
      rm -f "$dgen"
    done
  done
  seed=$((seed + 500))
done

# assemble the master table from per-comparison files (idempotent on resume)
printf "species\tdivergence\trep\tcoverage\ttruth\tpopANI\tpercent_genome_compared\n" > scaled_reads.tsv
cat pairs/*.tsv >> scaled_reads.tsv
echo "[10c] DONE -> $OUT/scaled_reads.tsv  ($(( $(wc -l < scaled_reads.tsv) - 1 )) comparisons)"
