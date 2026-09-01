#!/usr/bin/env bash
# List profiles that lack covT (near-empty; break inStrain compare) vs good ones.
set -uo pipefail
P=/mnt/d/bioai/results/profiles
: > /mnt/d/bioai/data/good_profiles.txt
bad=0; good=0
for d in "$P"/*.IS; do
  b=$(basename "$d")
  if [ -f "$d/raw_data/covT.hd5" ] && grep -q "covT" "$d/raw_data/attributes.tsv" 2>/dev/null; then
    echo "$d" >> /mnt/d/bioai/data/good_profiles.txt
    good=$((good+1))
  else
    echo "BAD (no covT): $b"
    bad=$((bad+1))
  fi
done
echo "good: $good  bad: $bad"
