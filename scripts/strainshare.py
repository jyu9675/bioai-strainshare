#!/usr/bin/env python3
"""
strainshare — unified, config-driven runner for the ANALYSIS half of the pipeline.

Cross-platform (runs on Windows). Takes the small tables you produced on the cluster
(steps 01-04, 07) and chains:

    05 shared-strain analysis  ->  09 generalist filter  ->  08 direction  ->  06 figures

All thresholds come from scripts/strainshare_standard.yaml (or the built-in STANDARD if
that file or pyyaml is absent), so every run is comparable.

Usage
-----
  python scripts/strainshare.py \
      --compare   results/compare.IS/output/genomeWide_compare.tsv \
      --meta      data/metadata.tsv \
      --metaphlan results/metaphlan/merged_metaphlan.tsv \
      --outdir    results
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    print("> " + " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--metaphlan", required=True)
    ap.add_argument("--config", default=os.path.join(HERE, "strainshare_standard.yaml"))
    ap.add_argument("--outdir", default="results")
    a = ap.parse_args()

    py = sys.executable
    cfg = a.config if os.path.exists(a.config) else None
    cfg_args = ["--config", cfg] if cfg else []
    os.makedirs(a.outdir, exist_ok=True)

    run([py, f"{HERE}/05_shared_strain_analysis.py", "--compare", a.compare,
         "--meta", a.meta, "--metaphlan", a.metaphlan, "--outdir", a.outdir])
    run([py, f"{HERE}/09_generalist_filter.py",
         "--pairs", f"{a.outdir}/pairs_tagged.tsv",
         "--candidates", f"{a.outdir}/translocation_candidates.tsv",
         "--outdir", a.outdir] + cfg_args)
    run([py, f"{HERE}/08_direction.py",
         "--candidates", f"{a.outdir}/translocation_candidates.tsv",
         "--pairs", f"{a.outdir}/pairs_tagged.tsv",
         "--meta", a.meta, "--outdir", a.outdir] + cfg_args)
    run([py, f"{HERE}/06_plots.py",
         "--pairs", f"{a.outdir}/pairs_tagged.tsv",
         "--candidates", f"{a.outdir}/translocation_candidates.tsv",
         "--meta", a.meta, "--outdir", f"{a.outdir}/figures"])

    print(f"\n[strainshare] done -> {a.outdir}")
    print("  tables:  pairs_tagged, species_within_between, translocation_candidates(_scored),")
    print("           genome_generalist_flags, direction_calls")
    print("  figures: figures/fig1..3.png")


if __name__ == "__main__":
    main()
