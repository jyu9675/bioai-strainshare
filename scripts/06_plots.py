#!/usr/bin/env python3
"""
Figures 1-3 from the tagged pairs produced by 05_shared_strain_analysis.py.

Fig 1  within- vs between-person popANI per species (is the signal real?)
Fig 2  popANI x community-similarity plane: translocation vs contamination quadrants
Fig 3  directionality timeline for surviving shared strains (gut-first vs vagina-first)

Usage:
  python 06_plots.py --pairs ../results/pairs_tagged.tsv --meta ../data/metadata.tsv \
                     --candidates ../results/translocation_candidates.tsv --outdir ../results/figures
"""
import argparse, os, sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strainshare_config import STANDARD

POPANI_THRESH = STANDARD["shared_strain"]["popani_primary"]
BC_SIMILAR = STANDARD["contamination"]["bray_curtis_similar_max"]


def fig1(pairs, outdir):
    sig = pairs[pairs.pair_class.isin(["within_gut_vagina", "between_gut_vagina"])].copy()
    sig = sig[sig.popANI.notna()]
    species = [s for s in sig.genome.unique()]
    fig, ax = plt.subplots(figsize=(max(6, len(species) * 1.2), 5))
    for i, sp in enumerate(species):
        for cls, dx, col in [("within_gut_vagina", -0.15, "#d1495b"),
                             ("between_gut_vagina", 0.15, "#4c9eb0")]:
            y = sig[(sig.genome == sp) & (sig.pair_class == cls)].popANI.values
            if len(y):
                ax.scatter(np.full(len(y), i + dx) + np.random.uniform(-0.05, 0.05, len(y)),
                           y, s=14, alpha=0.6, color=col,
                           label=cls if i == 0 else None)
    ax.axhline(POPANI_THRESH, ls="--", color="grey", lw=1)
    ax.set_xticks(range(len(species)))
    ax.set_xticklabels([s.split("/")[-1][:20] for s in species], rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("popANI"); ax.set_title("Fig 1 — within (red) vs between (blue) person, gut↔vagina")
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout(); fig.savefig(f"{outdir}/fig1_within_vs_between.png", dpi=150)


def fig2(pairs, outdir):
    gv = pairs[pairs.pair_class == "within_gut_vagina"].copy()
    gv = gv[gv.popANI.notna() & gv.bray_curtis.notna()]
    fig, ax = plt.subplots(figsize=(6, 5))
    sh = gv[gv.shared_strain]; nsh = gv[~gv.shared_strain]
    ax.scatter(nsh.bray_curtis, nsh.popANI, s=16, color="#cccccc", label="not shared")
    # among shared: dissimilar community (high BC) = translocation; similar = contamination
    tr = sh[sh.bray_curtis >= BC_SIMILAR]; ct = sh[sh.bray_curtis < BC_SIMILAR]
    ax.scatter(ct.bray_curtis, ct.popANI, s=36, color="#e07b39", label="contamination suspect")
    ax.scatter(tr.bray_curtis, tr.popANI, s=36, color="#2a9d3f", label="translocation candidate")
    ax.axhline(POPANI_THRESH, ls="--", color="grey", lw=1)
    ax.axvline(BC_SIMILAR, ls=":", color="grey", lw=1)
    ax.set_xlabel("Bray–Curtis community distance (shared species)")
    ax.set_ylabel("popANI"); ax.set_title("Fig 2 — shared strain × community similarity")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout(); fig.savefig(f"{outdir}/fig2_translocation_vs_contamination.png", dpi=150)


def fig3(cand, meta, outdir):
    """First-appearance timepoint of the shared strain in gut vs vagina, per surviving event."""
    tr = cand[cand.verdict == "translocation_candidate"].copy()
    if tr.empty:
        print("Fig 3 skipped: no translocation candidates."); return
    meta = meta.set_index("sample")
    fig, ax = plt.subplots(figsize=(7, max(3, 0.5 * len(tr))))
    for i, (_, r) in enumerate(tr.iterrows()):
        t1, t2 = meta.loc[r.s1].timepoint, meta.loc[r.s2].timepoint
        site1, site2 = meta.loc[r.s1].bodysite, meta.loc[r.s2].bodysite
        ax.plot([t1, t2], [i, i], color="#888", lw=1, zorder=1)
        for t, site in [(t1, site1), (t2, site2)]:
            ax.scatter(t, i, s=60, zorder=2,
                       color="#d1495b" if site == "vagina" else "#4c9eb0")
        ax.text(-0.02, i, f"{r.subject1} · {r.genome.split('/')[-1][:16]}",
                ha="right", va="center", fontsize=7, transform=ax.get_yaxis_transform())
    ax.set_yticks([]); ax.set_xlabel("timepoint (gestational week)")
    ax.set_title("Fig 3 — gut (blue) vs vagina (red) first appearance per shared strain")
    fig.tight_layout(); fig.savefig(f"{outdir}/fig3_directionality.png", dpi=150)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--outdir", default="../results/figures")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    np.random.seed(0)  # jitter reproducibility
    pairs = pd.read_csv(a.pairs, sep="\t")
    cand = pd.read_csv(a.candidates, sep="\t")
    meta = pd.read_csv(a.meta, sep="\t")
    fig1(pairs, a.outdir); fig2(pairs, a.outdir); fig3(cand, meta, a.outdir)
    print(f"Figures written to {a.outdir}")


if __name__ == "__main__":
    main()
