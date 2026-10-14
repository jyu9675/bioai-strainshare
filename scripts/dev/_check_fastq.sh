#!/usr/bin/env bash
# Test gzip integrity of all downloaded fastqs; list corrupt ones (candidates for re-download).
set -uo pipefail
F=/mnt/d/bioai/data/fastq
bad=0
: > /mnt/d/bioai/data/corrupt_fastq.txt
for g in "$F"/*.fastq.gz; do
  if ! gzip -t "$g" 2>/dev/null; then
    echo "CORRUPT: $(basename "$g")"
    basename "$g" >> /mnt/d/bioai/data/corrupt_fastq.txt
    bad=$((bad+1))
  fi
done
echo "checked: $(ls "$F"/*.fastq.gz | wc -l) files, corrupt: $bad"
echo "completed inStrain profiles: $(ls -d /mnt/d/bioai/results/profiles/*.IS 2>/dev/null | wc -l)/88"
