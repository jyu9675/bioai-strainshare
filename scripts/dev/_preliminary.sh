#!/usr/bin/env bash
# Preliminary results from whatever profiles are complete: clean partials, run compare,
# and dump a per-sample genome-detection summary.
set -uo pipefail
export TMPDIR=/home/allen/bioai_tmp; mkdir -p "$TMPDIR"
P=/mnt/d/bioai/results/profiles
REFS=/mnt/d/bioai/refs
R=/mnt/d/bioai/results

# 1. drop any incomplete .IS (interrupted mid-write => no output/ dir)
for d in "$P"/*.IS; do
  [[ -d "$d/output" ]] || { echo "removing partial: $(basename "$d")"; rm -rf "$d"; }
done
n=$(ls -d "$P"/*.IS 2>/dev/null | wc -l)
echo "complete profiles: $n"

# 2. compare all complete profiles
rm -rf "$R/compare.IS"
inStrain compare -i "$P"/*.IS -o "$R/compare.IS" -s "$REFS/vagref.stb" -p 8 > "$R/compare_prelim.log" 2>&1 \
  && echo "COMPARE OK" || { echo "COMPARE FAILED"; tail -5 "$R/compare_prelim.log"; }

# 3. per-sample genome detection summary (genome, coverage, breadth) -> composition.tsv
echo -e "sample\tgenome\tcoverage\tbreadth" > "$R/composition.tsv"
for g in "$P"/*.IS/output/*_genome_info.tsv; do
  s=$(basename "$g"); s=${s%%.IS*}
  awk -F'\t' -v s="$s" 'NR==1{for(i=1;i<=NF;i++)h[$i]=i; next}
    {print s"\t"$h["genome"]"\t"$h["coverage"]"\t"$h["breadth"]}' "$g" >> "$R/composition.tsv"
done
echo "wrote $R/composition.tsv ($(($(wc -l < "$R/composition.tsv")-1)) genome-detections)"
ls "$R/compare.IS/output/" 2>/dev/null
