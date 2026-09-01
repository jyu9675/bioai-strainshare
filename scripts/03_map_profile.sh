#!/usr/bin/env bash
# Map each sample to the reference and run inStrain profile.
# Expects paired fastqs in DATA named <sample>_1.fastq.gz / <sample>_2.fastq.gz.
# Per-sample failures (e.g. a corrupt fastq) are logged and SKIPPED, not fatal, so one
# bad file can't abort the whole run. Resumable: existing BAM/.IS are skipped.
set -uo pipefail                       # NOT -e: we handle per-sample errors explicitly
DATA=${1:-/mnt/d/bioai/data/fastq}
REFS=${2:-/mnt/d/bioai/refs}
OUT=${3:-/mnt/d/bioai/results/profiles}
THREADS=${4:-8}
mkdir -p "$OUT"
FAILED="$OUT/failed_samples.txt"; : > "$FAILED"

for r1 in "$DATA"/*_1.f*q.gz; do
  s=$(basename "$r1"); s=${s%%_1.*}
  r2=${r1/_1./_2.}
  bam="$OUT/$s.bam"
  echo "=== $s ==="
  # --- map (skip if BAM already present and non-empty) ---
  if [[ ! -s "$bam" ]]; then
    if ! bowtie2 -x "$REFS/vagref" -1 "$r1" -2 "$r2" -p "$THREADS" 2>"$OUT/$s.map.log" \
         | samtools sort -@4 -o "$bam" 2>>"$OUT/$s.map.log"; then
      echo "$s	mapping_failed" >> "$FAILED"; rm -f "$bam"; echo "  !! mapping failed, skipping"; continue
    fi
    samtools index "$bam" 2>>"$OUT/$s.map.log" || true
  fi
  # --- profile (skip if .IS already present) ---
  if [[ ! -d "$OUT/$s.IS" ]]; then
    # NO --database_mode: our reference is tiny (8 genomes). database_mode stores a reduced
    # profile (skips mm profiling, drops covT) that inStrain compare then can't read.
    if ! inStrain profile "$bam" "$REFS/vagref.fna" -o "$OUT/$s.IS" -s "$REFS/vagref.stb" \
         -p "$THREADS" >"$OUT/$s.profile.log" 2>&1; then
      echo "$s	profile_failed" >> "$FAILED"; rm -rf "$OUT/$s.IS"; echo "  !! profile failed, skipping"; continue
    fi
  fi
done

nf=$(grep -c . "$FAILED" 2>/dev/null || echo 0)
echo "done. profiles: $(ls -d "$OUT"/*.IS 2>/dev/null | wc -l), failed: $nf (see $FAILED)"
echo "(keep genome instances with coverage >=5x, breadth >=0.5 downstream)"
