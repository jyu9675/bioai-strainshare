#!/usr/bin/env bash
# inStrain compare hangs doing random HDF5 reads over the USB/DrvFs mount.
# Stage profiles in RAM (/dev/shm), compare single-process (avoids the multiprocessing crash),
# TMPDIR on ext4 (spare RAM). Persistent log on ext4 so it survives cleanup.
set -uo pipefail
export TMPDIR=/home/allen/bioai_tmp; mkdir -p "$TMPDIR"
SRC=/mnt/d/bioai/results/profiles
REFS=/mnt/d/bioai/refs
RAM=/dev/shm/profiles
OUT=/mnt/d/bioai/results/compare.IS
LOG=/home/allen/compare.log

rm -rf "$RAM"; mkdir -p "$RAM"
inputs=()
for d in "$SRC"/*.IS; do
  if [[ -f "$d/raw_data/covT.hd5" ]] && grep -q covT "$d/raw_data/attributes.tsv" 2>/dev/null; then
    cp -r "$d" "$RAM/" && inputs+=("$RAM/$(basename "$d")")
  fi
done
echo "staged ${#inputs[@]} profiles in RAM ($(du -sh "$RAM"|cut -f1)); starting compare -p 1"

rm -rf /dev/shm/compare.IS "$OUT"
inStrain compare -i "${inputs[@]}" -o /dev/shm/compare.IS -s "$REFS/vagref.stb" -p 1 > "$LOG" 2>&1
rc=$?
echo "compare exit=$rc"
if [[ -d /dev/shm/compare.IS/output ]]; then
  cp -r /dev/shm/compare.IS "$OUT"; echo "COMPARE OK -> $OUT"; ls "$OUT/output/"
else
  echo "COMPARE FAILED (rc=$rc); tail log:"; tail -8 "$LOG"
fi
rm -rf "$RAM" /dev/shm/compare.IS
