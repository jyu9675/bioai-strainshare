#!/usr/bin/env bash
# Produce the merged MetaPhlAn species table that 05_shared_strain_analysis.py needs
# for the Bray-Curtis (community-similarity) contamination filter.
# Runs on the same fastqs as the strain pipeline; independent of steps 02-04, so it can
# run in parallel. Output: results/metaphlan/merged_metaphlan.tsv
set -euo pipefail
DATA=${1:-/mnt/d/bioai/data/fastq}
OUT=${2:-/mnt/d/bioai/results/metaphlan}
THREADS=${3:-16}
DB=${4:-/mnt/d/bioai/refs/metaphlan_db}   # ~15GB DB MUST live on the external drive, not C:
mkdir -p "$OUT/profiles" "$DB"

for r1 in "$DATA"/*_1.f*q.gz; do
  s=$(basename "$r1"); s=${s%%_1.*}
  r2=${r1/_1./_2.}
  prof="$OUT/profiles/$s.mpa.tsv"
  [[ -s "$prof" ]] && continue
  echo "=== metaphlan $s ==="
  metaphlan "$r1,$r2" --input_type fastq --nproc "$THREADS" --db_dir "$DB" \
    --mapout "$OUT/profiles/$s.bt2.bz2" -o "$prof"
done

merge_metaphlan_tables.py "$OUT"/profiles/*.mpa.tsv > "$OUT/merged_metaphlan.tsv"
echo "Merged table: $OUT/merged_metaphlan.tsv"
echo "Note: 05 expects rows=species, cols=samples. If your MetaPhlAn version keeps full"
echo "lineage strings in the index, filter to s__ rows and strip prefixes, or pass as-is"
echo "(05 only needs matching sample columns + numeric rel-abundances)."
