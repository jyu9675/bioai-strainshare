"""Coverage-sweep + precision-edge benchmarks for shared-strain calls.

- ``model``: a principled coverage->breadth + finite-position popANI model (runs anywhere).
- ``summarize_reads`` / ``precision_edge``: ingest real-read results from the shell drivers
  (10b/10c) and produce the empirical validation figures.
The real-read drivers themselves live in ``scripts/`` (they need the Unix bioinformatics stack).
"""
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import STANDARD

GENOME_LEN = 2_000_000
DEFAULT_COVERAGES = [0.1, 0.25, 0.5, 1, 2, 4, 6, 10, 20, 30]
SG_EFFICIENCY = 0.5


def breadth(coverage, rng, n):
    """Expected COMPARISON breadth (percent_compared) at a coverage, calibrated to the
    reads-mode run: ~0.30 @5x, ~0.92 @10x; the 0.5 floor is reached around ~6-7x."""
    c = max(float(coverage), 1e-6)
    b = 1.0 / (1.0 + np.exp(-3.0 * (np.log(c) - np.log(6.0))))
    return np.clip(b + rng.normal(0, 0.03, n), 0.0, 1.0)


def estimate_popani(true_popani, n_pos, rng):
    n_pos = np.maximum(n_pos.astype(np.int64), 1)
    disc = rng.binomial(n_pos, np.clip(1.0 - true_popani, 0, 1))
    return 1.0 - disc / n_pos


def sweep(coverages, n_pairs, cfg, seed):
    rng = np.random.default_rng(seed)
    popani_thr = cfg["shared_strain"]["popani_primary"]
    breadth_min = cfg["shared_strain"]["breadth_min"]
    sg_cov_min = cfg["low_biomass"]["strainge_fallback_coverage_min"]

    n_same = n_pairs // 2
    n_diff = n_pairs - n_same
    true_same = np.clip(rng.normal(0.999995, 0.000003, n_same), 0, 1.0)
    true_diff = np.clip(rng.normal(0.997, 0.001, n_diff), 0, 1.0)
    true_popani = np.concatenate([true_same, true_diff])
    is_same = np.concatenate([np.ones(n_same, bool), np.zeros(n_diff, bool)])

    rows = []
    for c in coverages:
        b = breadth(c, rng, n_pairs)
        n_pos = b * GENOME_LEN
        eval_is = b >= breadth_min
        est_is = estimate_popani(true_popani, n_pos, rng)
        call_is = eval_is & (est_is >= popani_thr)
        eval_sg = np.full(n_pairs, c >= sg_cov_min)
        est_sg = estimate_popani(true_popani, n_pos * SG_EFFICIENCY, rng)
        call_sg = eval_sg & (est_sg >= popani_thr)
        for method, called, evaluable in [("inStrain", call_is, eval_is), ("StrainGE", call_sg, eval_sg)]:
            tp = int((called & is_same).sum()); fp = int((called & ~is_same).sum())
            fn = int((~called & is_same).sum()); tn = int((~called & ~is_same).sum())
            rows.append(dict(coverage=c, method=method,
                             sensitivity=tp / max(tp + fn, 1), specificity=tn / max(tn + fp, 1),
                             precision=tp / max(tp + fp, 1), no_call_rate=float((~evaluable).mean()),
                             tp=tp, fp=fp, fn=fn, tn=tn))
    return pd.DataFrame(rows)


