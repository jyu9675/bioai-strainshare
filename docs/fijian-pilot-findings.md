# Fijian rectal+vaginal pilot — two negatives, not one

*Open cohort PRJNA826539, 3 women with paired rectal + vaginal shotgun (57, 98, 107), profiled against
the 33-genome broad reference and compared with `inStrain compare`. Run directory
`/mnt/d/bioai/results/rv107_broad`; artifacts in [`../example/fijian/`](../example/fijian).*

This is the pilot cited in [`study-rectovaginal-pregnancy.md`](./study-rectovaginal-pregnancy.md) §1.
It was previously recorded as a single flat negative ("no within-woman cross-site sharing"). Re-reading
the per-genome coverage tables shows it is **two different negatives that must be reported separately**,
because they have opposite implications for study design.

## Negative 1 — commensals: a *true absence*

The dominant vaginal commensals are deeply covered vaginally and return **zero rows at any coverage** in
**every** rectal profile — not a trace, in any of the three women.

| Genome | 57V | 98V | 107V | 57R | 98R | 107R |
|---|--:|--:|--:|--:|--:|--:|
| *G. vaginalis* | 118.1× (0.909) | **185.0× (0.955)** | 9.3× (0.885) | — | — | — |
| *Gardnerella swidsinskii* | 10.3× (0.767) | 28.6× (0.919) | 7.4× (0.401) | — | — | — |
| *Gardnerella piotii* | 38.7× (0.919) | 14.5× (0.367) | 40.5× (0.935) | — | — | — |
| *Gardnerella leopoldii* | 34.2× (0.946) | 9.7× (0.590) | 10.3× (0.403) | — | — | — |
| *L. iners* | 44.9× (0.959) | 5.4× (0.915) | 3.5× (0.099) | — | — | — |

*(coverage × breadth; "—" = genome absent from the profile entirely)*

**185× vaginally against 0× rectally is a real biological absence, not a detection limit.** Sequencing
deeper will not produce a gut reservoir for these organisms. This is the finding that justifies
**excluding** *Lactobacillus* and vaginal *Gardnerella* from the target list — including them only
dilutes the signal.

## Negative 2 — BV taxa: *co-detected but uncallable*

The BV-associated organisms behave completely differently. They **are** present at both sites, in all
three women, at coverages that look promising:

| Genome | woman | rectum | vagina | co-detected? |
|---|--:|--:|--:|:--:|
| *P. bivia* | 57 | 6.7× (0.910) | 1.3× (0.165) | ✅ |
| *P. bivia* | 98 | 11.4× (0.948) | 1.7× (0.063) | ✅ |
| *P. bivia* | 107 | 10.6× (0.423) | 11.3× (0.143) | ✅ |
| *P. amnii* | 57 | 1.6× (0.096) | 16.8× (0.823) | ✅ |
| *P. amnii* | 107 | 3.8× (0.161) | 197.7× (0.880) | ✅ |
| *P. disiens* | 107 | 19.5× (0.949) | 6.5× (0.286) | ✅ |
| *Sneathia vaginalis* | 107 | 2.0× (0.715) | 117.3× (0.908) | ✅ |
| *Megasphaera lornae* | 57 | 1.0× (0.070) | 29.4× (0.946) | ✅ |
| *Finegoldia magna* | 107 | 10.7× (0.692) | 1.5× (0.063) | ✅ |

*P. bivia* is co-detected in **3/3 women**. And yet:

> **Not one within-woman rectum↔vagina pair produced a single comparable genome.**
> All 15 rows in `genomeWide_compare.tsv` are **between-woman, same-site**.

The reason is breadth *overlap*, not coverage. `inStrain compare` needs both profiles to cover the same
positions; the product of the two breadths never approaches the 0.5 `percent_compared` floor. The best
case in the cohort is *P. bivia* in woman 57 (0.910 rectal × 0.165 vaginal) — the deep side is fine, the
shallow side is not.

**So this negative is depth-limited, and says nothing about whether the strains are shared.** The honest
statement is *"co-detected, uncallable"*, and it is a positive argument for the cohort design rather
than a null result.

## The between-woman null — and one generalist strain

14 of the 15 between-woman pairs are correctly called **different** strains (popANI 0.978–0.997, all
below 0.999). **One is not**, and it matters:

| Genome | pair | popANI | `percent_compared` | call |
|---|---|--:|--:|---|
| *Fannyhessea vaginae* | 107V ↔ 57V | 0.97760 | 0.722 | different ✅ |
| *E. coli* | 57R ↔ 98R | 0.98451 | 0.647 | different ✅ |
| *G. vaginalis* | 57V ↔ 98V | 0.98809 | 0.851 | different ✅ |
| *L. iners* | 57V ↔ 98V | 0.99131 | 0.559 | different ✅ |
| *Prevotella disiens* | 107R ↔ 98R | 0.99691 | 0.673 | different ✅ |
| *Megasphaera lornae* | 57V ↔ 98V | 0.99416 | 0.916 | different ✅ |
| *P. bivia* | 57R ↔ 98R | 0.99784 | **0.452** | **no call** — under the floor |
| ***P. vulgatus*** | **107R ↔ 57R** | **0.99971** | **0.768** | **SHARED — between unrelated women** |

