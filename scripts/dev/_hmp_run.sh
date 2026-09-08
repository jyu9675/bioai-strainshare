#!/usr/bin/env bash
# HMP gut<->vaginal strain-sharing run (34 paired women, phs000228 / HMASM WGS).
# Designed to run ON an EC2 instance in us-west-2 (data-local to the HMP S3 bucket:
# downloads are fast and egress-free there). It streams each sample's tarball from S3,
# extracts the QC'd/host-removed FASTQs, maps -> inStrain profile, deletes the raw
# reads on success (so peak disk stays small), then compares and runs strainshare.
#
#   REQUIRES: conda env with bowtie2, samtools, inStrain, awscli, and the strainshare pkg;
#             a prebuilt broad reference ($REF.fna + $REF.stb + bowtie2 index $REF.*.bt2).
#             Build one with scripts/dev/_build_broadref.sh (extend it to cover the HMP
#             gut<->vaginal targets: E. coli / Enterobacteriaceae, Prevotella spp.,
#             Bacteroides spp., plus the vaginal set). Reference breadth is THE sensitivity
#             lever — a narrow reference throttles cross-site detection (see docs).
#
# Usage (on the EC2 box):
#   REF=/data/refs/broadref OUT=/data/hmp MANIFEST=scripts/dev/hmp_metadata.tsv \
#   THREADS=16 bash scripts/dev/_hmp_run.sh
#
# Resumable: a completed sample has profiles/<SRS>.IS/.done and is skipped.
set -uo pipefail
REF=${REF:?set REF to the broad reference prefix (…/broadref => broadref.fna/.stb/.bt2)}
OUT=${OUT:-/data/hmp}
MANIFEST=${MANIFEST:-scripts/dev/hmp_metadata.tsv}
THREADS=${THREADS:-16}
S3=s3://human-microbiome-project/HHS/HMASM/WGS
VAG_SITES="posterior_fornix mid_vagina vaginal_introitus"
GUT_SITE="stool"
mkdir -p "$OUT/dl" "$OUT/profiles"

# ---- 1. resolve each SRS to its S3 tarball path (one listing per body site) --------------
MAP="$OUT/srs_s3map.tsv"
if [ ! -s "$MAP" ]; then
  : > "$MAP"
  for site in $VAG_SITES $GUT_SITE; do
    aws s3 ls --no-sign-request "$S3/$site/" 2>/dev/null \
      | awk -v s="$S3/$site" '{sub(/\.tar\.bz2$/,"",$4); if($4!="") print $4"\t"s"/"$4".tar.bz2"}' >> "$MAP"
  done
  echo "[hmp] resolved $(wc -l < "$MAP") sample paths"
fi
srs_path () { awk -F'\t' -v k="$1" '$1==k{print $2; exit}' "$MAP"; }

