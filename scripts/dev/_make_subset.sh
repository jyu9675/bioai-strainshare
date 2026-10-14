#!/usr/bin/env bash
# Build a subset download list for chosen subjects (vagina+gut only) and their metadata.
# Usage: bash _make_subset.sh "M4 T7 T18 P2"
set -euo pipefail
cd "$(dirname "$0")/.."
SUBJECTS=${1:-"M4 T7 T18 P2"}

# 1. runs for chosen subjects, vagina+gut, from metadata.tsv
awk -F'\t' -v subs="$SUBJECTS" 'BEGIN{n=split(subs,a," "); for(i=1;i<=n;i++)want[a[i]]=1}
  NR==1{print > "data/metadata_subset.tsv"; next}
  ($2 in want) && ($4=="vagina"||$4=="gut"){print $1 > "data/subset_runs.txt"; print >> "data/metadata_subset.tsv"}' data/metadata.tsv

echo "subset runs: $(wc -l < data/subset_runs.txt)  subjects: $SUBJECTS"

# 2. fetch run->fastq_ftp map, join to subset runs -> URL list
curl -s "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA288562&result=read_run&fields=run_accession,fastq_ftp&format=tsv" > data/ftp_map.tsv
awk -F'\t' 'NR==FNR{keep[$1]=1; next} FNR>1 && ($1 in keep){n=split($2,u,";"); for(i=1;i<=n;i++) if(u[i]!="") print "https://"u[i]}' \
  data/subset_runs.txt data/ftp_map.tsv > data/download_subset.txt

echo "fastq files to download: $(wc -l < data/download_subset.txt)"