def plot_sweep(df, outdir, sg_cov_min):
    fig, ax = plt.subplots(figsize=(7.5, 5))
    styles = {("inStrain", "sensitivity"): ("#2a5d9c", "-", "inStrain sensitivity"),
              ("inStrain", "specificity"): ("#2a5d9c", ":", "inStrain specificity"),
              ("StrainGE", "sensitivity"): ("#c0563b", "-", "StrainGE sensitivity"),
              ("StrainGE", "specificity"): ("#c0563b", ":", "StrainGE specificity")}
    for (method, metric), (col, ls, lab) in styles.items():
        d = df[df.method == method].sort_values("coverage")
        ax.plot(d.coverage, d[metric], ls, color=col, lw=2, marker="o", ms=4, label=lab)
    ax.set_xscale("log")
    ax.set_xlabel("coverage (x, log scale)")
    ax.set_ylabel("sensitivity / specificity")
    ax.set_ylim(-0.03, 1.03)
    ax.axvline(6.0, color="grey", ls="--", lw=1)
    ax.text(6.2, 0.02, "inStrain confidence floor (~6-7x, breadth->0.5)", fontsize=7, color="grey", rotation=90, va="bottom")
    ax.axvline(sg_cov_min, color="#c0563b", ls="--", lw=1, alpha=0.6)
    ax.set_title("Fig 3 — shared-strain calls vs coverage (model, calibrated to reads-mode)\n"
                 "StrainGE rescues sensitivity below the inStrain confidence floor", fontsize=11)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    p = f"{outdir}/fig3_coverage_sweep.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def run_model(outdir, cfg=None, coverages=None, n_pairs=4000, seed=0):
    cfg = cfg or STANDARD
    coverages = coverages or DEFAULT_COVERAGES
    df = sweep(coverages, n_pairs, cfg, seed)
    os.makedirs(outdir, exist_ok=True)
    df.to_csv(f"{outdir}/benchmark_sweep.tsv", sep="\t", index=False)
    plot_sweep(df, outdir, cfg["low_biomass"]["strainge_fallback_coverage_min"])
    return df


def selftest(cfg=None):
    cfg = cfg or STANDARD
    df = sweep(DEFAULT_COVERAGES, 4000, cfg, seed=0)

    def val(method, metric, cov):
        return df[(df.method == method) & (df.coverage == cov)][metric].iloc[0]

    assert val("inStrain", "sensitivity", 30) > val("inStrain", "sensitivity", 0.5) + 0.2
    assert val("inStrain", "specificity", 30) > 0.95
    assert val("inStrain", "sensitivity", 30) > 0.95
    assert val("StrainGE", "sensitivity", 0.5) > val("inStrain", "sensitivity", 0.5)
    return df


