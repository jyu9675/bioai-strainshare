#!/usr/bin/env python3
"""
Steps 3-4 of the pilot: turn inStrain `compare` output into the within-vs-between
null table and the popANI x community-similarity plane that separates true
translocation from cross-swab contamination.

Inputs
------
--compare   inStrain genomeWide_compare.tsv
              cols: genome, name1, name2, popANI, conANI, percent_genome_compared
--meta      sample metadata TSV, one row per sample name used in inStrain
              cols: sample, subject, timepoint, bodysite   (bodysite in {vagina,gut,oral})
--metaphlan merged MetaPhlAn species table (rows=clades, cols=samples, values=rel abund %)
--outdir    output directory

Outputs
-------
pairs_tagged.tsv           every genome x sample-pair with class + shared-strain flag + BrayCurtis
species_within_between.tsv per-species within vs between shared-strain rate (Fig 1 / Table)
translocation_candidates.tsv within-person gut-vaginal shared strains + contamination verdict (Fig 2)
"""
import argparse, sys
import pandas as pd
import numpy as np

POPANI_THRESH = 0.999        # deck standard (99.9%). inStrain canonical = 0.99999 -- see plan.
BREADTH_THRESH = 0.5         # percent_genome_compared
BC_SIMILAR = 0.5             # Bray-Curtis DISTANCE below this => "similar community" => contamination-like


def bray_curtis(a, b):
    a = a.fillna(0).values; b = b.fillna(0).values
    s = a.sum() + b.sum()
    return 1.0 if s == 0 else np.abs(a - b).sum() / s


def pair_class(r1, r2):
    """Classify a sample pair from metadata rows."""
    same_subj = r1.subject == r2.subject
    sites = {r1.bodysite, r2.bodysite}
    gv = sites == {"gut", "vagina"}
    if same_subj and gv:
        return "within_gut_vagina"          # the signal
    if (not same_subj) and gv:
        return "between_gut_vagina"          # the null
    if same_subj and len(sites) == 1:
        return "within_same_site"            # positive control (same site over time)
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--metaphlan", required=True)
    ap.add_argument("--outdir", default="../results")
    a = ap.parse_args()

    cmp = pd.read_csv(a.compare, sep="\t")
    meta = pd.read_csv(a.meta, sep="\t").set_index("sample")
    mpa = pd.read_csv(a.metaphlan, sep="\t", index_col=0)
    # keep species rows only if MetaPhlAn taxonomy strings are present
    mpa = mpa[[c for c in mpa.columns if c in meta.index]]

    rows = []
    for _, x in cmp.iterrows():
        s1, s2 = x["name1"], x["name2"]
        if s1 not in meta.index or s2 not in meta.index:
            continue
        r1, r2 = meta.loc[s1], meta.loc[s2]
        cls = pair_class(r1, r2)
        shared = (x["popANI"] >= POPANI_THRESH) and (x["percent_genome_compared"] >= BREADTH_THRESH)
        bc = bray_curtis(mpa[s1], mpa[s2]) if (s1 in mpa.columns and s2 in mpa.columns) else np.nan
        rows.append(dict(genome=x["genome"], s1=s1, s2=s2, subject1=r1.subject, subject2=r2.subject,
                         site1=r1.bodysite, site2=r2.bodysite, pair_class=cls,
                         popANI=x["popANI"], breadth=x["percent_genome_compared"],
                         shared_strain=shared, bray_curtis=bc))
    df = pd.DataFrame(rows)
    df.to_csv(f"{a.outdir}/pairs_tagged.tsv", sep="\t", index=False)

    # --- Fig 1 / Table: within vs between shared-strain rate per species ---
    def rate(sub):
        g = sub.groupby("genome")["shared_strain"].agg(["mean", "sum", "count"])
        return g.rename(columns={"mean": "shared_rate", "sum": "n_shared", "count": "n_pairs"})
    w = rate(df[df.pair_class == "within_gut_vagina"]).add_prefix("within_")
    b = rate(df[df.pair_class == "between_gut_vagina"]).add_prefix("between_")
    tab = w.join(b, how="outer").fillna(0)
    tab["within_minus_between"] = tab["within_shared_rate"] - tab["between_shared_rate"]
    tab.sort_values("within_minus_between", ascending=False).to_csv(
        f"{a.outdir}/species_within_between.tsv", sep="\t")

    # --- Fig 2: contamination verdict on within-person gut-vaginal shared strains ---
    cand = df[(df.pair_class == "within_gut_vagina") & (df.shared_strain)].copy()
    # DISSIMILAR community (high BC distance) => real translocation; SIMILAR => contamination-like
    cand["verdict"] = np.where(cand["bray_curtis"] >= BC_SIMILAR, "translocation_candidate",
                               "contamination_suspect")
    cand.sort_values(["verdict", "popANI"], ascending=[True, False]).to_csv(
        f"{a.outdir}/translocation_candidates.tsv", sep="\t", index=False)

    print(f"pairs: {len(df)} | within-GV shared: {int(df[(df.pair_class=='within_gut_vagina')].shared_strain.sum())}"
          f" | translocation candidates: {(cand.verdict=='translocation_candidate').sum()}"
          f" | contamination suspects: {(cand.verdict=='contamination_suspect').sum()}")
    print(f"Wrote pairs_tagged / species_within_between / translocation_candidates to {a.outdir}")


if __name__ == "__main__":
    main()
