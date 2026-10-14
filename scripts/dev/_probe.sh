#!/usr/bin/env bash
# Quick size/count probe of the PRJNA288562 WGS subset before bulk download.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data
curl -s "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA288562&result=read_run&fields=run_accession,library_strategy,library_source,fastq_bytes&format=tsv" > data/probe.tsv

echo "total runs: $(($(wc -l < data/probe.tsv) - 1))"
echo "WGS runs: $(awk -F'\t' 'NR>1 && $2=="WGS"' data/probe.tsv | wc -l)"
echo "--- library_strategy breakdown ---"
tail -n +2 data/probe.tsv | cut -f2 | sort | uniq -c
echo "--- WGS download size ---"
awk -F'\t' 'NR>1 && $2=="WGS"{n=split($4,a,";"); for(i=1;i<=n;i++) s+=a[i]} END{printf "%.2f GB across fastq files\n", s/1e9}' data/probe.tsv
