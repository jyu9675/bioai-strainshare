#!/usr/bin/env bash
# Re-download all fastqs for runs that had a corrupt file. Deletes local copies first
# (so wget fetches fresh instead of resuming a corrupt file), then verifies gzip integrity.
set -uo pipefail
F=/mnt/d/bioai/data/fastq
LIST=/mnt/d/bioai/data/download_subset.txt
RUNS="SRR6748006 SRR6748035 SRR6748049 SRR6748051"

# delete every local file for the affected runs
for r in $RUNS; do rm -f "$F/$r"*.fastq.gz; done

# re-download their URLs fresh
grep -E "$(echo $RUNS | tr ' ' '|')" "$LIST" | xargs -n1 -P4 wget -q -P "$F"

echo "=== re-verify ==="
bad=0
for r in $RUNS; do
  for g in "$F/$r"*.fastq.gz; do
    if gzip -t "$g" 2>/dev/null; then echo "  ok $(basename "$g")"; else echo "  STILL BAD $(basename "$g")"; bad=$((bad+1)); fi
  done
done
echo "still corrupt: $bad"
