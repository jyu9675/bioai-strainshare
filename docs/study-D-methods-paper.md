# Study D — Methods paper outline

**Working title:** *strainshare: a standardized, contamination-aware framework for detecting
and directionally resolving gut↔cervicovaginal bacterial strain sharing*

**One-line thesis:** VALENCIA standardized *community-state-type* calls; there is no equivalent
standard for *strain-sharing* calls. `strainshare` fills that gap with fixed, versioned
thresholds, a built-in within-vs-between-person null, an explicit contamination discriminator,
a generalist-strain filter, and honest longitudinal-only direction inference — validated on a
public cohort and released as a portable workflow.

**Target venue (in priority order):** *Microbiome* · *Genome Biology* (Methods) · *mSystems*.
Precedent: VALENCIA (*Microbiome* 2020) and inStrain (*Nat Biotechnol* 2021) are both here.

---

## Why this paper exists (the gap)

1. **Strain-sharing thresholds are unstandardized.** Studies use different popANI cutoffs
   (e.g. 99.999% vs 99.995%); inStrain's own docs flag this as a cross-study comparability
   problem. Results are not comparable across labs — the exact problem VALENCIA solved for CSTs
   by replacing per-study hierarchical clustering with fixed reference centroids.
2. **No tool infers transmission *direction*.** inStrain, StrainPhlAn, StrainGE, and TRACS all
   explicitly decline to call direction. Yet direction is the biologically interesting question
   for gut↔FGT (who seeds whom).
3. **Strain sharing ≠ transmission.** Shared environment/diet inflate sharing between unrelated
   people; the stringent thresholds that exclude ~95% of false sharing also discard ~91% of true
   events. A defensible standard must ship the *controls* (null + generalist filter), not just a cutoff.
4. **Low-biomass FGT samples break coverage assumptions.** inStrain needs >6× for full breadth;
   many vaginal metagenomes never reach it. A standard must define a documented fallback (StrainGE
   to ~0.5×) rather than silently dropping targets.

> Positioning note: `strainshare` does **not** invent a new aligner or SNP caller. Like VALENCIA,
> its contribution is a *standard + the surrounding controls + a portable implementation*. That is
> exactly why VALENCIA became infrastructure despite being "just" a nearest-centroid classifier.

## What the standard defines (the deliverable)

A versioned spec (`strainshare_standard.yaml`, `spec_version` 0.1.0) fixing:

| Component | Rule | Rationale / source |
|---|---|---|
| Shared strain | `popANI ≥ 0.999` (lead) **and** `≥ 0.99999` (canonical) reported together; `percent_genome_compared ≥ 0.5` | inStrain canonical bar + pilot deck; report both so downstream studies pick either |
| Coverage floor | `≥ 5×` per sample for a valid strain comparison | below this popANI is unreliable |
| Significance | within-vs-between-person **null** per species: real biology ⇒ within ≫ between | the control most sharing papers omit |
| Contamination | shared strain + **dissimilar** community (Bray–Curtis) = translocation; + **similar** = cross-swab contamination | one strain moving vs whole-soup transfer |
| Generalist filter | genome "shared" in > 10% of between-person pairs ⇒ generalist/artifact, down-ranked | shared-environment confound |
| Direction | inferred **only** from longitudinal acquisition timing; cross-sectional ⇒ `direction_unresolved` | no method can call direction from sharing alone |
| Low biomass | targets below the coverage floor routed through **StrainGE** (≥ 0.5× bound) | 0.5× is the verified floor (0.1× claim did not survive verification) |

## Methods (as they'll be written)

- **Reference set:** GTDB reps + NCBI for the target species (*L. crispatus, L. iners, L. jensenii,
  Gardnerella/Bifidobacterium vaginale* complex, *Prevotella bivia, E. coli*, enterococci), with
  gut-abundant controls (*Bacteroides fragilis*) as internal negatives; dReplicated before mapping.
- **Core pipeline:** bowtie2 → inStrain `profile` → `compare` (database mode) → the six modules
  (M1 shared-strain + null, M2 contamination, M3 StrainGE fallback, M4 direction, M5 generalist,
  M6 portable Snakemake). All thresholds read from the versioned standard.
- **Benchmarking datasets:**
  1. **Synthetic ground truth** — planted shared/not-shared strains, known directions, known
     contamination, across a coverage sweep (0.1×→30×) to map the sensitivity/specificity cliff and
     locate the inStrain→StrainGE crossover. **Implemented:** [`scripts/10_benchmark.py`](../scripts/10_benchmark.py)
     ships two backends — `--mode model` (runs anywhere; the coverage→breadth + finite-position popANI
     model behind Fig 3, seen in [`../example/benchmark/`](../example/benchmark)) and `--mode reads`
     (scaffold: simulate reads → real inStrain/StrainGE → same metrics, for the final figure on the cluster).
     The model already reproduces the expected shape: inStrain no-calls below its ~0.5× breadth floor,
     StrainGE rescues sensitivity at 0.5–1×, both converge and stay specific ≥6×.
  2. **Public pilot — Goltsman/DiGiulio (PRJNA288562)** — longitudinal pregnancy cohort with paired
     vaginal+gut; reproduce and sharpen the 2018 "related-not-identical" result with modern
     contamination-aware calls and a real null.
  3. **Hold-out application** — the lab's 191-sample paired vaginal–rectal cohort (cross-sectional →
     shows the direction module correctly returning `unresolved`, which is the point).

## Figures (planned)

- **F1** within- vs between-person popANI per species (the null; is the signal real?)
- **F2** popANI × community-similarity plane — translocation vs contamination quadrants
- **F3** coverage sweep — sensitivity/specificity of shared-strain calls; inStrain vs StrainGE crossover
- **F4** direction calls on longitudinal events (gut-first vs vagina-first vs unresolved)
- **F5** generalist filter — between-person shared rate per genome; what it removes and why
- **Table 1** the standard, versioned, side-by-side with inStrain/StrainPhlAn/StrainGE/SameStr/TRACS defaults

## Validation / claims we can defend

- Reproduces within > between relatedness on the public pilot (method sanity).
- Positive controls behave (same-site-over-time shares; unrelated-person pairs don't).
- Direction module returns `unresolved` on cross-sectional data by construction — a feature, framed
  as honesty about what strain sharing can and cannot show.
- A *rigorous negative* (no identical gut↔vaginal strain survives the full filter stack) is itself a
  publishable, defensible result given the confound literature.

## Availability

Code: `github.com/jyu9675/bioai-strainshare` (MIT). Versioned standard + Snakemake workflow +
synthetic benchmark. `CITATION.cff` included for a citable release (tag `v0.1.0`, mint a Zenodo DOI
at submission).

## Author roles (to confirm)

Lead / corresponding: **you**. Kwon Lab: cohorts, clinical framing, co-senior. Flag: the VMT/CTV-05
engraftment application (Studies A/B) is the *biology* paper that cites this *methods* paper — keep
them separate so D can ship first.

## Rough timeline

1. Synthetic benchmark + coverage sweep (F3) — extends existing smoke test.
2. Re-run the public pilot through the full module stack (F1, F2, F4, F5).
3. Draft + Table 1 tool comparison.
4. Tag `v0.1.0`, Zenodo DOI, submit.

---

*Grounded in a verified deep-research pass (see [`design-note.html`](design-note.html)); every
threshold above is implemented in [`../scripts/strainshare_standard.yaml`](../scripts/strainshare_standard.yaml).*
