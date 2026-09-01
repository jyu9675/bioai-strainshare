#!/usr/bin/env python3
"""
M5 — generalist-strain filter.

Shared environment/diet and reference-database bias inflate strain "sharing" between
UNRELATED people. A genome "shared" across many between-person pairs is a generalist or
artifact, not a transmission marker. We flag such genomes and down-rank any within-person
translocation candidate that rests on one — the confound the transmission literature warns
is the main false-positive source.

Inputs
------
--pairs        pairs_tagged.tsv from 05
--candidates   optional translocation_candidates.tsv to annotate + score
--config       optional strainshare_standard.yaml
--outdir       output directory

Outputs
-------
genome_generalist_flags.tsv          per-genome between-person shared rate + is_generalist
translocation_candidates_scored.tsv  (if --candidates) candidates + is_generalist + confidence
"""
import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strainshare_config import load_config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--candidates", default=None)
    ap.add_argument("--config", default=None)
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()

    cfg = load_config(a.config)
    cutoff = cfg["generalist_filter"]["between_shared_rate_max"]

    pairs = pd.read_csv(a.pairs, sep="\t")
    between = pairs[pairs.pair_class == "between_gut_vagina"]
    if len(between):
        g = (between.groupby("genome")["shared_strain"]
             .agg(["mean", "sum", "count"])
             .rename(columns={"mean": "between_shared_rate",
                              "sum": "n_between_shared",
                              "count": "n_between_pairs"}))
    else:
        g = pd.DataFrame(columns=["between_shared_rate", "n_between_shared", "n_between_pairs"])
    g["is_generalist"] = g["between_shared_rate"] > cutoff

    os.makedirs(a.outdir, exist_ok=True)
    g.sort_values("between_shared_rate", ascending=False).to_csv(
        f"{a.outdir}/genome_generalist_flags.tsv", sep="\t")
    print(f"[09 generalist] {int(g['is_generalist'].sum())} genome(s) flagged generalist "
          f"(between-share > {cutoff})")

    if a.candidates:
        cand = pd.read_csv(a.candidates, sep="\t")
        flag = g["is_generalist"].to_dict() if len(g) else {}
        cand["is_generalist"] = cand["genome"].map(lambda x: bool(flag.get(x, False)))

        def confidence(r):
            verdict = r.get("verdict", "translocation_candidate")
            if r["is_generalist"]:
                return "low_generalist"
            return "high" if verdict == "translocation_candidate" else "medium"

        cand["confidence"] = cand.apply(confidence, axis=1)
        cand.to_csv(f"{a.outdir}/translocation_candidates_scored.tsv", sep="\t", index=False)
        print(f"Wrote {a.outdir}/translocation_candidates_scored.tsv")
    print(f"Wrote {a.outdir}/genome_generalist_flags.tsv")


if __name__ == "__main__":
    main()
