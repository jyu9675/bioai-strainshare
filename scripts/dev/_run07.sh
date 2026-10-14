#!/usr/bin/env bash
# Run MetaPhlAn (step 07) with TMPDIR on ext4 and DB on D:. Resumable (skips done .mpa.tsv).
set -uo pipefail
export TMPDIR=/home/allen/bioai_tmp
mkdir -p "$TMPDIR"
bash "$(dirname "$0")/07_metaphlan.sh" \
  /mnt/d/bioai/data/fastq /mnt/d/bioai/results/metaphlan 8 /mnt/d/bioai/refs/metaphlan_db
