#!/usr/bin/env bash
# Verify the tool stack is installed and on PATH before starting a real run.
# Usage: bash scripts/check_env.sh
miss=0
check() { if command -v "$1" >/dev/null 2>&1; then
    printf "  ok   %-20s %s\n" "$1" "$(command -v "$1")"
  else
    printf "  MISS %-20s (%s)\n" "$1" "$2"; miss=$((miss+1)); fi; }

echo "== core =="
check python3   "conda install python"
check curl      "download"
check wget      "download"
echo "== reference / mapping =="
check dRep      "pip install drep"
check bowtie2   "conda install -c bioconda bowtie2"
check bowtie2-build "part of bowtie2"
check samtools  "conda install -c bioconda samtools"
check parse_stb.py  "pip install instrain (dRep helper)"
echo "== strain / composition =="
check inStrain   "pip install instrain"
check metaphlan  "conda install -c bioconda metaphlan"
check merge_metaphlan_tables.py "part of metaphlan"
echo "== python libs =="
python3 - <<'PY'
import importlib.util, sys
miss = [m for m in ("pandas","numpy","matplotlib") if importlib.util.find_spec(m) is None]
print("  ok   python libs: pandas numpy matplotlib" if not miss
      else "  MISS python libs: " + " ".join(miss) + "  (pip install " + " ".join(miss) + ")")
sys.exit(1 if miss else 0)
PY
pylibs=$?
echo
if [[ $miss -eq 0 && $pylibs -eq 0 ]]; then
  echo "All tools present — ready to run 01→06."
else
  echo "$miss tool(s) missing above. Install them before running the pipeline."; exit 1
fi
