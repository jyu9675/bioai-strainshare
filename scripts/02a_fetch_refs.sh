#!/usr/bin/env bash
# Fetch reference genomes for the pilot's target + control species into refs/genomes/.
# Uses NCBI's static `datasets` binary (no conda solve). Tries the designated RefSeq
# reference first; falls back to one complete genome if no reference is designated.
set -euo pipefail
cd "$(dirname "$0")/.."
REFS=${1:-/mnt/d/bioai/refs}      # heavy refs on external drive by default
mkdir -p "$REFS/genomes" "$REFS/bin"
BIN="$REFS/bin/datasets"
if [[ ! -x "$BIN" ]]; then
  curl -sL -o "$BIN" https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets
  chmod +x "$BIN"
fi

# species -> output basename
species=(
  "Lactobacillus iners|L_iners"
  "Lactobacillus crispatus|L_crispatus"
  "Lactobacillus jensenii|L_jensenii"
  "Gardnerella vaginalis|G_vaginalis"
  "Prevotella bivia|P_bivia"
  "Bacteroides fragilis|B_fragilis"           # gut control / internal negative
  "Phocaeicola vulgatus|P_vulgatus"           # gut control
  "Faecalibacterium prausnitzii|F_prausnitzii" # gut control
)

fetch() { # $1=taxon  $2=basename
  local tax="$1" name="$2" zip="/tmp/${name}.zip" dir="/tmp/${name}"
  rm -rf "$zip" "$dir"
  # try designated reference; fall back to one complete genome
  if ! "$BIN" download genome taxon "$tax" --reference --include genome --filename "$zip" 2>/dev/null || [[ ! -s "$zip" ]]; then
    "$BIN" download genome taxon "$tax" --assembly-level complete --include genome --filename "$zip" 2>/dev/null || true
  fi
  [[ -s "$zip" ]] || { echo "  !! no genome for $tax"; return; }
  python -m zipfile -e "$zip" "$dir"
  # take the first assembly's fna (reference query returns 1; complete-level may return several)
  local fna; fna=$(find "$dir" -name '*.fna' | head -1)
  [[ -n "$fna" ]] || { echo "  !! no fna for $tax"; return; }
  # prefix contig headers with the species basename so dRep/inStrain keep them distinct
  awk -v p="$name" '/^>/{sub(/^>/,">"p"__")}1' "$fna" > "$REFS/genomes/${name}.fna"
  echo "  ok $name  ($(grep -c '^>' "$REFS/genomes/${name}.fna") contigs, $(du -h "$REFS/genomes/${name}.fna"|cut -f1))"
}

for row in "${species[@]}"; do
  IFS='|' read -r tax name <<< "$row"
  echo "-> $tax"
  fetch "$tax" "$name"
done
echo "done: $(ls "$REFS"/genomes/*.fna 2>/dev/null | wc -l) genomes in $REFS/genomes/"
