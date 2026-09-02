#!/usr/bin/env bash
# One-off: prove the full real-data chain on 2 fetched subjects (cervix<->vagina).
# download -> bowtie2 map to vagref -> inStrain profile -> compare -> metadata + community proxy.
# Then `strainshare analyze --site-pair cervix,vagina` is run on the outputs (Windows side).
set -uo pipefail
PICK=/mnt/c/Jeanyu/BIOAI/_cx_pick.tsv
OUT=/mnt/d/bioai/results/cx_test
REF=/mnt/d/bioai/refs/vagref
mkdir -p "$OUT/fastq" "$OUT/profiles"
printf "sample\tsubject\ttimepoint\tbodysite\n" > "$OUT/metadata.tsv"

tail -n +2 "$PICK" | tr -d '\r' | while IFS=$'\t' read -r sample subject site rc mb fq1 fq2; do
  bs=vagina; [ "$site" = "C" ] && bs=cervix
  printf "%s\t%s\t1\t%s\n" "$sample" "$subject" "$bs" >> "$OUT/metadata.tsv"
  if [ -f "$OUT/profiles/$sample.IS/.done" ]; then echo "[cx] skip $sample (done)"; continue; fi
  echo "[cx] downloading $sample ($site, ${rc} reads)"
  wget -q -O "$OUT/fastq/${sample}_1.fq.gz" "$fq1"
  wget -q -O "$OUT/fastq/${sample}_2.fq.gz" "$fq2"
  bowtie2 -x "$REF" -1 "$OUT/fastq/${sample}_1.fq.gz" -2 "$OUT/fastq/${sample}_2.fq.gz" -p 4 2>/dev/null \
    | samtools sort -@2 -o "$OUT/profiles/$sample.bam" - && samtools index "$OUT/profiles/$sample.bam"
  inStrain profile "$OUT/profiles/$sample.bam" "$REF.fna" -o "$OUT/profiles/$sample.IS" -s "$REF.stb" \
    -p 4 --database_mode >/dev/null 2>&1
  touch "$OUT/profiles/$sample.IS/.done"
  rm -f "$OUT/fastq/${sample}_"*.fq.gz "$OUT/profiles/$sample.bam"*
  echo "[cx]   profiled $sample"
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
