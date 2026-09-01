# strainshare: a standardized, contamination-aware framework for gut–cervicovaginal bacterial strain sharing, with an empirically characterized resolution limit

**Authors:** Jean Yu¹, [Kwon Lab collaborators]², Douglas S. Kwon²
¹ [affiliation] · ² Ragon Institute of Mass General Brigham, MIT, and Harvard

*Draft v0.1 — generated from the analyses in this repository (github.com/jyu9675/bioai-strainshare).
Every quantitative claim is reproducible from `example/` and the numbered scripts.*

---

## Abstract

Whether bacterial strains move between the gut and the female genital tract (FGT) — and in which
direction — is a central open question for reproductive-health microbiome research, including vaginal
microbiota transplantation (VMT) and live-biotherapeutic engraftment. Yet strain-sharing analysis lacks
the standardization that VALENCIA brought to vaginal community-state typing: popANI thresholds vary
between studies, no tool infers transmission direction, and low-biomass FGT metagenomes routinely fall
below usable coverage. We present **strainshare**, a versioned, reference-based standard that packages a
population-aware shared-strain call, a within-vs-between-person null, an explicit
translocation-vs-contamination discriminator, a generalist-strain filter, longitudinal-only direction
inference, and a low-biomass StrainGE fallback. Using real reads simulated from *Lactobacillus crispatus*,
*L. iners*, and *Gardnerella vaginalis*, we show that (i) the pipeline recovers same-strain pairs at
popANI = 1.000 and 0.3%-diverged strains at 0.9971, cleanly split by the 0.999 threshold; (ii) the
breadth-limited **confidence floor is ~10× coverage**, not ~1×; and (iii) the threshold has a **sharp,
species-agnostic resolution limit of ~0.1% divergence** (replicate SD < 10⁻⁴). Applied to a public
pregnancy cohort (PRJNA288562; 4 subjects, 88 profiles), strainshare validates on positive controls
(11 confident within-site persistence calls) and returns a **rigorous negative** for gut↔FGT sharing —
which we show is driven by cross-site coverage starvation, not by detection of distinct strains. These
results yield a concrete design rule for future cohorts and a reusable standard for the field.

---

## 1. Introduction

The cervicovaginal microbiome is a major determinant of reproductive and HIV-acquisition risk, and
therapies that reshape it — VMT and *L. crispatus* live biotherapeutics — succeed or fail at the level of
individual strains: donor strains must engraft, and a recipient's endogenous strains form a competing
reservoir that resists displacement [1,2]. A natural and largely unexplored hypothesis is that the **gut
serves as a reservoir** seeding or reseeding the vagina. Testing it requires confidently deciding whether
a gut and a vaginal sample from the same person carry the *same* bacterial strain, and, ideally, which
site acquired it first.

Three gaps block this. First, **thresholds are unstandardized**: studies apply different popANI cutoffs,
which inStrain's own documentation flags as a cross-study comparability problem [3] — precisely the
situation VALENCIA resolved for community-state types by replacing per-study clustering with fixed
reference centroids [4]. Second, **no method infers transmission direction**: inStrain, StrainPhlAn,
StrainGE, and TRACS all decline to do so [3,5,6]. Third, **strain sharing is confounded** by shared
environment and by cross-swab contamination, and stringent thresholds that exclude ~95% of false sharing
also discard ~91% of true events [7].

We built strainshare to close these gaps as an *integration and a standard* — not a new aligner — and to
characterize, empirically, what its central threshold actually means.

## 2. Results

### 2.1 A versioned standard with built-in controls

strainshare fixes every threshold in a single versioned spec (`spec_version 0.1.0`) and ships the controls
the confound literature demands (Table 1; Methods). A shared-strain call requires popANI ≥ 0.999 (lead;
0.99999 canonical also reported) over percent_compared ≥ 0.5 at ≥ 5× coverage. Significance is judged by a
**within-vs-between-person null** rather than a bare cutoff; a candidate is split into translocation vs
cross-swab contamination by whether the two samples' communities are dissimilar or similar; genomes
"shared" across unrelated people are flagged **generalist** and down-ranked; and direction is inferred
**only** from longitudinal acquisition timing, returning `direction_unresolved` for cross-sectional data
rather than guessing.

