#!/usr/bin/env bash
# Build a broad vaginal+gut reference for cross-site strain sharing.
# Reuses the 8 existing vagref genomes and adds ~25 more. Resolves each species to a RefSeq
# assembly via NCBI eutils, then downloads the genome FASTA from NCBI's FTP (the `datasets`
# taxon query hangs from some networks; eutils + FTP-by-accession are reliable).
set -uo pipefail
OUT=${OUT:-/mnt/d/bioai/refs/broadref}
E="https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
mkdir -p "$OUT/genomes"
cp -n /mnt/d/bioai/refs/genomes/*.fna "$OUT/genomes/" 2>/dev/null || true   # reuse existing 8

SP=(
  # --- vaginal / CST species ---
  "Lactobacillus gasseri" "Lactobacillus mulieris"
  "Gardnerella leopoldii" "Gardnerella piotii" "Gardnerella swidsinskii"
  "Fannyhessea vaginae" "Prevotella amnii" "Prevotella timonensis" "Prevotella disiens"
  "Sneathia vaginalis" "Megasphaera lornae" "Mobiluncus curtisii"
  "Aerococcus christensenii" "Streptococcus agalactiae" "Finegoldia magna" "Bifidobacterium breve"
  # --- gut species ---
  "Bacteroides uniformis" "Segatella copri" "Escherichia coli" "Bifidobacterium longum"
  "Bifidobacterium adolescentis" "Akkermansia muciniphila" "Roseburia intestinalis"
  "Ruminococcus bromii" "Phocaeicola dorei" "Blautia wexlerae"
)

for s in "${SP[@]}"; do
  tag=$(echo "$s" | tr ' ' '_')
  [ -f "$OUT/genomes/${tag}.fna" ] && { echo "have $tag"; continue; }
  term=$(echo "$s" | sed 's/ /+/g')
  uid=$(curl -s --max-time 30 "$E/esearch.fcgi?db=assembly&term=${term}%5BOrganism%5D+AND+latest_refseq%5Bfilter%5D&retmax=1" \
        | grep -oE '<Id>[0-9]+' | head -1 | grep -oE '[0-9]+')
  if [ -z "$uid" ]; then echo "FAIL $tag (no assembly)"; sleep 0.4; continue; fi
  ftp=$(curl -s --max-time 30 "$E/esummary.fcgi?db=assembly&id=$uid" \
        | grep -oE '<FtpPath_RefSeq>[^<]*' | head -1 | sed 's/<FtpPath_RefSeq>//')
  if [ -z "$ftp" ]; then echo "FAIL $tag (no ftp path)"; sleep 0.4; continue; fi
  base=$(basename "$ftp")
  url=$(echo "$ftp/${base}_genomic.fna.gz" | sed 's|ftp://|https://|')
  if wget -q --timeout=120 "$url" -O "$OUT/genomes/${tag}.fna.gz" && gzip -t "$OUT/genomes/${tag}.fna.gz" 2>/dev/null; then
    gunzip -f "$OUT/genomes/${tag}.fna.gz"; echo "OK   $tag  ($base)"
  else
    rm -f "$OUT/genomes/${tag}.fna.gz"; echo "FAIL $tag (download)"
  fi
  sleep 0.4
done

# combined reference + scaffold-to-genome map + index
cat "$OUT"/genomes/*.fna > "$OUT/broadref.fna"
: > "$OUT/broadref.stb"
for g in "$OUT"/genomes/*.fna; do
  n=$(basename "$g")
  grep "^>" "$g" | sed 's/^>//' | awk -v nm="$n" '{print $1"\t"nm}' >> "$OUT/broadref.stb"
done
bowtie2-build --threads 4 "$OUT/broadref.fna" "$OUT/broadref" >/dev/null 2>&1
echo "DONE: $(ls "$OUT"/genomes/*.fna | wc -l) genomes, $(wc -l < "$OUT/broadref.stb") scaffolds"
