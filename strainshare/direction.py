"""M4 — transmission DIRECTION inference for within-person gut<->vagina shared strains.

Direction is NEVER inferred from a sharing call alone (no strain-sharing method can). We
infer it ONLY from longitudinal acquisition timing: the site where a shared strain is
detected EARLIER is the putative source. Events without enough temporal spread — including
any cross-sectional cohort — are reported as ``direction_unresolved``, not guessed.
"""
import os

import numpy as np
import pandas as pd

from .config import STANDARD, site_classes


def sample_sites_times(pairs, subject, genome, breadth_min, meta):
    """Every sample of `subject` in which `genome` is detected (breadth >= min)."""
    sub = pairs[(pairs.genome == genome) & (pairs.breadth >= breadth_min)]
    samples = set()
    for _, r in sub.iterrows():
        for s, subj in [(r.s1, r.subject1), (r.s2, r.subject2)]:
            if subj == subject:
                samples.add(s)
    return [(meta.loc[s].bodysite, meta.loc[s].timepoint) for s in samples if s in meta.index]


def call_direction(sites_times, min_timepoints, site_a="gut", site_b="vagina"):
    """Return (direction, earliest_a_tp, earliest_b_tp, note). Direction is named with the
    real bodysite strings, e.g. 'gut_to_vagina' or 'oral_to_gut'."""
    times = sorted({t for _, t in sites_times})
    if len(times) < min_timepoints:
        return "direction_unresolved", np.nan, np.nan, "insufficient timepoints (needs longitudinal)"
    ta = [t for site, t in sites_times if site == site_a]
    tb = [t for site, t in sites_times if site == site_b]
    if not ta or not tb:
        return "direction_unresolved", np.nan, np.nan, "strain not detected at both sites"
    ea, eb = min(ta), min(tb)
    if ea < eb:
        return f"{site_a}_to_{site_b}", ea, eb, f"{site_a} precedes {site_b}"
    if eb < ea:
        return f"{site_b}_to_{site_a}", ea, eb, f"{site_b} precedes {site_a}"
    return "concurrent", ea, eb, "first detected at same timepoint"


def run(candidates, pairs, meta, cfg=None):
    cfg = cfg or STANDARD
    breadth_min = cfg["shared_strain"]["breadth_min"]
    min_tp = cfg["direction"]["min_timepoints"]
    site_a, site_b, _, _ = site_classes(cfg)
    meta = meta.set_index("sample")

    if "verdict" in candidates.columns:
        candidates = candidates[candidates.verdict == "translocation_candidate"]
    events = candidates[["subject1", "genome"]].drop_duplicates().rename(columns={"subject1": "subject"})

    col_a, col_b = f"earliest_{site_a}_tp", f"earliest_{site_b}_tp"
    rows = []
    for _, e in events.iterrows():
        st = sample_sites_times(pairs, e.subject, e.genome, breadth_min, meta)
        direction, ea, eb, note = call_direction(st, min_tp, site_a, site_b)
        rows.append({"subject": e.subject, "genome": e.genome, "direction": direction,
                     col_a: ea, col_b: eb, "n_timepoints": len({t for _, t in st}), "note": note})
    out = pd.DataFrame(rows, columns=["subject", "genome", "direction", col_a, col_b, "n_timepoints", "note"])
    return out.sort_values(["direction", "subject"]) if len(out) else out


def run_files(candidates_path, pairs_path, meta_path, outdir, cfg=None):
    candidates = pd.read_csv(candidates_path, sep="\t")
    pairs = pd.read_csv(pairs_path, sep="\t")
    meta = pd.read_csv(meta_path, sep="\t")
    out = run(candidates, pairs, meta, cfg)
    os.makedirs(outdir, exist_ok=True)
    out.to_csv(f"{outdir}/direction_calls.tsv", sep="\t", index=False)
    return out
