# The between-person null — and why the breadth floor is load-bearing

*A Study D (methods) result. Between-person, same-site strain comparisons across two cohorts:
Goltsman/DiGiulio (PRJNA288562, 4 unrelated US women, gut↔gut) and the Fijian pilot
(PRJNA826539, 3 women, same-site). Data in [`../example/fijian/`](../example/fijian),
figure `../example/figures/fig_breadth_floor.png`.*

## The gap this fills

Every strain-sharing claim needs a null: *what popANI do people who share nothing produce?*
The pilot's original null ([`04b_between_person_compare.sh`](../scripts/04b_between_person_compare.sh))
compared **gut↔vagina** pairs only. That leaves the question the rectovaginal study actually
depends on — do unrelated people share strains **at the same site**? — untested.

That gap had a concrete cost. It let a between-woman *P. vulgatus* call in the Fijian pilot be
misread as a generalist taxon, when the control that would have settled it did not exist
(see [`fijian-pilot-findings.md`](./fijian-pilot-findings.md)).

## Result 1 — popANI without a breadth floor has a ~22% false-positive rate

Across 54 between-person comparisons that produced a value, **12 (22%) reach popANI ≥ 0.999** —
the same-strain threshold — **while comparing less than 50% of the genome.** Every one of them is
an artifact of comparing almost nothing:

| | rows with a value | popANI ≥ 0.999 | of those, breadth artifacts | genuine shared |
|---|--:|--:|--:|--:|
| Goltsman (US) gut↔gut | 39 | 12 | **12 (100%)** | 0 |
| Fijian same-site | 15 | 1 | 0 | 1 |
| **combined** | **54** | **13** | **12 (92%)** | **1** |

The artifacts are not marginal. They sit at `percent_compared` **0.00016–0.052** — between 0.016% and
5.2% of the genome — and **six of the twelve report popANI of exactly 1.00000**. Ranked naively by
popANI, they are the *top* hits in the dataset:

| genome | pair | popANI | `percent_compared` |
|---|---|--:|--:|
| *L. crispatus* | M4 × P2 | **1.00000** | 0.00126 |
| *L. jensenii* | M4 × P2 | **1.00000** | 0.00016 |
| *L. crispatus* | M4 × T7 | **1.00000** | 0.00120 |
| *L. jensenii* | M4 × T18 | **1.00000** | 0.00016 |
| *L. jensenii* | P2 × T18 | **1.00000** | 0.00035 |
| *L. jensenii* | T18 × T7 | **1.00000** | 0.00022 |
| *L. crispatus* | P2 × T18 | 0.99957 | 0.00115 |
| *F. prausnitzii* | M4 × P2 | 0.99940 | 0.03056 |

These are vaginal *Lactobacillus* genomes being "detected" in gut samples on a few hundred bases of
spurious mapping — `L_jensenii` at 0.00016 breadth is roughly **500 bases** of a 2 Mb genome. Report
popANI alone and you publish six *perfect* strain-sharing events between women who have never met.

![between-person popANI vs breadth](../example/figures/fig_breadth_floor.png)

## Result 2 — the false-positive rate is cohort-dependent, and worst where data are thin

The two cohorts behave very differently:

- **Goltsman:** only 7/48 rows (15%) clear the breadth floor at all; 12 of the 39 valued rows are
  artifacts (**31%**).
- **Fijian:** 14/15 rows (93%) clear the floor; **zero** artifacts.

The difference is depth relative to the reference, not biology. Fijian profiles are deep against a
narrow community; Goltsman gut profiles are shallow against a reference containing vaginal genomes
that barely map. **The floor matters most precisely where the data are weakest — which is where
the temptation to relax it is strongest.**

## Result 3 — one genuine between-person shared strain

The single call that survives both criteria is the Fijian *P. vulgatus* pair (107R ↔ 57R, popANI
0.99971 at 77% breadth). It is not a breadth artifact, not a generalist taxon, and not contamination
— the full elimination is in [`fijian-pilot-findings.md`](./fijian-pilot-findings.md). Two unrelated
women in one community genuinely share a gut strain.

## What this means for the standard

1. **`popani_primary` and `breadth_min` are a pair, not a primary criterion plus a nicety.**
   Reporting either alone is not a weaker version of the standard; on this data it is wrong 22% of
   the time. The versioned standard already encodes both — this quantifies the cost of dropping one.
2. **Every cohort needs its own same-site between-person null.** The rate above is a property of the
   cohort's depth and reference, not a universal constant, so it cannot be cited from another study.
3. **Rank candidate calls by breadth, never by popANI.** A popANI-sorted table puts the artifacts on
   top.

## Reproducing

```bash
# the Goltsman between-subject gut<->gut comparisons
python scripts/dev/_pvulgatus_between.py

# the broader same-site null (both body sites, N profiles per subject; resumable)
N_PER_SUBJECT=2 python scripts/dev/_between_person_null.py

# the figure
python scripts/plot_breadth_floor.py \
  --inputs "example/fijian/goltsman_pvulgatus_between.tsv:Goltsman (US) gut↔gut" \
           "example/fijian/genomeWide_compare.tsv:Fijian same-site" \
  --out example/figures/fig_breadth_floor.png
```

Rows where `popANI == 0` mean inStrain emitted a record but compared nothing usable. They are
excluded from the denominators above — counting them would flatter the artifact rate rather than
report it honestly.