# ---- 2. per-sample: download -> extract -> map (unpaired) -> profile -> cleanup ----------
echo "[hmp] start $(date +%T)"
tail -n +2 "$MANIFEST" | while IFS=$'\t' read -r sample subject timepoint bodysite; do
  [ -z "$sample" ] && continue
  IS="$OUT/profiles/$sample.IS"
  if [ -f "$IS/.done" ]; then echo "[hmp] skip $sample (done)"; continue; fi
  path=$(srs_path "$sample")
  if [ -z "$path" ]; then echo "[hmp] NO S3 PATH for $sample — skipping"; continue; fi
  echo "[hmp] $sample ($bodysite, subj $subject t$timepoint)  <- $path"

  tb="$OUT/dl/$sample.tar.bz2"
  # robust download (verify it's a valid bzip2 archive; retry)
  tries=0
  while ! bzip2 -t "$tb" 2>/dev/null; do
    tries=$((tries+1)); [ $tries -gt 4 ] && { echo "[hmp]  DOWNLOAD FAILED $sample"; break; }
    rm -f "$tb"; aws s3 cp --no-sign-request "$path" "$tb" >/dev/null 2>&1 || true
  done
  bzip2 -t "$tb" 2>/dev/null || { rm -f "$tb"; continue; }

  tar -xjf "$tb" -C "$OUT/dl"                       # -> $OUT/dl/<SRS>/<SRS>.denovo_...{1,2,singleton}.fastq
  d="$OUT/dl/$sample"
  r1="$d/$sample.denovo_duplicates_marked.trimmed.1.fastq"
  r2="$d/$sample.denovo_duplicates_marked.trimmed.2.fastq"
  rs="$d/$sample.denovo_duplicates_marked.trimmed.singleton.fastq"
  reads=""; for f in "$r1" "$r2" "$rs"; do [ -s "$f" ] && reads="${reads:+$reads,}$f"; done
  if [ -z "$reads" ]; then echo "[hmp]  NO FASTQ in $sample"; rm -rf "$tb" "$d"; continue; fi

  # UNPAIRED mapping (-U): HMASM reads are human-screened, which desyncs mates; inStrain runs
  # with --pairing_filter all_reads downstream so per-read mapping is the robust choice.
  bowtie2 -x "$REF" -U "$reads" -p "$THREADS" 2>"$OUT/profiles/$sample.bt2.log" \
    | samtools sort -@ 2 -o "$OUT/profiles/$sample.bam" - && samtools index "$OUT/profiles/$sample.bam"
  inStrain profile "$OUT/profiles/$sample.bam" "$REF.fna" -o "$IS" -s "$REF.stb" \
    -p "$THREADS" --database_mode --pairing_filter all_reads >"$OUT/profiles/$sample.IS.log" 2>&1

  if ls "$IS/output/"*genome_info.tsv >/dev/null 2>&1; then
    touch "$IS/.done"
    rm -rf "$tb" "$d" "$OUT/profiles/$sample.bam"*   # keep only the .IS profile
    echo "[hmp]  profiled $sample"
    # real-time co-detection check (survives crashes via the on-disk log)
    if [ -f "$(dirname "$0")/hmp_codetect_watch.py" ]; then
      hit=$(HMP_OUT="$OUT" HMP_META="$MANIFEST" python3 "$(dirname "$0")/hmp_codetect_watch.py" 2>/dev/null)
      if [ -n "$hit" ]; then echo "$hit" | tee -a "$OUT/CODETECTIONS.log"; fi
    fi
  else
    rm -f "$OUT/profiles/$sample.bam"*
    echo "[hmp]  PROFILE FAILED $sample (kept tarball/fastq for retry)"
  fi
done
echo "[hmp] profiling loop done $(date +%T)"

# ---- 3. compare + strainshare analyze ---------------------------------------------------
echo "[hmp] inStrain compare"
inStrain compare -i "$OUT"/profiles/*.IS -o "$OUT/compare.IS" -s "$REF.stb" \
  -p "$THREADS" --database_mode >"$OUT/compare.log" 2>&1 || true
GW=$(find "$OUT/compare.IS/output" -name "*genomeWide_compare.tsv" 2>/dev/null | head -1 || true)
[ -n "${GW:-}" ] && cp "$GW" "$OUT/genomeWide_compare.tsv"

# community proxy (coverage matrix) for the contamination discriminator
python3 - "$OUT" <<'PY'
import sys, glob, os, pandas as pd
out=sys.argv[1]; rows=[]
for d in glob.glob(f"{out}/profiles/*.IS"):
    s=os.path.basename(d)[:-3]
    fs=glob.glob(f"{d}/output/*genome_info.tsv")
    if not fs: continue
    gi=pd.read_csv(fs[0], sep="\t"); cov="coverage" if "coverage" in gi.columns else gi.columns[1]
    for _,r in gi.iterrows(): rows.append(dict(sample=s, genome=r["genome"], coverage=float(r[cov])))
if rows:
    pd.DataFrame(rows).pivot_table(index="genome", columns="sample", values="coverage", aggfunc="mean")\
      .fillna(0).to_csv(f"{out}/community.tsv", sep="\t"); print("[hmp] community.tsv written")
PY

echo "[hmp] strainshare analyze (gut<->vagina)"
strainshare analyze \
  --compare "$OUT/genomeWide_compare.tsv" \
  --meta "$MANIFEST" \
  --metaphlan "$OUT/community.tsv" \
  --site-pair gut,vagina \
  --outdir "$OUT/strainshare_out" || echo "[hmp] (check flags: strainshare analyze --help)"
echo "[hmp] DONE -> $OUT   ($(date +%T))"
echo "[hmp] results: $OUT/strainshare_out  (shared-strain calls, within-vs-between null, figures)"
