#!/usr/bin/env bash
# Check whether body site / subject is recoverable from ENA metadata for the WGS runs.
set -euo pipefail
cd "$(dirname "$0")/.."
curl -s "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA288562&result=read_run&fields=run_accession,library_strategy,sample_title,sample_alias&format=tsv" > data/meta_probe.tsv
echo "=== first WGS rows (run | strategy | sample_title | sample_alias) ==="
awk -F'\t' 'NR==1 || $2=="WGS"' data/meta_probe.tsv | head -12
echo
echo "=== body-site keyword counts in WGS sample_title+alias ==="
awk -F'\t' '$2=="WGS"{print tolower($3" "$4)}' data/meta_probe.tsv \
  | grep -oE 'vagin[a-z]*|stool|feces|rectal|gut|saliva|oral|tooth|gum|posterior fornix|buccal' \
  | sort | uniq -c | sort -rn
