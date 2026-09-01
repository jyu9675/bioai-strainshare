"""M4 — transmission DIRECTION inference for within-person gut<->vagina shared strains.

Direction is NEVER inferred from a sharing call alone (no strain-sharing method can). We
infer it ONLY from longitudinal acquisition timing: the site where a shared strain is
detected EARLIER is the putative source. Events without enough temporal spread — including
any cross-sectional cohort — are reported as ``direction_unresolved``, not guessed.
"""
import os

import numpy as np
import pandas as pd

from .config import STANDARD


def sample_sites_times(pairs, subject, genome, breadth_min, meta):
    """Every sample of `subject` in which `genome` is detected (breadth >= min)."""
    sub = pairs[(pairs.genome == genome) & (pairs.breadth >= breadth_min)]
    samples = set()
    for _, r in sub.iterrows():
        for s, subj in [(r.s1, r.subject1), (r.s2, r.subject2)]:
            if subj == subject:
                samples.add(s)
    return [(meta.loc[s].bodysite, meta.loc[s].timepoint) for s in samples if s in meta.index]


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


def run(candidates, pairs, meta, cfg=None):
    cfg = cfg or STANDARD
    breadth_min = cfg["shared_strain"]["breadth_min"]
    min_tp = cfg["direction"]["min_timepoints"]
    meta = meta.set_index("sample")

    if "verdict" in candidates.columns:
        candidates = candidates[candidates.verdict == "translocation_candidate"]
    events = candidates[["subject1", "genome"]].drop_duplicates().rename(columns={"subject1": "subject"})

    rows = []
    for _, e in events.iterrows():
        st = sample_sites_times(pairs, e.subject, e.genome, breadth_min, meta)
        direction, eg, ev_t, note = call_direction(st, min_tp)
        rows.append(dict(subject=e.subject, genome=e.genome, direction=direction,
                         earliest_gut_tp=eg, earliest_vagina_tp=ev_t,
                         n_timepoints=len({t for _, t in st}), note=note))
    out = pd.DataFrame(rows, columns=["subject", "genome", "direction", "earliest_gut_tp",
                                      "earliest_vagina_tp", "n_timepoints", "note"])
    return out.sort_values(["direction", "subject"]) if len(out) else out


def run_files(candidates_path, pairs_path, meta_path, outdir, cfg=None):
    candidates = pd.read_csv(candidates_path, sep="\t")
    pairs = pd.read_csv(pairs_path, sep="\t")
    meta = pd.read_csv(meta_path, sep="\t")
    out = run(candidates, pairs, meta, cfg)
    os.makedirs(outdir, exist_ok=True)
    out.to_csv(f"{outdir}/direction_calls.tsv", sep="\t", index=False)
    return out