### 2.2 Real-read validation: the pipeline recovers ground truth, with a ~10× confidence floor

Simulating reads from real *L. crispatus* (same strain) and a 0.3%-diverged copy (different strain) through
the actual wgsim → bowtie2 → inStrain pipeline, strainshare recovered the ground truth exactly:
same-strain **popANI = 1.000** (0 population SNPs) and different-strain **popANI = 0.9971** (~5,900 SNPs
over 2.04 Mb, matching the injected divergence), cleanly separated by the 0.999 threshold at every
evaluable depth (Fig. 3). Critically, the *breadth-limited* confidence floor — the depth at which
percent_compared reaches 0.5 — sits at **~10×, not ~1×**: 0.5× and 2× yielded no comparison at all, and 5×
produced the correct popANI on only 30% of the genome. Low-biomass FGT samples frequently fall below this
floor, motivating the StrainGE fallback (M3).

### 2.3 The 0.999 threshold has a sharp, species-agnostic resolution limit of ~0.1%

To characterize the threshold's resolving power we swept near-boundary divergences (0.05–0.3%) across three
species (*L. crispatus*, *L. iners*, *G. vaginalis*), three replicates each, at 20× (39 real comparisons).
popANI tracked divergence almost exactly, with **replicate SD < 10⁻⁴**, and — importantly — the three
species fell on the **same curve** (Fig. 6). A strain diverged by 0.05% gave popANI ~0.99952 and was called
identical; 0.1% (~0.99903) sat on the knife-edge, flipping by species; ≥0.2% was reliably flagged as
different. A "shared strain" call therefore carries a quantitative meaning — *diverged by less than
~0.1%* — that holds regardless of organism.

### 2.4 Cohort application: validated controls and a depth-limited negative

Applied to the Goltsman/DiGiulio pregnancy cohort (4 subjects, 88 profiles), strainshare fired correctly on
positive controls — **11 confident within-site persistence calls** (popANI ≥ 0.999 and breadth 0.8–0.94:
*L. iners* in vagina over time, *P. vulgatus* in gut) — and returned **zero** gut↔vagina shared strains,
within or between person (Fig. cohort). A capped between-person null was near-empty by biology: 39 of 40
unrelated gut↔vagina pairs shared no comparable genome at depth (a *Lactobacillus*-dominated vagina and a
*Bacteroides*-dominated gut have nothing to compare), and the single comparable pair gave popANI 0.9946
(different strain).

The negative is **breadth-driven, not a detection of distinct strains**: within-person cross-site
comparisons with popANI ≈ 1.0 rest on tens of bases (breadth 10⁻⁵–10⁻⁴) — the "popANI = 1.0 on a handful
of positions" artifact predicted by §2.2 — and the standard's breadth floor correctly rejects them. The
shared taxa across sites sit below the ~10× confidence floor, so the tool honestly reports "no evidence of
sharing (depth-limited)" rather than overclaiming.

## 3. Discussion

strainshare is to strain sharing what VALENCIA is to community-state typing: not a new algorithm, but a
fixed, reference-based, versioned standard plus the controls that make results comparable and defensible.
Its differentiators are honest direction inference (never manufactured from a sharing call), shipped
confound controls, an explicit low-biomass path, and — uniquely — an **empirically measured resolution
limit**, so a "shared strain" is a quantitative rather than conventional claim.

The cohort result carries a concrete design rule. Because gut↔FGT shared taxa are typically present at trace
abundance at one site, detecting cross-site strain sharing requires getting *those taxa* above ~10× breadth
— i.e., much deeper sequencing on the relevant samples, or targeted enrichment — rather than simply
increasing total depth. This directly informs the design of larger paired gut–vaginal cohorts and of
strain-level endpoints in VMT / live-biotherapeutic trials, where the biologically interesting questions
(does a gut reservoir predict engraftment? is relapsing *L. iners* a persisting or reseeded strain? [1,2])
are exactly the ones strainshare is built to answer once adequate depth is in hand.