def summarize_reads(path, cfg, outdir):
    cfg = cfg or STANDARD
    popani_thr = cfg["shared_strain"]["popani_primary"]
    breadth_min = cfg["shared_strain"]["breadth_min"]
    d = pd.read_csv(path, sep="\t")
    d["popANI"] = pd.to_numeric(d["popANI"], errors="coerce")
    d["breadth"] = pd.to_numeric(d["percent_genome_compared"], errors="coerce")
    d["evaluable"] = d["breadth"] >= breadth_min
    d["called_shared"] = d["evaluable"] & (d["popANI"] >= popani_thr)
    d["correct"] = ((d.truth == "same") & d.called_shared) | ((d.truth == "diff") & ~d.called_shared)
    os.makedirs(outdir, exist_ok=True)
    d.to_csv(f"{outdir}/reads_summary.tsv", sep="\t", index=False)

    has = d[d.popANI.notna()]
    y_lo = min(0.9965, has.popANI.min() - 0.0005) if len(has) else 0.996
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.axhline(popani_thr, color="grey", ls="--", lw=1)
    ax.text(d.coverage.min(), popani_thr + 0.00004, f"shared-strain threshold  {popani_thr}", fontsize=8, color="grey")
    for truth, col, lab in [("same", "#2a7d46", "same strain (truth: shared)"),
                            ("diff", "#c0563b", "different strain (truth: not shared)")]:
        s = d[d.truth == truth]
        conf = s[s.evaluable & s.popANI.notna()]
        subbr = s[~s.evaluable & s.popANI.notna()]
        nocall = s[s.popANI.isna()]
        ax.scatter(conf.coverage, conf.popANI, s=90, color=col, zorder=3, edgecolor="white", label=f"{lab} — confident")
        ax.scatter(subbr.coverage, subbr.popANI, s=90, facecolors="none", edgecolors=col, linewidths=1.6, zorder=3, label=f"{lab} — sub-breadth")
        if len(nocall):
            ax.scatter(nocall.coverage, [y_lo + 0.0002] * len(nocall), s=80, color=col, marker="x", zorder=3, label=f"{lab} — no-call")
        for _, r in s.iterrows():
            if pd.notna(r.popANI):
                ax.annotate(f"br={r.breadth:.2f}", (r.coverage, r.popANI), fontsize=6.5, color=col, xytext=(5, -3), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_xlabel("coverage (x, log scale)")
    ax.set_ylabel("popANI (real inStrain)")
    ax.set_ylim(y_lo, 1.0006)
    ax.set_title("Fig 3 (reads) — empirical validation on real L. crispatus\n"
                 "same strain (popANI=1.0) vs 0.3%-diverged strain (~0.997), across coverage", fontsize=11)
    ax.legend(fontsize=7, loc="center right")
    fig.tight_layout()
    fig.savefig(f"{outdir}/fig3_reads_validation.png", dpi=150)
    plt.close(fig)
    return d


def precision_edge(path, cfg, outdir):
    cfg = cfg or STANDARD
    thr = cfg["shared_strain"]["popani_primary"]
    bmin = cfg["shared_strain"]["breadth_min"]
    d = pd.read_csv(path, sep="\t")
    d["popANI"] = pd.to_numeric(d["popANI"], errors="coerce")
    d["breadth"] = pd.to_numeric(d["percent_genome_compared"], errors="coerce")
    d["divergence"] = pd.to_numeric(d["divergence"], errors="coerce")
    d["evaluable"] = d["breadth"] >= bmin
    d["called_shared"] = d["evaluable"] & (d["popANI"] >= thr)
    diff = d[(d.truth == "diff") & d.popANI.notna()].copy()
    same = d[(d.truth == "same") & d.popANI.notna()].copy()
    g = (diff.groupby(["species", "divergence"])
         .agg(mean_popANI=("popANI", "mean"), sd_popANI=("popANI", "std"), n=("popANI", "size"),
              frac_called_shared=("called_shared", "mean")).reset_index())
    g["frac_flagged_different"] = 1 - g["frac_called_shared"]
    os.makedirs(outdir, exist_ok=True)
    g.to_csv(f"{outdir}/precision_edge_summary.tsv", sep="\t", index=False)

    colors = {"L_crispatus": "#2a7d46", "L_iners": "#2a5d9c", "G_vaginalis": "#9c5a2a"}
    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    xs = sorted(diff.divergence.unique())
    xx = [xs[0] * 0.5] + xs + [xs[-1] * 1.15]
    ax.plot([x * 100 for x in xx], [1 - x for x in xx], color="grey", ls=":", lw=1.2, label="expected: popANI = 1 − divergence")
    ax.axhline(thr, color="#c0392b", ls="--", lw=1.2)
    ax.text(xs[0] * 100 * 0.55, thr + 0.00004, f"shared-strain threshold {thr}", color="#c0392b", fontsize=8)
    for sp in sorted(g.species.unique()):
        raw = diff[diff.species == sp]
        gg = g[g.species == sp].sort_values("divergence")
        col = colors.get(sp, "#555")
        ax.scatter(raw.divergence * 100, raw.popANI, s=22, alpha=0.45, color=col, zorder=2)
        ax.plot(gg.divergence * 100, gg.mean_popANI, "-o", color=col, lw=1.8, zorder=3, label=sp)
    if len(same):
        ax.scatter([xs[0] * 100 * 0.5] * len(same), same.popANI, marker="*", s=90, color="black", zorder=4, label="same-strain control (popANI≈1.0)")
    ax.set_xscale("log")
    ax.set_xlabel("strain divergence (%)")
    ax.set_ylabel("popANI (real inStrain)")
    ax.set_title("Precision edge — popANI vs near-boundary divergence, by species\n"
                 "where a diverged strain drops below the 0.999 threshold", fontsize=11)
    ax.legend(fontsize=7.5, loc="lower left")
    fig.tight_layout()
    fig.savefig(f"{outdir}/fig_precision_edge.png", dpi=150)
    plt.close(fig)
    return g
