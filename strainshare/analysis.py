"""M1 + M2 — shared-strain call, within-vs-between-person null, and the
translocation-vs-contamination discriminator.

Works for ANY paired-site strain-sharing question — the two sites come from
``cfg['site_pair']`` (default ["gut","vagina"], for which the class labels are the
historical within_gut_vagina / between_gut_vagina).
"""
import os

import numpy as np
import pandas as pd

from .config import STANDARD, site_classes


def bray_curtis(a, b):
    a = a.fillna(0).values
    b = b.fillna(0).values
    s = a.sum() + b.sum()
    return 1.0 if s == 0 else float(np.abs(a - b).sum() / s)


def classify_pair(r1, r2, site_pair=("gut", "vagina")):
    """Classify a sample pair from metadata rows into the null design classes."""
    a, b = site_pair
    same_subj = r1.subject == r2.subject
    sites = {r1.bodysite, r2.bodysite}
    cross = sites == {a, b}
    if same_subj and cross:
        return f"within_{a}_{b}"           # the signal
    if (not same_subj) and cross:
        return f"between_{a}_{b}"           # the null
    if same_subj and len(sites) == 1:
        return "within_same_site"          # positive control (same site over time)
    return "other"


def analyze(compare, meta, mpa, cfg=None):
    """Core analysis. Returns dict of DataFrames: pairs_tagged, species_within_between,
    translocation_candidates. `compare` needs columns genome,name1,name2,popANI,
    percent_genome_compared; `meta` needs sample,subject,timepoint,bodysite; `mpa` is a
    community table (rows=features, cols=samples)."""
    cfg = cfg or STANDARD
    popani = cfg["shared_strain"]["popani_primary"]
    breadth = cfg["shared_strain"]["breadth_min"]
    bc_sim = cfg["contamination"]["bray_curtis_similar_max"]
    site_a, site_b, within_cls, between_cls = site_classes(cfg)

    meta = meta.set_index("sample")
    mpa = mpa[[c for c in mpa.columns if c in meta.index]]

    rows = []
    for _, x in compare.iterrows():
        s1, s2 = x["name1"], x["name2"]
        if s1 not in meta.index or s2 not in meta.index:
            continue
        r1, r2 = meta.loc[s1], meta.loc[s2]
        cls = classify_pair(r1, r2, (site_a, site_b))
        shared = (x["popANI"] >= popani) and (x["percent_genome_compared"] >= breadth)
        bc = bray_curtis(mpa[s1], mpa[s2]) if (s1 in mpa.columns and s2 in mpa.columns) else np.nan
        rows.append(dict(genome=x["genome"], s1=s1, s2=s2, subject1=r1.subject, subject2=r2.subject,
                         site1=r1.bodysite, site2=r2.bodysite, pair_class=cls,
                         popANI=x["popANI"], breadth=x["percent_genome_compared"],
                         shared_strain=shared, bray_curtis=bc))
    pairs = pd.DataFrame(rows, columns=["genome", "s1", "s2", "subject1", "subject2", "site1",
                                        "site2", "pair_class", "popANI", "breadth",
                                        "shared_strain", "bray_curtis"])

    def rate(sub):
        g = sub.groupby("genome")["shared_strain"].agg(["mean", "sum", "count"])
        return g.rename(columns={"mean": "shared_rate", "sum": "n_shared", "count": "n_pairs"})

    w = rate(pairs[pairs.pair_class == within_cls]).add_prefix("within_")
    b = rate(pairs[pairs.pair_class == between_cls]).add_prefix("between_")
    swb = w.join(b, how="outer").fillna(0)
    swb["within_minus_between"] = swb["within_shared_rate"] - swb["between_shared_rate"]
    swb = swb.sort_values("within_minus_between", ascending=False)

    cand = pairs[(pairs.pair_class == within_cls) & (pairs.shared_strain)].copy()
    cand["verdict"] = np.where(cand["bray_curtis"] >= bc_sim, "translocation_candidate",
                               "contamination_suspect")
    cand = cand.sort_values(["verdict", "popANI"], ascending=[True, False])

    return {"pairs_tagged": pairs, "species_within_between": swb, "translocation_candidates": cand}


def analyze_files(compare_path, meta_path, metaphlan_path, outdir, cfg=None):
    compare = pd.read_csv(compare_path, sep="\t")
    meta = pd.read_csv(meta_path, sep="\t")
    mpa = pd.read_csv(metaphlan_path, sep="\t", index_col=0)
    out = analyze(compare, meta, mpa, cfg)
    os.makedirs(outdir, exist_ok=True)
    out["pairs_tagged"].to_csv(f"{outdir}/pairs_tagged.tsv", sep="\t", index=False)
    out["species_within_between"].to_csv(f"{outdir}/species_within_between.tsv", sep="\t")
    out["translocation_candidates"].to_csv(f"{outdir}/translocation_candidates.tsv", sep="\t", index=False)
    return out