Two women in the same cohort carry gut *P. vulgatus* populations that are identical by the exact
criterion the study uses to call transmission, at 77% breadth. There are three ways that happens, and
they have very different consequences. We tested all three.

**Explanation 1 — *P. vulgatus* is a cosmopolitan generalist** (near-identical strains in everyone, so
the threshold is simply too loose for this taxon). **Rejected.** Run on the Goltsman cohort
(PRJNA288562), four unrelated US women with no shared environment, all six between-subject gut↔gut
pairs call *different* at good breadth:

| pair | popANI | `percent_compared` | call |
|---|--:|--:|---|
| M4 × P2 | 0.99835 | 0.788 | different |
| P2 × T7 | 0.99750 | 0.753 | different |
| M4 × T7 | 0.99597 | 0.725 | different |
| M4 × T18 | 0.98715 | 0.528 | different |
| P2 × T18 | 0.97939 | 0.539 | different |
| T18 × T7 | 0.97676 | 0.504 | different |

*P. vulgatus* strains are cleanly resolvable between unrelated hosts. The taxon is **not** a generalist,
and the Fijian pair is a genuine outlier against this baseline — not a threshold artifact.

**Explanation 2 — cross-sample contamination.** **Rejected.** Contamination transfers whole communities,
so it would make *multiple* genomes identical and the two communities converge. Neither holds:

- Of the **two** comparable genomes in this pair, only *P. vulgatus* is identical. *P. disiens* — compared
  at **higher** breadth (0.838 vs 0.768) — is clearly different at popANI 0.99330.
- The gut communities differ markedly. 57R carries *E. coli* (13.0×), *F. prausnitzii*, *B. fragilis*,
  *Blautia wexlerae*, *Roseburia intestinalis* and two *Bifidobacterium* spp. that are **absent** from
  107R; 107R carries *Sneathia vaginalis*, absent from 57R.

**Explanation 3 — the two women genuinely share this strain.** **Supported by elimination.** One specific
strain is shared against clearly distinct community backgrounds, while a co-present taxon at higher
breadth is not shared. That is the signature of a real acquisition event — shared household, water
source, or community contact — rather than an assay artifact.

### Why this matters more than a generalist would have

A generalist taxon is a nuisance you filter once. **Between-woman strain sharing in a community is a
first-order confounder for this study's entire design** — and simultaneously a form of evidence for its
premise. The proposal targets low-resource settings precisely because environmental transmission is
expected to be higher there; this is a direct, if n=1, observation of it happening.

Consequences:

- **The between-person null is not optional**, and must be run *within cohort*, not borrowed from a
  reference population. The US baseline above would have been useless for interpreting the Fijian pair
  had we not also had the Fijian between-woman comparisons.
- **Cross-site sharing within a woman cannot be attributed to rectovaginal transfer** until the same
  strain is shown *not* to be circulating between women in her community. In a village cohort, a strain
  shared rectum↔vagina may have entered both sites independently from a shared source.
- The M5 generalist filter (`09_generalist_filter.py`) still fires correctly here — but what it flagged
  is **community sharing, not taxon promiscuity**. The flag's interpretation is cohort-dependent, and
  the docs should say so.

The *P. bivia* row is the opposite control working correctly: a popANI that would otherwise read as
"close" is withheld because only 45% of the genome was compared.

## What this changes

1. **Target list.** Commensals out on evidence of true absence; **BV taxa are the highest-value
   secondary targets**, because they demonstrably reach both sites.
2. **Power calculation.** Depth must be powered on the **cross-site taxon**, and specifically on the
   *shallow* side of each pair — the constraint is overlapping breadth ≥0.5, not sample depth.
3. **Reporting.** "No sharing detected" is the wrong summary of this cohort. The right one is: *one
   organism class is genuinely absent from the gut; another is present at both sites but below the
   resolution of the assay.*
4. ***E. coli* remains rectum-only** in all three women (57R 13.0×, 98R 7.0×, absent from every vagina),
   so this cohort cannot speak to the primary pathogen hypothesis either way.
5. **Between-woman sharing is real and must be controlled within cohort.** The between-person null
   surfaced a confident cross-host shared strain (*P. vulgatus*, popANI 0.99971) that survives both
   the generalist test (6/6 unrelated US women call different) and the contamination test (only 1 of 2
   comparable genomes shared; communities distinct). Every within-woman transmission claim in the main
   study must be reported alongside the between-woman distribution **for that taxon in that cohort** —
   otherwise a community-acquired strain is indistinguishable from rectovaginal transfer.

## Reproducing

```bash
# per-sample, per-genome coverage/breadth (source of the tables above)
column -t example/fijian/genome_coverage.tsv

# the 15 compare rows — note every pair is between-woman, same-site
column -t example/fijian/genomeWide_compare.tsv

# the cross-cohort generalist test (6 between-subject gut<->gut pairs, Goltsman)
column -t example/fijian/goltsman_pvulgatus_between.tsv
python scripts/dev/_pvulgatus_between.py        # regenerate; needs the Goltsman profiles
```

Coverage rows are filtered to >0.5× from each profile's `*_genome_info.tsv`. The absence claims in
Negative 1 were checked against the **unfiltered** tables: the commensal genomes have no row at all in
the rectal profiles.
