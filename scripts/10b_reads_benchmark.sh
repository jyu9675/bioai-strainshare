#!/usr/bin/env bash
# ============================================================================
# 10b — REAL reads-mode benchmark (the empirical validation behind Study D Fig 3)
# ============================================================================
# Simulate reads from a real genome (SAME strain) and a diverged copy (DIFFERENT
# strain, known SNP rate) across a coverage grid, run the ACTUAL pipeline
# (wgsim -> bowtie2 -> inStrain profile/compare), and record real popANI per pair.
# This replaces the assumptions in `10_benchmark.py --mode model` with empirical
# tool behavior. Unix + bioai env only.
#
#   bash scripts/10b_reads_benchmark.sh <base.fna> <outdir> [threads] ["cov list"] [divergence]
#   e.g. bash scripts/10b_reads_benchmark.sh /mnt/d/bioai/refs/genomes/L_crispatus.fna \
#           /mnt/d/bioai/results/benchmark_reads 4 "0.5 2 30" 0.003
# ----------------------------------------------------------------------------
set -euo pipefail
BASE=${1:?base genome fasta}
OUT=${2:?output dir}
THREADS=${3:-4}
COVERAGES=${4:-"0.5 2 30"}
DIVERGENCE=${5:-0.003}          # SNP rate for the "different" strain (~0.3% -> popANI ~0.997)
READLEN=150

mkdir -p "$OUT"/ref "$OUT"/reads "$OUT"/profiles
cd "$OUT"
cp -f "$BASE" ref/base.fna

# --- build the "different strain": mutate base at a known SNP rate ---
python3 - ref/base.fna ref/diff.fna "$DIVERGENCE" <<'PY'
import sys, random
inp, outp, rate = sys.argv[1], sys.argv[2], float(sys.argv[3])
random.seed(42); bases = "ACGT"
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

# --- reference index + scaffold-to-bin map (map everything to base) ---
bowtie2-build --threads "$THREADS" ref/base.fna ref/base >/dev/null 2>&1
python3 - ref/base.fna ref/base.stb <<'PY'
import sys
with open(sys.argv[1]) as f, open(sys.argv[2], "w") as o:
    for line in f:
        if line.startswith(">"):
            o.write(line[1:].split()[0] + "\tbase_genome\n")
PY
GLEN=$(python3 -c "print(sum(len(l.strip()) for l in open('ref/base.fna') if not l.startswith('>')))")
echo "[10b] genome length = $GLEN bp; coverages = $COVERAGES; divergence = $DIVERGENCE"

sim_map_profile () {   # name  genome  coverage  seed
  local name=$1 genome=$2 cov=$3 seed=$4
  local N; N=$(python3 -c "print(max(1,int($cov*$GLEN/(2*$READLEN))))")
  wgsim -N "$N" -1 $READLEN -2 $READLEN -e 0.001 -r 0 -R 0 -S "$seed" \
    "$genome" reads/${name}_1.fq reads/${name}_2.fq >/dev/null 2>&1
  bowtie2 -x ref/base -1 reads/${name}_1.fq -2 reads/${name}_2.fq -p "$THREADS" 2>/dev/null \
    | samtools sort -@2 -o profiles/${name}.bam - && samtools index profiles/${name}.bam
  inStrain profile profiles/${name}.bam ref/base.fna -o profiles/${name}.IS -s ref/base.stb \
    -p "$THREADS" --database_mode >/dev/null 2>&1
  rm -f reads/${name}_1.fq reads/${name}_2.fq profiles/${name}.bam*   # reclaim space
  echo "[10b]   profiled $name (cov ${cov}x, N=$N pairs)"
}

printf "pair\tcoverage\ttruth\tpopANI\tpercent_genome_compared\n" > reads_pairs.tsv
for cov in $COVERAGES; do
  tag="c${cov/./p}"
  echo "[10b] === coverage ${cov}x ==="
  sim_map_profile "sameA_$tag" ref/base.fna "$cov" 11
  sim_map_profile "sameB_$tag" ref/base.fna "$cov" 22
  sim_map_profile "diff_$tag"  ref/diff.fna "$cov" 33
  # compare may legitimately fail at very low coverage (nothing clears the floor) ->
  # record NA (= no-call) and keep going instead of aborting the whole sweep.
  inStrain compare -i profiles/sameA_$tag.IS profiles/sameB_$tag.IS profiles/diff_$tag.IS \
    -o profiles/cmp_$tag.IS -s ref/base.stb -p "$THREADS" --database_mode >/dev/null 2>&1 || true
  GW=$(find profiles/cmp_$tag.IS/output -name "*genomeWide_compare.tsv" 2>/dev/null | head -1 || true)
  if [ -n "${GW:-}" ] && [ -s "$GW" ]; then
    python3 - "$GW" "$cov" "sameA_$tag" "sameB_$tag" "diff_$tag" >> reads_pairs.tsv <<'PY'
import sys
import pandas as pd
gw, cov, sA, sB, dF = sys.argv[1:6]
d = pd.read_csv(gw, sep="\t")
brcol = "percent_compared" if "percent_compared" in d.columns else "percent_genome_compared"
def get(a, b):
    m = d[(d.name1.str.contains(a) & d.name2.str.contains(b)) |
          (d.name1.str.contains(b) & d.name2.str.contains(a))]
    if len(m) == 0:
        return ("NA", "NA")
    r = m.iloc[0]
    return (r["popANI"], r[brcol])
for truth, (a, b) in [("same", (sA, sB)), ("diff", (sA, dF))]:
    p, br = get(a, b)
    print(f"{a}|{b}\t{cov}\t{truth}\t{p}\t{br}")
PY
  else
    printf "sameA_%s|sameB_%s\t%s\tsame\tNA\tNA\n" "$tag" "$tag" "$cov" >> reads_pairs.tsv
    printf "sameA_%s|diff_%s\t%s\tdiff\tNA\tNA\n"  "$tag" "$tag" "$cov" >> reads_pairs.tsv
    echo "[10b]   coverage ${cov}x: no comparison cleared the floor -> recorded no-call (expected at very low depth)"
  fi
  rm -rf profiles/sameA_$tag.IS profiles/sameB_$tag.IS profiles/diff_$tag.IS profiles/cmp_$tag.IS
done

echo "[10b] DONE -> $OUT/reads_pairs.tsv"
cat reads_pairs.tsv
