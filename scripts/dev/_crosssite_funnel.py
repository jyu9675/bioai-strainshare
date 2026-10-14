#!/usr/bin/env python3
"""
Within-woman cross-site (gut <-> vagina) co-detection funnel, Goltsman cohort.

The Fijian pilot showed that "no shared strains" collapses two different results: taxa
genuinely absent from one site, and taxa present at both sites but below the breadth needed
to compare them (docs/fijian-pilot-findings.md). This applies the same funnel to Goltsman,
which is the deeper cohort, so the two can be told apart there too.

Funnel, per woman:
  detected at gut  ->  detected at BOTH sites (co-detection)  ->  jointly deep enough to
  compare  ->  shared strain

A taxon that never reaches the comparable stage is NOT evidence of absence. That distinction
is the whole point of the funnel.
"""
import os, glob, itertools
import pandas as pd

META = "/mnt/d/bioai/data/metadata.tsv"
PROF = "/mnt/d/bioai/results/profiles"
OUT = "/mnt/d/bioai/results/crosssite_funnel"
DETECT_COV = 1.0      # "present at this site at all"
DETECT_BREADTH = 0.10
COMPARABLE_BREADTH = 0.5   # both sides must plausibly overlap this much

os.makedirs(OUT, exist_ok=True)

good = {os.path.basename(d)[:-3] for d in glob.glob(f"{PROF}/*.IS")
        if os.path.exists(f"{d}/raw_data/covT.hd5")}
meta = pd.read_csv(META, sep="\t")
meta = meta[meta["sample"].isin(good)]


def profile(sample):
    gi = f"{PROF}/{sample}.IS/output/{sample}.IS_genome_info.tsv"
    if not os.path.exists(gi):
        return None
    try:
        return pd.read_csv(gi, sep="\t")
    except Exception:
        return None


def best(sample_list):
    """deepest profile: highest median coverage among genomes above the detection floor"""
    scored = []
    for s in sample_list:
        d = profile(s)
        if d is None:
            continue
        ok = d[(d.coverage >= DETECT_COV) & (d.breadth >= DETECT_BREADTH)]
        if len(ok):
            scored.append((float(ok.coverage.median()), len(ok), s))
    return max(scored)[2] if scored else None


rows = []
for subj, grp in meta.groupby("subject"):
    g = best(grp[grp.bodysite == "gut"]["sample"].tolist())
    v = best(grp[grp.bodysite == "vagina"]["sample"].tolist())
    if not g or not v:
        continue
    dg, dv = profile(g), profile(v)
    dg = dg[(dg.coverage >= DETECT_COV) & (dg.breadth >= DETECT_BREADTH)]
    dv = dv[(dv.coverage >= DETECT_COV) & (dv.breadth >= DETECT_BREADTH)]
    gset = dict(zip(dg.genome, zip(dg.coverage, dg.breadth)))
    vset = dict(zip(dv.genome, zip(dv.coverage, dv.breadth)))
    both = sorted(set(gset) & set(vset))
    for gen in both:
        gc, gb = gset[gen]
        vc, vb = vset[gen]
        rows.append(dict(subject=subj, gut_sample=g, vag_sample=v, genome=gen,
                         gut_cov=gc, gut_breadth=gb, vag_cov=vc, vag_breadth=vb,
                         min_breadth=min(gb, vb),
                         comparable=min(gb, vb) >= COMPARABLE_BREADTH))
    print(f"{subj}: gut={g} ({len(gset)} taxa)  vagina={v} ({len(vset)} taxa)  "
          f"co-detected={len(both)}", flush=True)

df = pd.DataFrame(rows)
if df.empty:
    print("\nno co-detections at all")
    raise SystemExit

df.to_csv(f"{OUT}/codetections.tsv", sep="\t", index=False)

print("\n=== CROSS-SITE CO-DETECTION FUNNEL ===")
print(f"women analysed                     {df.subject.nunique()}")
print(f"co-detected (gut AND vagina) rows  {len(df)}")
print(f"  distinct taxa                    {df.genome.nunique()}")
print(f"jointly comparable (both br>={COMPARABLE_BREADTH})  {int(df.comparable.sum())}")
print(f"  -> of co-detections              {100*df.comparable.mean():.0f}%")

print("\nper woman:")
for subj, g in df.groupby("subject"):
    print(f"  {subj:5s} co-detected={len(g):3d}  comparable={int(g.comparable.sum()):2d}")

print("\nco-detected taxa (how many women each):")
print(df.genome.value_counts().to_string())

print(f"\nwrote {OUT}/codetections.tsv")
