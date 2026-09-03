#!/usr/bin/env bash
# One-off: prove the full real-data chain on 2 fetched subjects (cervix<->vagina).
# download -> bowtie2 map to vagref -> inStrain profile -> compare -> metadata + community proxy.
# Then `strainshare analyze --site-pair cervix,vagina` is run on the outputs (Windows side).
set -uo pipefail
PICK=${PICK:-/mnt/c/Jeanyu/BIOAI/_cx_pick.tsv}
OUT=${OUT:-/mnt/d/bioai/results/cx_test}
REF=${REF:-/mnt/d/bioai/refs/vagref}
mkdir -p "$OUT/fastq" "$OUT/profiles"
printf "sample\tsubject\ttimepoint\tbodysite\n" > "$OUT/metadata.tsv"

tail -n +2 "$PICK" | tr -d '\r' | while IFS=$'\t' read -r sample subject site rc mb fq1 fq2; do
  case "$site" in V) bs=vagina;; C) bs=cervix;; R) bs=rectum;; G) bs=gut;; O) bs=oral;; *) bs="$site";; esac
  printf "%s\t%s\t1\t%s\n" "$sample" "$subject" "$bs" >> "$OUT/metadata.tsv"
  if [ -f "$OUT/profiles/$sample.IS/.done" ]; then echo "[cx] skip $sample (done)"; continue; fi
  echo "[cx] downloading $sample ($site, ${rc} reads)"
  ok=1
  for f in 1 2; do
    url=$fq1; [ "$f" = 2 ] && url=$fq2
    dest="$OUT/fastq/${sample}_${f}.fq.gz"; tries=0
    while ! gzip -t "$dest" 2>/dev/null; do
      tries=$((tries+1)); [ $tries -gt 5 ] && { ok=0; break; }
      [ $tries -ge 2 ] && rm -f "$dest"          # full re-download if resume didn't fix it
      wget -q -c --timeout=180 --tries=3 -O "$dest" "$url" || true
    done
    [ $ok = 0 ] && break
  done
  if [ $ok = 0 ]; then echo "[cx]   DOWNLOAD FAILED $sample (kept partial for resume)"; continue; fi
  bowtie2 -x "$REF" -1 "$OUT/fastq/${sample}_1.fq.gz" -2 "$OUT/fastq/${sample}_2.fq.gz" -p 4 2>/dev/null \
    | samtools sort -@2 -o "$OUT/profiles/$sample.bam" - && samtools index "$OUT/profiles/$sample.bam"
  # --pairing_filter all_reads: host-removal (e.g. PRJNA826539) breaks mate-pairing metadata,
  # which inStrain's default paired_only rejects wholesale ("no paired reads").
  inStrain profile "$OUT/profiles/$sample.bam" "$REF.fna" -o "$OUT/profiles/$sample.IS" -s "$REF.stb" \
    -p 4 --database_mode --pairing_filter all_reads >/dev/null 2>&1
  if ls "$OUT/profiles/$sample.IS/output/"*genome_info.tsv >/dev/null 2>&1; then
    touch "$OUT/profiles/$sample.IS/.done"
    rm -f "$OUT/fastq/${sample}_"*.fq.gz "$OUT/profiles/$sample.bam"*
    echo "[cx]   profiled $sample"
  else
    rm -f "$OUT/profiles/$sample.bam"*
    echo "[cx]   PROFILE FAILED $sample (kept fastq for retry)"
  fi
done

echo "[cx] compare"
inStrain compare -i "$OUT"/profiles/*.IS -o "$OUT/compare.IS" -s "$REF.stb" -p 4 --database_mode >/dev/null 2>&1 || true
GW=$(find "$OUT/compare.IS/output" -name "*genomeWide_compare.tsv" 2>/dev/null | head -1 || true)
if [ -n "${GW:-}" ] && [ -s "$GW" ]; then
  cp "$GW" "$OUT/genomeWide_compare.tsv"; echo "[cx] compare rows: $(( $(wc -l < "$OUT/genomeWide_compare.tsv") - 1 ))"
else echo "[cx] NO compare table (breadth too low)"; fi

# community proxy from inStrain genome_info coverage
python3 - "$OUT" <<'PY'
import sys, glob, os
import pandas as pd
out = sys.argv[1]; rows = []
for d in glob.glob(f"{out}/profiles/*.IS"):
    s = os.path.basename(d)[:-3]
    fs = glob.glob(f"{d}/output/*genome_info.tsv")
    if not fs: continue
    gi = pd.read_csv(fs[0], sep="\t")
    cov = "coverage" if "coverage" in gi.columns else gi.columns[1]
    for _, r in gi.iterrows():
        rows.append(dict(sample=s, genome=r["genome"], coverage=float(r[cov])))
if rows:
    m = pd.DataFrame(rows).pivot_table(index="genome", columns="sample", values="coverage", aggfunc="mean").fillna(0)
    m.to_csv(f"{out}/community.tsv", sep="\t"); print("[cx] community.tsv", m.shape)
else:
    print("[cx] no genome_info")
PY
echo "[cx] DONE -> $OUT"
