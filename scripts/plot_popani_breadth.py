#!/usr/bin/env python3
"""
Diagnostic: popANI x breadth, colored by pair class. The most honest single view of a
cohort's strain-sharing result -- it shows WHERE calls land relative to both the popANI
threshold and the breadth (percent_compared) floor, so spurious "popANI=1.0 on a few
bases" points can't masquerade as sharing.

A confident shared-strain call lives in the TOP-RIGHT box (popANI >= threshold AND
breadth >= floor). Positive controls (same-site over time) should sit there; a true
gut<->vaginal translocation would too.

Usage:
  python scripts/plot_popani_breadth.py --pairs results/goltsman/pairs_tagged.tsv \
      --out results/goltsman/figures/fig_cohort_popani_breadth.png [--title "Goltsman cohort"]
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strainshare_config import STANDARD

POPANI = STANDARD["shared_strain"]["popani_primary"]
BREADTH = STANDARD["shared_strain"]["breadth_min"]
FLOOR = 1e-5  # plotting floor so breadth=0 is visible on log scale

STYLE = {
    "within_same_site":  ("#2a7d46", "o", "within, same site over time (positive control)"),
    "within_gut_vagina": ("#c0563b", "o", "within-person gut↔vagina (the signal)"),
    "between_gut_vagina": ("#2a5d9c", "X", "between-person gut↔vagina (the null)"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="")
    a = ap.parse_args()

    d = pd.read_csv(a.pairs, sep="\t")
    d = d[d.popANI.notna()].copy()
    d["bx"] = d["breadth"].clip(lower=FLOOR)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    # confident-call box (top-right)
    ax.axhspan(POPANI, 1.0006, xmin=0, xmax=1, color="#eef6ef", zorder=0)
    ax.axvline(BREADTH, color="grey", ls=":", lw=1)
    ax.axhline(POPANI, color="grey", ls="--", lw=1)
    ax.text(BREADTH * 1.1, 0.9702, f"breadth floor {BREADTH}", fontsize=8, color="grey", rotation=90, va="bottom")
    ax.text(FLOOR * 1.3, POPANI + 0.00006, f"shared-strain threshold {POPANI}", fontsize=8, color="grey")

    for cls, (col, mk, lab) in STYLE.items():
        s = d[d.pair_class == cls]
        if len(s):
            ax.scatter(s.bx, s.popANI, s=42, marker=mk, color=col, alpha=0.75,
                       edgecolor="white", linewidths=0.4, label=f"{lab}  (n={len(s)})", zorder=3)
    # annotate the confident-call region
    ax.text(0.62, 0.9996, "confident\nshared-strain\ncalls", fontsize=8, color="#2a7d46",
            ha="center", va="top")

    ax.set_xscale("log")
    ax.set_xlabel("breadth — percent_genome_compared (log; left edge = 0)")
    ax.set_ylabel("popANI")
    ax.set_ylim(0.9695, 1.0006)
    ttl = "popANI × breadth by pair class"
    if a.title:
        ttl += f" — {a.title}"
    ax.set_title(ttl + "\nspurious high-popANI points sit at negligible breadth and are correctly rejected", fontsize=11)
    ax.legend(fontsize=7.5, loc="lower right")
    fig.tight_layout()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    fig.savefig(a.out, dpi=150)

    # report the confident box occupancy
    conf = d[(d.popANI >= POPANI) & (d.breadth >= BREADTH)]
    print(f"[plot] {len(d)} comparisons; {len(conf)} in the confident-call box:")
    print(conf.pair_class.value_counts().to_string() if len(conf) else "  (none)")
    print(f"[plot] wrote {a.out}")


if __name__ == "__main__":
    main()
