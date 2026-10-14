#!/usr/bin/env bash
# Full HMP Aim-1 run: all 34 women / 99 samples, into one output dir so the funnel sees the
# whole cohort. Reuses any profiles already finished by the 5-woman pilot (no re-download).
#
#   REF=/mnt/d/bioai/refs/broadref/broadref \
#   OUT=/mnt/d/bioai/results/hmp_full \
#   PILOT=/mnt/d/bioai/results/hmp_pilot5 \
#   MANIFEST=/mnt/c/Jeanyu/BIOAI/scripts/dev/hmp_metadata.tsv \
#   THREADS=4  bash scripts/dev/_hmp_run_full.sh
#
# Resumable + bandwidth-bound; safe to kill and re-launch (the .done gate skips finished samples).
set -uo pipefail
REF=${REF:?}; OUT=${OUT:-/mnt/d/bioai/results/hmp_full}
PILOT=${PILOT:-/mnt/d/bioai/results/hmp_pilot5}
MANIFEST=${MANIFEST:-/mnt/c/Jeanyu/BIOAI/scripts/dev/hmp_metadata.tsv}
THREADS=${THREADS:-4}
export TMPDIR=${TMPDIR:-/home/allen/bioai_tmp}
mkdir -p "$OUT/profiles" "$TMPDIR"

# 1. seed with completed pilot profiles (copy the whole <SRS>.IS dir if it has a .done)
if [ -d "$PILOT/profiles" ]; then
  n=0
  for d in "$PILOT"/profiles/*.IS; do
    [ -f "$d/.done" ] || continue
    b=$(basename "$d")
    if [ ! -f "$OUT/profiles/$b/.done" ]; then cp -r "$d" "$OUT/profiles/"; n=$((n+1)); fi
  done
  echo "[full] seeded $n finished pilot profiles into $OUT/profiles"
fi

# 2. hand off to the standard driver over the FULL manifest (it skips .done, downloads the rest,
#    then runs inStrain compare + strainshare analyze across all 99)
REF="$REF" OUT="$OUT" MANIFEST="$MANIFEST" THREADS="$THREADS" \
  bash "$(dirname "$0")/_hmp_run.sh"

# 3. the integrity-first funnel over the whole cohort
echo "[full] Aim-1 funnel"
python3 "$(dirname "$0")/hmp_aim1_funnel.py" \
  --profiles "$OUT/profiles" --compare "$OUT/genomeWide_compare.tsv" --meta "$MANIFEST" \
  --out "$OUT/aim1_funnel" || echo "[full] funnel: run manually once compare exists"
echo "[full] DONE -> $OUT/aim1_funnel/FUNNEL.txt"
