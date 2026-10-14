#!/usr/bin/env bash
# Per-subject V/G/O sample counts + timepoint span, to plan a subset download.
set -euo pipefail
cd "$(dirname "$0")/.."
echo -e "subject\tvagina\tgut\toral\tdays"
awk -F'\t' 'NR>1{
  key=$2; site=$4; day=$3
  cnt[key SUBSEP site]++
  if(day!=""){ if(!(key in mn)||day<mn[key])mn[key]=day; if(!(key in mx)||day>mx[key])mx[key]=day }
  subs[key]=1
}
END{
  for(s in subs){
    v=cnt[s SUBSEP "vagina"]+0; g=cnt[s SUBSEP "gut"]+0; o=cnt[s SUBSEP "oral"]+0
    printf "%s\t%d\t%d\t%d\t%s-%s\n", s, v, g, o, mn[s], mx[s]
  }
}' data/metadata.tsv | sort -k2 -rn
echo
echo "Subjects with BOTH vagina>=2 and gut>=2 (usable for within-person sharing + temporal):"
awk -F'\t' 'NR>1{v[$2]+=($4=="vagina"); g[$2]+=($4=="gut")} END{for(s in v) if(v[s]>=2&&g[s]>=2) print "  "s" (V="v[s]", G="g[s]")"}' data/metadata.tsv
