#!/usr/bin/env bash
# Download the subset fastqs (4 parallel, resumable). Heavy data -> external drive D:.
# Usage: bash _download_subset.sh [LIST] [DEST]
set -euo pipefail
LIST=${1:-/mnt/d/bioai/data/download_subset.txt}
DEST=${2:-/mnt/d/bioai/data/fastq}
mkdir -p "$DEST"
echo "start: $(date)  files: $(wc -l < "$LIST")  dest: $DEST"
xargs -a "$LIST" -n1 -P4 wget -q -c -P "$DEST"
echo "done: $(date)  files: $(ls "$DEST" | wc -l), size: $(du -sh "$DEST" | cut -f1)"
