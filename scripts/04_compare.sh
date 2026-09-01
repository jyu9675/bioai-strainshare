#!/usr/bin/env bash
# Compare all profiles pairwise. Within- and between-person comparisons come out of one run;
# they get sliced apart later by 05_shared_strain_analysis.py using the metadata.
set -uo pipefail
PROF=${1:-/mnt/d/bioai/results/profiles}
REFS=${2:-/mnt/d/bioai/refs}
OUT=${3:-/mnt/d/bioai/results/compare.IS}
THREADS=${4:-8}

# Include only profiles that actually stored a coverage table (covT). Near-empty samples
# (host-dominated vaginal swabs where almost nothing mapped) lack covT and make compare
# raise KeyError('covT'). Filter them out here.
inputs=()
for d in "$PROF"/*.IS; do
  [[ -f "$d/raw_data/covT.hd5" ]] && grep -q covT "$d/raw_data/attributes.tsv" 2>/dev/null && inputs+=("$d")
done
echo "compare inputs: ${#inputs[@]} profiles with covT (of $(ls -d "$PROF"/*.IS 2>/dev/null | wc -l))"

# NOTE: no --database_mode (it needs stored genome_level_info; plain compare uses the -s stb grouping).
inStrain compare -i "${inputs[@]}" -o "$OUT" -s "$REFS/vagref.stb" -p "$THREADS"
echo "Compare output: $OUT/output/*_genomeWide_compare.tsv"
