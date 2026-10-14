# Cervix↔vagina validation (n=26) — strainshare on public data

The **largest** positive-control run of [strainshare](../../README.md) on **public** shotgun
metagenomes — the expanded version of [`example/cervix_vagina_n20/`](../cervix_vagina_n20).

## Data & method
- **Source:** ENA **PRJNA982400** (Fijian cohort; 92 women with paired cervix + vagina WGS).
- **Run:** targeted all 92 women; **26 completed both sites** before the laptop link degraded (the run is
  resumable). 59 profiles compared → `strainshare analyze --site-pair cervix,vagina` against the 33-genome
  broad reference. (ENA throttled the download mid-burst; fixed by a retry-pause in the driver — see
  `scripts/dev/_cx_test.sh`.)

## Result — a clean, strong within- vs between-person null
2,137 comparable genome-pairs → **76 within-woman cervix↔vagina shared strains** (24 translocation
candidates; 52 flagged as possible contamination — expected, since cervix and vagina share a community).

| Species | within-person shared | between-person shared |
|---|---|---|
| *L. iners* | 14/14 (100%) | 13/238 (5.5%) |
| *G. vaginalis* | 9/10 (90%) | 3/214 (1.4%) |
| *G. piotii* | 8/8 (100%) | 1/113 (0.9%) |
| *G. swidsinskii* | 6/6 (100%) | 1/58 (1.7%) |
| *Sneathia vaginalis* | 6/6 (100%) | 1/42 (2.4%) |
| *Megasphaera lornae* | 6/6 (100%) | 4/75 (5.3%) |
| *Prevotella amnii* | 6/6 (100%) | 2/36 (5.6%) |
| *Fannyhessea vaginae* | 7/8 (88%) | 3/109 (2.8%) |
| *Gardnerella leopoldii* | 7/8 (88%) | 3/104 (2.9%) |
| *Aerococcus christensenii* | 3/3 | 1/21 |

Across ~14 species, a woman's two sites share the **same strain ~90–100% of the time**; unrelated women
almost never do (~0–6%). See `species_within_between.tsv` and `figures/fig1_within_vs_between.png`.

## Honest scope
Positive-control axis (adjacent sites, shared community) — **not** the gut→vaginal transmission biology.
It validates the method (within-vs-between null, translocation-vs-contamination discriminator,
directionality) that the rectovaginal study relies on, at the largest scale run to date on open data.

## Files
`species_within_between.tsv` · `pairs_tagged.tsv` · `translocation_candidates(_scored).tsv` ·
`direction_calls.tsv` · `genome_generalist_flags.tsv` · `metadata.tsv` · `figures/`
