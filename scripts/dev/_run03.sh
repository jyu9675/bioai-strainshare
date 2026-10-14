#!/usr/bin/env bash
# Finish profiling: run step 03 with TMPDIR on ext4. Wrapper avoids inline $VAR expansion
# through the PowerShell->WSL bridge (which intermittently yields an empty TMPDIR).
set -uo pipefail
export TMPDIR=/home/allen/bioai_tmp
mkdir -p "$TMPDIR"
bash "$(dirname "$0")/03_map_profile.sh" \
  /mnt/d/bioai/data/fastq /mnt/d/bioai/refs /mnt/d/bioai/results/profiles 8
