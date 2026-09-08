#!/usr/bin/env bash
# ============================================================================================
# ONE-SHOT full HMP 34-woman gut<->vaginal strain-sharing (Aim 1) on a FRESH EC2 instance.
#
# Prereqs (see docs/hmp-aws-runbook.md):
#   - Region us-west-2 (the HMP bucket is there -> downloads are fast + egress-free)
#   - Ubuntu 22.04 or Amazon Linux 2023, >=16 vCPU, >=32 GB RAM
#   - A data volume with >=250 GB free, and WORK pointed at it (default $HOME/hmp)
#   - No AWS credentials needed (the bucket is public: aws s3 ... --no-sign-request)
#
# Run:
#   export WORK=/data/hmp           # a path on your big volume
#   curl -LsSf https://raw.githubusercontent.com/jyu9675/bioai-strainshare/main/scripts/dev/ec2_hmp_run.sh -o run.sh
#   bash run.sh 2>&1 | tee $WORK.log
#
# Outputs:
#   $WORK/run/aim1_funnel/FUNNEL.txt        the integrity-gated Aim-1 funnel over all 34 women
#   $WORK/run/CODETECTIONS.log              every within-woman gut<->vagina co-detection, live
# ============================================================================================
set -euo pipefail
WORK=${WORK:-$HOME/hmp}
THREADS=${THREADS:-$(nproc)}
REPO=${REPO:-$HOME/bioai-strainshare}
export TMPDIR=${TMPDIR:-$WORK/tmp}
mkdir -p "$WORK" "$TMPDIR"

# sanity: warn if the work volume looks small
avail_gb=$(df -BG --output=avail "$WORK" 2>/dev/null | tail -1 | tr -dc '0-9')
if [ -n "${avail_gb:-}" ] && [ "$avail_gb" -lt 200 ]; then
  echo "[ec2] WARNING: only ${avail_gb} GB free at $WORK — point WORK at a >=250 GB volume." >&2
fi

echo "[ec2] === 1/4 tools ==="
if [ ! -d "$HOME/mf" ]; then
  curl -LsSf "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh" -o /tmp/mf.sh
  bash /tmp/mf.sh -b -p "$HOME/mf"
fi
source "$HOME/mf/etc/profile.d/conda.sh"
CREATE=mamba; command -v mamba >/dev/null 2>&1 || CREATE=conda
conda env list | grep -q "^hmp " || $CREATE create -y -n hmp -c bioconda -c conda-forge \
  bowtie2 samtools instrain awscli pandas 'python=3.11' git
conda activate hmp

echo "[ec2] === 2/4 repo ==="
[ -d "$REPO/.git" ] || git clone https://github.com/jyu9675/bioai-strainshare.git "$REPO"
pip install -e "$REPO" -q 2>/dev/null || true

echo "[ec2] === 3/4 reference (self-contained, ~5 min) ==="
REF="$WORK/refs/broadref"
[ -f "$REF.1.bt2" ] || OUT="$WORK/refs/broadref" THREADS="$THREADS" \
  bash "$REPO/scripts/dev/_build_broadref_ec2.sh"

echo "[ec2] === 4/4 full 34-woman Aim-1 run (THREADS=$THREADS) ==="
# hmp_metadata_run.tsv = all 34 women / 98 samples (SRS013521 excluded: a pathological sample that
# hangs inStrain; woman 159227541 keeps 2 other stools + 2 vaginal, so she stays analyzable).
# To attempt the full 99 including SRS013521, set MANIFEST=.../hmp_metadata.tsv instead.
REF="$REF" OUT="$WORK/run" PILOT="$WORK/run" \
  MANIFEST="$REPO/scripts/dev/hmp_metadata_run.tsv" THREADS="$THREADS" \
  bash "$REPO/scripts/dev/_hmp_run_full.sh"

echo ""
echo "[ec2] ================ DONE ================"
echo "  Aim-1 funnel:   $WORK/run/aim1_funnel/FUNNEL.txt"
echo "  co-detections:  $WORK/run/CODETECTIONS.log   (empty = none found across all 34 women)"
echo "  full tables:    $WORK/run/aim1_funnel/  +  $WORK/run/genomeWide_compare.tsv"
echo "  retrieve them:  aws s3 cp --recursive $WORK/run/aim1_funnel s3://<your-bucket>/hmp_out/   (or scp)"
echo "  then TERMINATE the instance."
