#!/usr/bin/env python3
"""
Study D figure: why the breadth floor is load-bearing.

Plots popANI against percent_compared for BETWEEN-PERSON comparisons -- pairs that are
known a priori to be unrelated, so anything landing above the popANI threshold is either
a genuine community-acquired strain or an artifact of comparing almost none of the genome.

The figure's point: a large fraction of between-person rows reach popANI >= 0.999 while
comparing <5% of the genome. Reporting popANI without the breadth floor turns those into
false "shared strain" calls.

Usage:
  python scripts/plot_breadth_floor.py \
      --inputs example/fijian/goltsman_pvulgatus_between.tsv:"Goltsman (US) gut" \
               example/fijian/genomeWide_compare.tsv:"Fijian same-site" \
      --out example/figures/fig_breadth_floor.png
"""
import argparse, os, sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
try:
    from strainshare_config import STANDARD
    POPANI = STANDARD["shared_strain"]["popani_primary"]
    BREADTH = STANDARD["shared_strain"]["breadth_min"]
except Exception:
    POPANI, BREADTH = 0.999, 0.5

FLOOR = 1e-4
PALETTE = ["#2a5d9c", "#c0563b", "#2a7d46", "#9c7420"]


def pc_col(d):
    return "percent_compared" if "percent_compared" in d.columns else "percent_genome_compared"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True,
                    help='each as path:label')
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="Between-person comparisons: popANI is not enough")
    a = ap.parse_args()

    sets = []
    for spec in a.inputs:
        path, _, label = spec.partition(":")
        d = pd.read_csv(path, sep="\t")
        c = pc_col(d)
        d = d[["genome", "popANI", c]].rename(columns={c: "pc"})
        d["label"] = label or os.path.basename(path)
        sets.append(d)
    df = pd.concat(sets, ignore_index=True)
    # popANI == 0 means inStrain emitted a row but compared nothing usable -- these are
    # "not compared", not "completely divergent". Excluding them keeps the denominator
    # honest: the artifact rate is a fraction of comparisons that actually produced a value.
    n_nocmp = int((df.popANI <= 0).sum())
    df = df[df.popANI > 0].copy()
    df["pc_plot"] = df.pc.clip(lower=FLOOR)

    fig, ax = plt.subplots(figsize=(8.4, 5.6))

    # artifact zone: above the popANI line but below the breadth floor
    ax.axhspan(POPANI, 1.0005, xmin=0, xmax=1, color="#c0563b", alpha=0.05, zorder=0)
    ax.add_patch(plt.Rectangle((FLOOR, POPANI), BREADTH - FLOOR, 1.0005 - POPANI,
                               facecolor="#c0563b", alpha=0.13, edgecolor="none", zorder=1))
    ax.add_patch(plt.Rectangle((BREADTH, POPANI), 1.02 - BREADTH, 1.0005 - POPANI,
                               facecolor="#2a7d46", alpha=0.13, edgecolor="none", zorder=1))

    ax.axhline(POPANI, color="#333", lw=1.1, ls="--", zorder=3)
    ax.axvline(BREADTH, color="#333", lw=1.1, ls="--", zorder=3)

    for i, (label, grp) in enumerate(df.groupby("label", sort=False)):
        ax.scatter(grp.pc_plot, grp.popANI, s=46, alpha=0.85,
                   color=PALETTE[i % len(PALETTE)], edgecolor="white", lw=0.7,
                   label=f"{label}  (n={len(grp)})", zorder=4)

    n_art = int(((df.popANI >= POPANI) & (df.pc < BREADTH)).sum())
    n_ok = int(((df.popANI >= POPANI) & (df.pc >= BREADTH)).sum())
    tot = len(df)

    ax.set_xscale("log")
    ax.set_xlim(FLOOR * 0.7, 1.25)
    ax.set_ylim(min(0.973, df.popANI[df.popANI > 0].min() - 0.002), 1.0006)
    ax.set_xlabel("fraction of genome compared  (percent_compared, log scale)")
    ax.set_ylabel("popANI")
    ax.set_title(a.title, fontsize=12.5, pad=12)

    ax.annotate(f"BREADTH ARTIFACTS — {n_art}/{tot} rows ({100*n_art/tot:.0f}%)\n"
                f"popANI ≥ {POPANI} reached on <{BREADTH:.0%} of the genome.\n"
                f"Reported without the floor, every one is a false\n"
                f"“shared strain” between people who share nothing.",
                xy=(0.02, 0.88), xycoords="axes fraction", fontsize=8.8,
                color="#8c3a22", va="top", ha="left",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                          edgecolor="#c0563b", alpha=0.9, lw=0.9))
    ax.annotate(f"confident\nshared strain\n{n_ok}/{tot}",
                xy=(0.985, 0.03), xycoords="axes fraction", fontsize=8.8,
                color="#1d5c32", va="bottom", ha="right",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                          edgecolor="#2a7d46", alpha=0.9, lw=0.9))
    ax.annotate(f"popANI ≥ {POPANI}  (same-strain threshold)", xy=(0.22, POPANI),
                fontsize=8, color="#333", va="top", ha="center")
    ax.annotate(f"breadth floor  {BREADTH:.0%} →", xy=(BREADTH * 0.94, 0.5),
                xycoords=("data", "axes fraction"), fontsize=8, color="#333",
                va="center", ha="right")
    if n_nocmp:
        ax.annotate(f"({n_nocmp} further rows compared nothing at all and are excluded)",
                    xy=(0.5, -0.155), xycoords="axes fraction", fontsize=7.6,
                    color="#666", ha="center")

    ax.legend(loc="lower left", frameon=True, fontsize=8.6)
    ax.grid(alpha=0.16, zorder=0)
    fig.tight_layout()
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    fig.savefig(a.out, dpi=190)
    print(f"wrote {a.out}")
    print(f"  rows={tot}  breadth-artifacts={n_art}  confident-shared={n_ok}")


if __name__ == "__main__":
    main()
