"""Figures: within/between null, translocation-vs-contamination plane, directionality
timeline, and the popANI x breadth diagnostic."""
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import STANDARD

POPANI = STANDARD["shared_strain"]["popani_primary"]
BC_SIMILAR = STANDARD["contamination"]["bray_curtis_similar_max"]
BREADTH_MIN = STANDARD["shared_strain"]["breadth_min"]


def fig1(pairs, outdir):
    sig = pairs[pairs.pair_class.isin(["within_gut_vagina", "between_gut_vagina"])].copy()
    sig = sig[sig.popANI.notna()]
    species = list(sig.genome.unique())
    fig, ax = plt.subplots(figsize=(max(6, len(species) * 1.2), 5))
    for i, sp in enumerate(species):
        for cls, dx, col in [("within_gut_vagina", -0.15, "#d1495b"),
                             ("between_gut_vagina", 0.15, "#4c9eb0")]:
            y = sig[(sig.genome == sp) & (sig.pair_class == cls)].popANI.values
            if len(y):
                ax.scatter(np.full(len(y), i + dx) + np.random.uniform(-0.05, 0.05, len(y)),
                           y, s=14, alpha=0.6, color=col, label=cls if i == 0 else None)
    ax.axhline(POPANI, ls="--", color="grey", lw=1)
    ax.set_xticks(range(len(species)))
    ax.set_xticklabels([s.split("/")[-1][:20] for s in species], rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("popANI")
    ax.set_title("Fig 1 — within (red) vs between (blue) person, gut↔vagina")
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(f"{outdir}/fig1_within_vs_between.png", dpi=150)
    plt.close(fig)


def fig2(pairs, outdir):
    gv = pairs[pairs.pair_class == "within_gut_vagina"].copy()
    gv = gv[gv.popANI.notna() & gv.bray_curtis.notna()]
    fig, ax = plt.subplots(figsize=(6, 5))
    sh = gv[gv.shared_strain]
    nsh = gv[~gv.shared_strain]
    ax.scatter(nsh.bray_curtis, nsh.popANI, s=16, color="#cccccc", label="not shared")
    tr = sh[sh.bray_curtis >= BC_SIMILAR]
    ct = sh[sh.bray_curtis < BC_SIMILAR]
    ax.scatter(ct.bray_curtis, ct.popANI, s=36, color="#e07b39", label="contamination suspect")
    ax.scatter(tr.bray_curtis, tr.popANI, s=36, color="#2a9d3f", label="translocation candidate")
    ax.axhline(POPANI, ls="--", color="grey", lw=1)
    ax.axvline(BC_SIMILAR, ls=":", color="grey", lw=1)
    ax.set_xlabel("Bray–Curtis community distance (shared species)")
    ax.set_ylabel("popANI")
    ax.set_title("Fig 2 — shared strain × community similarity")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(f"{outdir}/fig2_translocation_vs_contamination.png", dpi=150)
    plt.close(fig)


def fig3(cand, meta, outdir):
    tr = cand[cand.verdict == "translocation_candidate"].copy() if "verdict" in cand.columns else cand.copy()
    if tr.empty:
        print("Fig 3 skipped: no translocation candidates.")
        return
    meta = meta.set_index("sample")
    fig, ax = plt.subplots(figsize=(7, max(3, 0.5 * len(tr))))
    for i, (_, r) in enumerate(tr.iterrows()):
        t1, t2 = meta.loc[r.s1].timepoint, meta.loc[r.s2].timepoint
        site1, site2 = meta.loc[r.s1].bodysite, meta.loc[r.s2].bodysite
        ax.plot([t1, t2], [i, i], color="#888", lw=1, zorder=1)
        for t, site in [(t1, site1), (t2, site2)]:
            ax.scatter(t, i, s=60, zorder=2, color="#d1495b" if site == "vagina" else "#4c9eb0")
        ax.text(-0.02, i, f"{r.subject1} · {r.genome.split('/')[-1][:16]}",
                ha="right", va="center", fontsize=7, transform=ax.get_yaxis_transform())
    ax.set_yticks([])
    ax.set_xlabel("timepoint")
    ax.set_title("Fig 3 — gut (blue) vs vagina (red) first appearance per shared strain")
    fig.tight_layout()
    fig.savefig(f"{outdir}/fig3_directionality.png", dpi=150)
    plt.close(fig)


def all_figures(pairs, cand, meta, outdir, seed=0):
    os.makedirs(outdir, exist_ok=True)
    np.random.seed(seed)
    fig1(pairs, outdir)
    fig2(pairs, outdir)
    fig3(cand, meta, outdir)


# ---- popANI x breadth diagnostic (confident-call box) ----
_STYLE = {
    "within_same_site":  ("#2a7d46", "o", "within, same site over time (positive control)"),
    "within_gut_vagina": ("#c0563b", "o", "within-person gut↔vagina (the signal)"),
    "between_gut_vagina": ("#2a5d9c", "X", "between-person gut↔vagina (the null)"),
}
_FLOOR = 1e-5


def popani_breadth(pairs, out, title=""):
    d = pairs[pairs.popANI.notna()].copy()
    d["bx"] = d["breadth"].clip(lower=_FLOOR)
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.axhspan(POPANI, 1.0006, color="#eef6ef", zorder=0)
    ax.axvline(BREADTH_MIN, color="grey", ls=":", lw=1)
    ax.axhline(POPANI, color="grey", ls="--", lw=1)
    ax.text(BREADTH_MIN * 1.1, 0.9702, f"breadth floor {BREADTH_MIN}", fontsize=8, color="grey", rotation=90, va="bottom")
    ax.text(_FLOOR * 1.3, POPANI + 0.00006, f"shared-strain threshold {POPANI}", fontsize=8, color="grey")
    for cls, (col, mk, lab) in _STYLE.items():
        s = d[d.pair_class == cls]
        if len(s):
            ax.scatter(s.bx, s.popANI, s=42, marker=mk, color=col, alpha=0.75,
                       edgecolor="white", linewidths=0.4, label=f"{lab}  (n={len(s)})", zorder=3)
    ax.text(0.62, 0.9996, "confident\nshared-strain\ncalls", fontsize=8, color="#2a7d46", ha="center", va="top")
    ax.set_xscale("log")
    ax.set_xlabel("breadth — percent_genome_compared (log; left edge = 0)")
    ax.set_ylabel("popANI")
    ax.set_ylim(0.9695, 1.0006)
    ttl = "popANI × breadth by pair class"
    if title:
        ttl += f" — {title}"
    ax.set_title(ttl + "\nspurious high-popANI points sit at negligible breadth and are correctly rejected", fontsize=11)
    ax.legend(fontsize=7.5, loc="lower right")
    fig.tight_layout()
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    conf = d[(d.popANI >= POPANI) & (d.breadth >= BREADTH_MIN)]
    return conf
