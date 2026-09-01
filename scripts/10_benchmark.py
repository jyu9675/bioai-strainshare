#!/usr/bin/env python3
"""
Coverage-sweep benchmark for shared-strain calls  ->  Study D, Figure 3.

Maps the sensitivity/specificity of shared-strain detection as a function of sequencing
coverage, and locates the inStrain -> StrainGE crossover. Answers the reviewer question:
"at what depth does a low-biomass vaginal sample stop yielding a trustworthy strain call,
and where does the StrainGE fallback (M3) earn its place?"

Two backends
------------
--mode model  (default; runs anywhere, incl. Windows)
    A principled MODEL, not real reads. It encodes the documented relationships:
      * breadth(coverage): b(c) = 1 - exp(-ln2 * c)  -> anchored to inStrain's own numbers
        (~50% breadth at ~1x, ~98% at 6x). A comparison is evaluable only if breadth >= 0.5.
      * popANI estimation from a finite number of compared positions: with n_pos positions,
        discordances ~ Binomial(n_pos, 1 - true_popANI), so est_popANI = 1 - disc/n_pos.
        At low n_pos this is noisy and can read popANI = 1.0 on a handful of bases -- exactly
        the "popANI=1.0 on 28-82 bases = artifact" failure seen in the pilot's own low-depth run.
      * StrainGE: evaluable down to ~0.5x coverage (the verified low-coverage bound; the 0.1x
        claim did NOT survive verification), at the cost of noisier ANI (assembly-step penalty).
    Use for method development and the illustrative figure. It is deterministic given --seed.

--mode reads  (SCAFFOLD; Unix + refs, run on the cluster for the FINAL figure)
    Simulate reads at each coverage from known same/different reference strains, map, run the
    real inStrain profile/compare + StrainGE, and feed the actual calls through the same metrics.
    Prints the intended step list and exits until wired to a read simulator + reference set.

Usage
-----
  python scripts/10_benchmark.py --outdir results/benchmark
  python scripts/10_benchmark.py --selftest         # runs model + asserts expected shape
  python scripts/10_benchmark.py --mode reads       # prints the real-read recipe

Outputs (model mode)
--------------------
  benchmark_sweep.tsv              per coverage x method: sensitivity, specificity, precision, no-call rate
  fig3_coverage_sweep.png          the figure
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strainshare_config import load_config

LN2 = np.log(2.0)
GENOME_LEN = 2_000_000          # positions available at full breadth (order-of-magnitude)
DEFAULT_COVERAGES = [0.1, 0.25, 0.5, 1, 2, 4, 6, 10, 20, 30]
SG_EFFICIENCY = 0.5             # StrainGE effective-positions penalty (assembly step on low biomass)


def breadth(coverage, rng, n):
    """Expected genome breadth at a coverage, with mild per-sample noise. Anchored to
    inStrain: ~50% at 1x, ~98% at 6x."""
    b = 1.0 - np.exp(-LN2 * coverage)
    b = b + rng.normal(0, 0.03, n)
    return np.clip(b, 0.0, 1.0)


def estimate_popani(true_popani, n_pos, rng):
    """Estimate popANI from n_pos compared positions: disc ~ Binomial(n_pos, 1-true)."""
    n_pos = np.maximum(n_pos.astype(np.int64), 1)
    disc = rng.binomial(n_pos, np.clip(1.0 - true_popani, 0, 1))
    return 1.0 - disc / n_pos


def sweep(coverages, n_pairs, cfg, seed):
    rng = np.random.default_rng(seed)
    popani_thr = cfg["shared_strain"]["popani_primary"]
    breadth_min = cfg["shared_strain"]["breadth_min"]
    sg_cov_min = cfg["low_biomass"]["strainge_fallback_coverage_min"]

    # ground truth: half identical (same strain), half a distinct strain (~0.3% divergence)
    n_same = n_pairs // 2
    n_diff = n_pairs - n_same
    true_same = np.clip(rng.normal(0.999995, 0.000003, n_same), 0, 1.0)
    true_diff = np.clip(rng.normal(0.997, 0.001, n_diff), 0, 1.0)
    true_popani = np.concatenate([true_same, true_diff])
    is_same = np.concatenate([np.ones(n_same, bool), np.zeros(n_diff, bool)])

    rows = []
    for c in coverages:
        b = breadth(c, rng, n_pairs)
        n_pos = (b * GENOME_LEN)

        # --- inStrain: evaluable only if breadth >= breadth_min ---
        eval_is = b >= breadth_min
        est_is = estimate_popani(true_popani, n_pos, rng)
        call_is = eval_is & (est_is >= popani_thr)

        # --- StrainGE: evaluable down to sg_cov_min, noisier (fewer effective positions) ---
        eval_sg = np.full(n_pairs, c >= sg_cov_min)
        est_sg = estimate_popani(true_popani, n_pos * SG_EFFICIENCY, rng)
        call_sg = eval_sg & (est_sg >= popani_thr)

        for method, called, evaluable in [("inStrain", call_is, eval_is),
                                          ("StrainGE", call_sg, eval_sg)]:
            tp = int((called & is_same).sum())
            fp = int((called & ~is_same).sum())
            fn = int((~called & is_same).sum())       # missed (wrong call OR no-call)
            tn = int((~called & ~is_same).sum())
            sens = tp / max(tp + fn, 1)
            spec = tn / max(tn + fp, 1)
            prec = tp / max(tp + fp, 1)
            nocall = float((~evaluable).mean())
            rows.append(dict(coverage=c, method=method, sensitivity=sens, specificity=spec,
                             precision=prec, no_call_rate=nocall, tp=tp, fp=fp, fn=fn, tn=tn))
    return pd.DataFrame(rows)


def plot(df, outdir, breadth_min, sg_cov_min):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

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
    ax.axvline(1.0, color="grey", ls="--", lw=1)
    ax.text(1.02, 0.02, "inStrain breadth floor (~1x -> 50%)", fontsize=7, color="grey", rotation=90, va="bottom")
    ax.axvline(sg_cov_min, color="#c0563b", ls="--", lw=1, alpha=0.6)
    ax.set_title("Fig 3 — shared-strain calls vs coverage (model)\n"
                 "StrainGE rescues sensitivity below the inStrain breadth floor", fontsize=11)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    path = f"{outdir}/fig3_coverage_sweep.png"
    fig.savefig(path, dpi=150)
    return path


def reads_scaffold():
    print("[10 benchmark] --mode reads is a SCAFFOLD (Unix + reference strains). Intended steps:")
    print("""
  1. pick a same-strain pair and a different-strain pair of reference genomes per target species
     (e.g. two L. crispatus assemblies for 'same', a diverged one for 'different')
  2. for each coverage in the grid: simulate paired reads at that depth
        wgsim / ART / InSilicoSeq  ->  <sp>_<cov>x_{1,2}.fq.gz
  3. map + profile + compare with the REAL pipeline (scripts 03/04) and StrainGE (03b)
  4. apply the strainshare standard thresholds to the real calls
  5. compute the SAME metrics as model mode -> benchmark_sweep.tsv, fig3_coverage_sweep.png
  This replaces the model's assumptions with empirical read behavior for the final figure.