## 4. Methods (summary)

**Standard and modules.** Thresholds live in `strainshare_standard.yaml`. M1 shared-strain call +
within/between null (`05_shared_strain_analysis.py`); M2 contamination discriminator (community Bray–Curtis);
M3 StrainGE low-biomass fallback (≥0.5×; scaffold); M4 direction from longitudinal timing
(`08_direction.py`); M5 generalist filter (`09_generalist_filter.py`); M6 portable Snakemake workflow. A
unified runner (`strainshare.py`) chains the analysis half cross-platform.

**Benchmarks.** `10_benchmark.py` provides a model backend and ingests real-read results; `10b`/`10c` drive
the real wgsim → bowtie2 → inStrain pipeline for the coverage-floor validation (§2.2) and the precision-edge
sweep (§2.3). Divergent strains are produced by mutating a real reference at a known SNP rate.

**Cohort.** 88 inStrain profiles (PRJNA288562) were compared pairwise (the all-N compare exceeds memory);
`04b_between_person_compare.sh` adds a capped between-person null. Community similarity for M2 used an
8-genome coverage proxy pending a full MetaPhlAn merge.

**Availability.** Code, the versioned standard, benchmarks, and all figures/tables:
github.com/jyu9675/bioai-strainshare (MIT; `CITATION.cff`). A tagged release + Zenodo DOI is planned at
submission.

## 5. Limitations

- The cohort is 4 subjects — this validates the *method* and yields a rigorous negative, not a population
  estimate.
- The gut↔FGT negative is **depth-limited**; it is not evidence for the absence of sharing, and a
  higher-depth cohort is required to test the reservoir hypothesis.
- The coverage-floor and precision-edge figures use simulated reads from reference genomes; real
  metagenomes add mapping complexity that a target-enriched follow-up should probe.
- M2's contamination axis currently uses an 8-genome proxy; a full-community MetaPhlAn profile would sharpen
  it (it does not affect the cohort's zero-candidate result).
- StrainGE's low-coverage advantage is partly from an author-run benchmark; M3 is a fallback, not a
  replacement.

## References

1. Vaginal microbiota transplantation: donor-strain engraftment in recurrent BV. medRxiv 2025.08.27.25334544.
2. *L. crispatus* live biotherapeutic (CTV-05/LACTIN-V): strain-resolved engraftment and competing endogenous reservoir. Cell Host & Microbe 2026, S1931-3128(26)00090-9.
3. inStrain — popANI, percent_compared, coverage/breadth. https://instrain.readthedocs.io/en/latest/important_concepts.html
4. VALENCIA — nearest-centroid vaginal community-state typing. Microbiome 2020, 10.1186/s40168-020-00934-6.
5. StrainGE (with StrainPhlAn comparison). Genome Biology 2022, 10.1186/s13059-022-02630-0.
6. TRACS — multi-kingdom transmission ("does not determine direction"). Nature Microbiology 2026, 10.1038/s41564-026-02339-x.
7. Shared environments complicate strain-transmission inference. Microbiome 2025, 10.1186/s40168-025-02051-8.
8. SameStr — standardized shared-strain defaults (MVS ≥99.9% over ≥5 kb). Microbiome 2022, 10.1186/s40168-022-01251-w.
9. HIV/ART geography-dependent gut microbiome effects. Nature Microbiology 2025, 10.1038/s41564-025-02157-7.

*See [`table1-tool-comparison.md`](table1-tool-comparison.md) for Table 1, [`study-D-methods-paper.md`](study-D-methods-paper.md)
for the full methods/figure plan, and [`goltsman-cohort-findings.md`](goltsman-cohort-findings.md) for the cohort detail.*
