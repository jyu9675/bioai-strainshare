#!/usr/bin/env bash
# Verify that re-profiling WITHOUT database_mode lets inStrain compare run to completion.
set -uo pipefail
export TMPDIR=/home/allen/bioai_tmp; mkdir -p "$TMPDIR"
P=/mnt/d/bioai/results/profiles
REFS=/mnt/d/bioai/refs
A=SRR6747963; B=SRR6747964    # same subject (M4 gut), 2 genomes / 26 scaffolds each

for s in $A $B; do
  rm -rf "$P/$s.IS"
  inStrain profile "$P/$s.bam" "$REFS/vagref.fna" -o "$P/$s.IS" -s "$REFS/vagref.stb" -p 8 \
    > "$P/$s.profile.log" 2>&1 && echo "profiled $s" || echo "PROFILE FAILED $s"
done

rm -rf /home/allen/testcmp
inStrain compare -i "$P/$A.IS" "$P/$B.IS" -o /home/allen/testcmp -s "$REFS/vagref.stb" -p 8 \
  > /home/allen/testcmp.log 2>&1 && echo "COMPARE OK" || { echo "COMPARE FAILED"; tail -5 /home/allen/testcmp.log; }
echo "--- output files ---"
ls /home/allen/testcmp/output/ 2>/dev/null