""")


def run_model(a, cfg):
    coverages = [float(x) for x in a.coverages.split(",")] if a.coverages else DEFAULT_COVERAGES
    df = sweep(coverages, a.n_pairs, cfg, a.seed)
    os.makedirs(a.outdir, exist_ok=True)
    df.to_csv(f"{a.outdir}/benchmark_sweep.tsv", sep="\t", index=False)
    p = plot(df, a.outdir, cfg["shared_strain"]["breadth_min"],
             cfg["low_biomass"]["strainge_fallback_coverage_min"])
    print(f"[10 benchmark] model sweep over {coverages}")
    print(f"  wrote {a.outdir}/benchmark_sweep.tsv")
    print(f"  wrote {p}")
    return df


def selftest(cfg):
    df = sweep(DEFAULT_COVERAGES, 4000, cfg, seed=0)
    def val(method, metric, cov):
        return df[(df.method == method) & (df.coverage == cov)][metric].iloc[0]
    # sensitivity climbs with coverage
    assert val("inStrain", "sensitivity", 30) > val("inStrain", "sensitivity", 0.5) + 0.2, \
        "inStrain sensitivity should rise strongly with coverage"
    # high-coverage calls are clean
    assert val("inStrain", "specificity", 30) > 0.95, "inStrain specificity should be high at 30x"
    assert val("inStrain", "sensitivity", 30) > 0.95, "inStrain sensitivity should be high at 30x"
    # StrainGE rescues sensitivity below the inStrain breadth floor
    assert val("StrainGE", "sensitivity", 0.5) > val("inStrain", "sensitivity", 0.5), \
        "StrainGE should out-sensitize inStrain at 0.5x (the crossover)"
    print("[10 benchmark] SELFTEST PASSED:")
    print(f"  inStrain sens 0.5x={val('inStrain','sensitivity',0.5):.2f} -> 30x={val('inStrain','sensitivity',30):.2f}")
    print(f"  inStrain spec 30x={val('inStrain','specificity',30):.2f}")
    print(f"  StrainGE sens 0.5x={val('StrainGE','sensitivity',0.5):.2f} (> inStrain: crossover confirmed)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["model", "reads"], default="model")
    ap.add_argument("--coverages", default=None, help="comma list, e.g. 0.1,0.5,1,6,30")
    ap.add_argument("--n-pairs", type=int, default=4000, dest="n_pairs")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--config", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                      "strainshare_standard.yaml"))
    ap.add_argument("--outdir", default="results/benchmark")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    cfg = load_config(a.config if os.path.exists(a.config) else None)

    if a.selftest:
        selftest(cfg)
        return
    if a.mode == "reads":
        reads_scaffold()
        return
    run_model(a, cfg)


if __name__ == "__main__":
    main()
