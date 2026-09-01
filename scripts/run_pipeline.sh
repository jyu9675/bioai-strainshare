#!/usr/bin/env bash
# Run the downstream pipeline (03 map/profile -> 04 compare -> 07 metaphlan -> 05 analysis -> 06 plots)
# against the external drive D:. Reference (02) is already built. Run AFTER the fastq download finishes.
#   conda activate bioai && bash scripts/run_pipeline.sh [THREADS]
set -euo pipefail
cd "$(dirname "$0")/.."
THREADS=${1:-8}
# TMPDIR must be on the native Linux (ext4) fs: Python multiprocessing binds Unix-domain
# sockets here, and DrvFs mounts (/mnt/d, /mnt/c) don't support them (OSError 95).
# Only tiny scratch/sockets live here; all big outputs go to -o on /mnt/d.
export TMPDIR="${HOME:-/home/allen}/bioai_tmp"; mkdir -p "$TMPDIR"
REFS=/mnt/d/bioai/refs
DATA=/mnt/d/bioai/data/fastq
META=/mnt/d/bioai/data/metadata_subset.tsv
RES=/mnt/d/bioai/results

echo "### 03 map + profile"
bash scripts/03_map_profile.sh "$DATA" "$REFS" "$RES/profiles" "$THREADS"
echo "### 04 compare"
bash scripts/04_compare.sh "$RES/profiles" "$REFS" "$RES/compare.IS" "$THREADS"
echo "### 07 metaphlan (community table)"
bash scripts/07_metaphlan.sh "$DATA" "$RES/metaphlan" "$THREADS"
echo "### 05 shared-strain analysis"
python scripts/05_shared_strain_analysis.py \
  --compare "$RES"/compare.IS/output/*_genomeWide_compare.tsv \
  --meta "$META" --metaphlan "$RES/metaphlan/merged_metaphlan.tsv" --outdir "$RES"
echo "### 09 generalist filter (M5)"
python scripts/09_generalist_filter.py --pairs "$RES/pairs_tagged.tsv" \
  --candidates "$RES/translocation_candidates.tsv" \
  --config scripts/strainshare_standard.yaml --outdir "$RES"
echo "### 08 direction inference (M4)"
python scripts/08_direction.py --candidates "$RES/translocation_candidates.tsv" \
  --pairs "$RES/pairs_tagged.tsv" --meta "$META" \
  --config scripts/strainshare_standard.yaml --outdir "$RES"
echo "### 06 figures"
python scripts/06_plots.py --pairs "$RES/pairs_tagged.tsv" \
  --candidates "$RES/translocation_candidates.tsv" --meta "$META" --outdir "$RES/figures"
echo "### PIPELINE DONE -> $RES  (tables + figures/ + direction_calls + generalist flags)"
