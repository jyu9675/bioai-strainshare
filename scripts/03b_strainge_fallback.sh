#!/usr/bin/env bash
# ============================================================================
# M3 — low-biomass StrainGE fallback  [SCAFFOLD — not yet wired into run_pipeline]
# ============================================================================
# WHY: inStrain needs ~thousands of mapped reads / >6x for full breadth. Many
# low-biomass VAGINAL metagenomes never reach that, so inStrain silently drops
# the target. StrainGE detects strain sharing down to ~0.5x coverage — the
# defensible low-coverage bound (the 0.1x figure did NOT survive verification).
# Route only the targets that FAIL inStrain's coverage floor through StrainGE;
# keep inStrain popANI as the primary call where coverage allows.
#
# STATUS: interface + steps below are the intended contract. Fill in once a
# StrainGE reference DB is built for the vaginal/gut target species. Unix-only.
#
# Usage (intended):
#   bash scripts/03b_strainge_fallback.sh <fastq_dir> <strainge_db> <out_dir> [threads]
# ----------------------------------------------------------------------------
set -euo pipefail
FASTQ_DIR=${1:?fastq dir}
DB=${2:?strainge db dir (straingst kmerize + cluster output)}
OUT=${3:?out dir}
THREADS=${4:-8}
COV_MIN=0.5   # keep in sync with strainshare_standard.yaml: low_biomass.strainge_fallback_coverage_min

mkdir -p "$OUT"
echo "[03b] StrainGE fallback — SCAFFOLD. Intended steps:"
cat <<'STEPS'
  1. straingst kmerize   -> per-sample k-mer sketch (k=23) of reads
  2. straingst run       -> report closest reference strain(s) per sample vs the DB
  3. straingr prepare-ref + align + call -> per-sample variant calls for shared-strain comparison
  4. emit a table with the SAME columns as inStrain compare so downstream 05/08/09 are agnostic:
         genome  name1  name2  popANI  conANI  percent_genome_compared
     (compute ANI-equivalent from straingr shared-vs-total callable positions)
  5. merge with the inStrain genomeWide_compare.tsv, tagging `method={instrain,strainge}`.
STEPS
echo "[03b] TODO: implement once the StrainGE DB exists. Coverage floor = ${COV_MIN}x."
exit 0
