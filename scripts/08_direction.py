#!/usr/bin/env python3
"""
M4 — transmission DIRECTION inference for within-person gut<->vagina shared strains.

Direction is NEVER inferred from a sharing call alone. No strain-sharing method can do it
(inStrain, StrainPhlAn, StrainGE, TRACS all explicitly decline). We infer it ONLY from
longitudinal acquisition timing: for a shared strain, the site where it is detected EARLIER
is the putative source. Events without enough temporal spread — including any cross-sectional
cohort — are reported as 'direction_unresolved', not guessed.

Inputs
------
--candidates  translocation_candidates.tsv from 05 (within-person gut<->vagina shared strains)
--pairs       pairs_tagged.tsv from 05 (used to find every sample a genome is detected in)
--meta        metadata TSV: sample, subject, timepoint, bodysite
--config      optional strainshare_standard.yaml (else built-in STANDARD defaults)
--outdir      output directory

Output
------
direction_calls.tsv   one row per (subject, genome) shared event with a direction call

Limitation (stated up front): "detected in a sample" is proxied by that sample participating
in a >= breadth_min comparison for the genome. A per-sample presence table from the profiles
would be stricter; this proxy is transparent and errs toward 'unresolved'.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strainshare_config import load_config


def sample_sites_times(pairs, subject, genome, breadth_min, meta):
    """Every sample of `subject` in which `genome` is detected (breadth >= min), as (site, timepoint)."""
    sub = pairs[(pairs.genome == genome) & (pairs.breadth >= breadth_min)]
    samples = set()
    for _, r in sub.iterrows():
        for s, subj in [(r.s1, r.subject1), (r.s2, r.subject2)]:
            if subj == subject:
                samples.add(s)
    out = []
    for s in samples:
        if s in meta.index:
            out.append((meta.loc[s].bodysite, meta.loc[s].timepoint))
    return out


def call_direction(sites_times, min_timepoints):
    """Return (direction, earliest_gut_tp, earliest_vagina_tp, note)."""
    times = sorted({t for _, t in sites_times})
    if len(times) < min_timepoints:
        return "direction_unresolved", np.nan, np.nan, "insufficient timepoints (needs longitudinal)"
    gut = [t for site, t in sites_times if site == "gut"]
    vag = [t for site, t in sites_times if site == "vagina"]
    if not gut or not vag:
        return "direction_unresolved", np.nan, np.nan, "strain not detected at both sites"
    eg, ev = min(gut), min(vag)
    if eg < ev:
        return "gut_to_vagina", eg, ev, "gut precedes vagina"
    if ev < eg:
        return "vagina_to_gut", eg, ev, "vagina precedes gut"
    return "concurrent", eg, ev, "first detected at same timepoint"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--config", default=None)
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()

    cfg = load_config(a.config)
    breadth_min = cfg["shared_strain"]["breadth_min"]
    min_tp = cfg["direction"]["min_timepoints"]

    cand = pd.read_csv(a.candidates, sep="\t")
    pairs = pd.read_csv(a.pairs, sep="\t")
    meta = pd.read_csv(a.meta, sep="\t").set_index("sample")

    # only genuine translocation candidates carry a meaningful direction
    if "verdict" in cand.columns:
        cand = cand[cand.verdict == "translocation_candidate"]
    events = cand[["subject1", "genome"]].drop_duplicates().rename(columns={"subject1": "subject"})

    rows = []
    for _, e in events.iterrows():
        st = sample_sites_times(pairs, e.subject, e.genome, breadth_min, meta)
        direction, eg, ev_t, note = call_direction(st, min_tp)
        rows.append(dict(subject=e.subject, genome=e.genome, direction=direction,
                         earliest_gut_tp=eg, earliest_vagina_tp=ev_t,
                         n_timepoints=len({t for _, t in st}), note=note))
    out = pd.DataFrame(rows, columns=["subject", "genome", "direction", "earliest_gut_tp",
                                      "earliest_vagina_tp", "n_timepoints", "note"])
    out = out.sort_values(["direction", "subject"])
    os.makedirs(a.outdir, exist_ok=True)
    out.to_csv(f"{a.outdir}/direction_calls.tsv", sep="\t", index=False)
    tally = out.direction.value_counts().to_dict() if len(out) else {}
    print(f"[08 direction] {len(out)} event(s) -> {tally}")
    print(f"Wrote {a.outdir}/direction_calls.tsv")


if __name__ == "__main__":
    main()
