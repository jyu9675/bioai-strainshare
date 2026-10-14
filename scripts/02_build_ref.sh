#!/usr/bin/env bash
# Build the focused reference DB for inStrain: concatenate genomes -> bowtie2 index -> scaffold-to-bin map.
# Genomes in $REFS/genomes/ are curated species representatives (from 02a_fetch_refs.sh), so they are
# already effectively dereplicated (distinct species, ANI<95%) -- no dRep/checkM step needed.
# If you later add many REDUNDANT genomes per species, dereplicate first:
#   dRep dereplicate $REFS/genome_db -g $REFS/genomes/*.fna --ignoreGenomeQuality -p $THREADS
# and point the cat/parse_stb below at $REFS/genome_db/dereplicated_genomes/.
set -euo pipefail
REFS=${1:-/mnt/d/bioai/refs}
THREADS=${2:-8}
cd "$REFS"

cat genomes/*.fna > vagref.fna
bowtie2-build --threads "$THREADS" vagref.fna vagref
parse_stb.py --reverse -f genomes/*.fna -o vagref.stb   # scaffold -> genome
echo "Reference ready: $REFS/vagref.fna ($(grep -c '^>' vagref.fna) contigs), index vagref.*, stb vagref.stb"
