"""M5 — generalist-strain filter.

A genome "shared" across many BETWEEN-person pairs is a generalist / DB artifact, not a
transmission marker. Flag those genomes and down-rank any within-person translocation
candidate that rests on one.
"""
import os

import pandas as pd

from .config import STANDARD


def run(pairs, cfg=None, candidates=None):
    """Return (flags_df, scored_df). scored_df is None if no candidates given."""
    cfg = cfg or STANDARD
    cutoff = cfg["generalist_filter"]["between_shared_rate_max"]

    between = pairs[pairs.pair_class == "between_gut_vagina"]
    if len(between):
        g = (between.groupby("genome")["shared_strain"]
             .agg(["mean", "sum", "count"])
             .rename(columns={"mean": "between_shared_rate", "sum": "n_between_shared",
                              "count": "n_between_pairs"}))
    else:
        g = pd.DataFrame(columns=["between_shared_rate", "n_between_shared", "n_between_pairs"])
    g["is_generalist"] = g["between_shared_rate"] > cutoff
    g = g.sort_values("between_shared_rate", ascending=False)

    scored = None
    if candidates is not None:
        scored = candidates.copy()
        flag = g["is_generalist"].to_dict() if len(g) else {}
        scored["is_generalist"] = scored["genome"].map(lambda x: bool(flag.get(x, False)))

        def confidence(r):
            verdict = r.get("verdict", "translocation_candidate")
            if r["is_generalist"]:
                return "low_generalist"
            return "high" if verdict == "translocation_candidate" else "medium"

        scored["confidence"] = scored.apply(confidence, axis=1)
    return g, scored


def run_files(pairs_path, outdir, cfg=None, candidates_path=None):
    pairs = pd.read_csv(pairs_path, sep="\t")
    candidates = pd.read_csv(candidates_path, sep="\t") if candidates_path else None
    g, scored = run(pairs, cfg, candidates)
    os.makedirs(outdir, exist_ok=True)
    g.to_csv(f"{outdir}/genome_generalist_flags.tsv", sep="\t")
    if scored is not None:
        scored.to_csv(f"{outdir}/translocation_candidates_scored.tsv", sep="\t", index=False)
    return g, scored
