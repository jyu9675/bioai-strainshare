#!/usr/bin/env bash
# TEST: can the all-N inStrain compare (which OOM'd at 15GB) now complete with 25GB RAM?
# Stage all covT-good profiles in RAM, run one compare over all of them.
set -uo pipefail
export TMPDIR=/home/allen/bioai_tmp; mkdir -p "$TMPDIR"
RAM=/dev/shm/allprof; rm -rf "$RAM"; mkdir -p "$RAM"
n=0
for d in /mnt/d/bioai/results/profiles/*.IS; do
  if [[ -f "$d/raw_data/covT.hd5" ]] && grep -q covT "$d/raw_data/attributes.tsv" 2>/dev/null; then
    cp -r "$d" "$RAM/"; n=$((n+1))
  fi
done
echo "staged $n profiles in RAM ($(du -sh "$RAM"|cut -f1)); /dev/shm:"; df -h /dev/shm | tail -1
echo "starting all-N compare -p 4 ..."
rm -rf /dev/shm/compare_all /mnt/d/bioai/results/compare_all.IS
/usr/bin/time -v inStrain compare -i "$RAM"/*.IS -o /dev/shm/compare_all \
  -s /mnt/d/bioai/refs/vagref.stb -p 4 > /home/allen/compare_all.log 2>&1
rc=$?
echo "compare exit=$rc"
if [[ -d /dev/shm/compare_all/output ]]; then
  cp -r /dev/shm/compare_all /mnt/d/bioai/results/compare_all.IS
  echo "ALL-N COMPARE OK -> results/compare_all.IS"; ls /mnt/d/bioai/results/compare_all.IS/output/
  grep -E "Maximum resident|Elapsed" /home/allen/compare_all.log
else
  echo "FAILED (rc=$rc):"; tail -6 /home/allen/compare_all.log
fi
rm -rf "$RAM" /dev/shm/compare_all
