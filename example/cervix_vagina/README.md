# Real-data run — cervix ↔ vagina strain sharing (public ENA cohort)

A live end-to-end validation of strainshare on **real public data** — not synthetic.

**Data:** ENA **PRJNA982400** (open), 8 women, paired **cervix + vaginal** shotgun metagenomes.
Fetched with `strainshare fetch`, mapped to a vaginal reference, profiled with inStrain, then:

```bash
strainshare fetch --bioproject PRJNA982400 --site-map "V=vagina,C=cervix" --max-subjects 8 --download
snakemake ...                                  # map -> profile -> compare
strainshare analyze --site-pair cervix,vagina ...
```

## Result — the within-vs-between null holds cleanly

| species | within-person shared | between-person shared | within − between |
|---|---|---|---|
| *G. vaginalis* | **1.0** (2/2) | 0.0 (0/10) | **1.0** |
| *L. crispatus* | **1.0** (1/1) | 0.0 (0/1) | **1.0** |
| *L. iners* | **1.0** (3/3) | 0.17 (2/12) | **0.83** |

**6 confident within-woman cervix↔vagina shared strains** (popANI ≥ 0.99999, breadth 0.78–0.95)
across 6 of 8 women; **every** within-person cross-site comparison that cleared breadth was shared,
while unrelated women were not (see `fig1_within_vs_between.png`, `popani_breadth.png`).

## Two things the tool got right
- **The *L. iners* nuance:** unrelated women share *L. iners* 17% of the time (vs 0% for the more
  strain-diverse *L. crispatus*/*G. vaginalis*) — the known lower diversity of *L. iners*, and exactly
  what the generalist filter is for. The within−between signal stays strongly positive (0.83).
- **Adjacent-site honesty:** all 6 shared strains were flagged *similar-community* (not
  *translocation_candidate*) — correct, because cervix and vagina are one continuous community. For
  distinct sites (e.g. rectum↔vagina) a shared strain + dissimilar community would flag as translocation.

## Scope
Proof that the pipeline runs on fetched public data and yields a correct, nuanced multi-subject
result — a positive-signal complement to the depth-limited Goltsman negative. Only the dominant
species reach breadth at this cohort's depth; deeper data would resolve more taxa.
