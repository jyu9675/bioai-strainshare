# Cervix↔vagina validation (n=20) — strainshare on public data

A larger positive-control run of [strainshare](../../README.md) on **public** shotgun metagenomes,
expanding the earlier 8-woman validation ([`example/cervix_vagina/`](../cervix_vagina/)).

## Data & method
- **Source:** ENA **PRJNA982400** (Fijian cohort; 92 women each with paired cervix + vagina WGS).
  Sample sheet built with `strainshare fetch --bioproject PRJNA982400`.
- **Run:** 20 women (40 samples) → unpaired bowtie2 map to the 33-genome broad reference →
  `inStrain profile` → `inStrain compare` → `strainshare analyze --site-pair cervix,vagina`.
  (35/40 profiled; 4 low-biomass samples incomplete and excluded from compare.)

## Result — the within- vs between-person null holds cleanly
630 comparable genome-pairs → **37 within-woman cervix↔vagina shared strains** (21 translocation
candidates, 16 flagged as possible contamination — expected, since cervix and vagina are adjacent and
share a community).

| Species | within-person shared | between-person shared |
|---|---|---|
| *L. iners* | 7/7 (100%) | 3/84 (3.6%) |
| *G. vaginalis* | 5/5 (100%) | 2/50 (4%) |
| *G. piotii* | 4/4 (100%) | 1/36 (2.8%) |
| *G. leopoldii* | 4/4 (100%) | 2/21 (9.5%) |
| *Sneathia vaginalis* | 3/3 | 1/15 |
| *Fannyhessea vaginae* | 3/3 | 2/18 |
| +7 more | within = 100% | near-0 |

A woman's two sites share the **same strain ~100% of the time**; unrelated women almost never do — the
signature a valid strain-sharing tool must produce. See `species_within_between.tsv` and
`figures/fig1_within_vs_between.png`.

## Honest scope
This is the tool's **positive-control axis** (adjacent sites with a shared community), *not* the
gut→vaginal transmission biology. It validates the method — the within-vs-between null, the
translocation-vs-contamination discriminator, and directionality — that the rectovaginal study depends on.

## Files
`species_within_between.tsv` · `pairs_tagged.tsv` · `translocation_candidates(_scored).tsv` ·
`direction_calls.tsv` · `genome_generalist_flags.tsv` · `metadata.tsv` · `figures/`
