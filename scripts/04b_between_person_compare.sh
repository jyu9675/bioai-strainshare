#!/usr/bin/env bash
# ============================================================================
# 04b — between-person gut<->vagina pairwise compare (builds the NULL for F1/F5)
# ============================================================================
# The all-N `inStrain compare` OOMs on this cohort, so within-person pairs were done
# via a pairwise workaround. This adds a CAPPED, representative set of BETWEEN-person
# cross-site comparisons (unrelated subjects) so 05 can compute a real within-vs-between
# null and 09 has between-person data. Pairwise compare is cheap; only all-N blows up.
# RESUMABLE: per-pair results cached in pairs/, skipped on rerun.
#
#   bash scripts/04b_between_person_compare.sh <profiles_dir> <meta.tsv> <stb> <outdir> [threads] [cap]
#   e.g. bash scripts/04b_between_person_compare.sh /mnt/d/bioai/results/profiles \
#           /mnt/d/bioai/data/metadata_subset.tsv /mnt/d/bioai/refs/vagref.stb \
#           /mnt/d/bioai/results/between 4 40
# ----------------------------------------------------------------------------
set -euo pipefail
PROF=${1:?profiles dir (*.IS)}
META=${2:?metadata tsv (sample subject timepoint bodysite)}
STB=${3:?vagref.stb}
OUT=${4:?output dir}
THREADS=${5:-4}
CAP=${6:-40}
mkdir -p "$OUT"/pairs "$OUT"/cmp

# 1. enumerate between-person gut<->vagina sample pairs (unrelated subjects), capped + deterministic
python3 - "$META" "$PROF" "$CAP" "$OUT/pairlist.tsv" <<'PY'
import sys, os
import pandas as pd
meta, prof, cap, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
m = pd.read_csv(meta, sep="\t")
have = {d[:-3] for d in os.listdir(prof) if d.endswith(".IS")}
m = m[m["sample"].isin(have)]
gut = m[m.bodysite == "gut"]; vag = m[m.bodysite == "vagina"]
pairs = []
for _, g in gut.iterrows():
    for _, v in vag.iterrows():
        if g.subject != v.subject:
            pairs.append(tuple(sorted((g["sample"], v["sample"]))))
pairs = sorted(set(pairs))
if len(pairs) > cap:                        # deterministic even spread to the cap
    step = max(1, len(pairs) // cap)
    pairs = pairs[::step][:cap]
with open(out, "w") as o:
    for a, b in pairs:
        o.write(f"{a}\t{b}\n")
print(f"[04b] between-person gut<->vagina pairs: {len(pairs)} (cap {cap})")
PY

# 2. pairwise compare, resumable, normalize sample names to the SRR accession
printf "genome\tname1\tname2\tpopANI\tconANI\tpercent_genome_compared\n" > "$OUT/between_compare.tsv"
while IFS=$'\t' read -r A B; do
  key="${A}__${B}"
  if [ ! -f "$OUT/pairs/${key}.tsv" ]; then
    inStrain compare -i "$PROF/${A}.IS" "$PROF/${B}.IS" -o "$OUT/cmp/${key}.IS" \
      -s "$STB" -p "$THREADS" --database_mode >/dev/null 2>&1 || true
    GW=$(find "$OUT/cmp/${key}.IS/output" -name "*genomeWide_compare.tsv" 2>/dev/null | head -1 || true)
    if [ -n "${GW:-}" ] && [ -s "$GW" ]; then
      python3 - "$GW" > "$OUT/pairs/${key}.tsv" <<'PY'
import sys, re
import pandas as pd
d = pd.read_csv(sys.argv[1], sep="\t")
brcol = "percent_compared" if "percent_compared" in d.columns else "percent_genome_compared"
def norm(x):
    mo = re.search(r"SRR\d+", str(x));  return mo.group(0) if mo else str(x)
for _, r in d.iterrows():
    print(f"{r['genome']}\t{norm(r['name1'])}\t{norm(r['name2'])}\t{r['popANI']}\t{r.get('conANI', r['popANI'])}\t{r[brcol]}")
PY
    else
      : > "$OUT/pairs/${key}.tsv"            # no comparison cleared -> no rows (still marks pair done)
    fi
    rm -rf "$OUT/cmp/${key}.IS"
    echo "[04b] compared $A x $B"
  fi
  cat "$OUT/pairs/${key}.tsv" >> "$OUT/between_compare.tsv"
done < "$OUT/pairlist.tsv"
echo "[04b] DONE -> $OUT/between_compare.tsv ($(( $(wc -l < "$OUT/between_compare.tsv") - 1 )) rows)"
