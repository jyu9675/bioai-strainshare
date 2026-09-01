#!/usr/bin/env bash
# Download the WGS (shotgun) subset of PRJNA288562 from ENA.
# Most runs in this BioProject are 16S amplicon (useless for strain calls) -- we filter to WGS.
set -euo pipefail
OUT=${1:-../data}
mkdir -p "$OUT"

# 1. Run table with strategy + fastq URLs + metadata alias
curl -s "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA288562&result=read_run&fields=run_accession,library_strategy,library_source,sample_alias,fastq_ftp&format=tsv" \
  > "$OUT/prjna288562_runs.tsv"

# 2. Keep only shotgun rows. Filter on library_strategy==WGS ONLY:
#    library_source is METAGENOMIC for amplicon rows too, so it can't be used to exclude 16S.
awk -F'\t' 'NR==1 || $2=="WGS"' "$OUT/prjna288562_runs.tsv" > "$OUT/wgs_runs.tsv"
echo "WGS runs: $(($(wc -l < "$OUT/wgs_runs.tsv") - 1))"

# 3. Download fastqs (4 parallel). Recover subject/timepoint/bodysite from sample_alias + SraRunTable.
cut -f5 "$OUT/wgs_runs.tsv" | tail -n +2 | tr ';' '\n' | sed 's#^#https://#' \
  | xargs -n1 -P4 wget -c -P "$OUT"
echo "Done. Also pull SraRunTable from SRA Run Selector for subject/timepoint/site metadata."
