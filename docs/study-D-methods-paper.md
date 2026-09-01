# Study D — Methods paper outline

> **A full prose draft now exists: [`manuscript-draft.md`](manuscript-draft.md)** (abstract → results →
> discussion → methods → limitations, every number reproducible from `example/`). This outline remains the
> figure/dataset plan behind it.

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
  1. **Synthetic ground truth + real-read validation** — two layers, both implemented in
     [`../example/benchmark/`](../example/benchmark):
     - *Model* ([`scripts/10_benchmark.py --mode model`](../scripts/10_benchmark.py)): coverage→breadth +
       finite-position popANI, runs anywhere; the illustrative sweep + inStrain→StrainGE crossover (Fig 3, model).
     - *Real reads* ([`scripts/10b_reads_benchmark.sh`](../scripts/10b_reads_benchmark.sh)): **run**, not a
       scaffold. Simulates reads from real *L. crispatus* (same strain) and a 0.3%-diverged copy (different
       strain) at 0.5–30×, through the actual wgsim→bowtie2→inStrain pipeline. **Result (Fig 3, reads):**
       same-strain popANI = **1.000**, different-strain = **0.9971** (recovering the injected 0.3%),
       cleanly split by the 0.999 threshold at every evaluable depth. **Key empirical finding:** the
       breadth-limited *confidence* floor (percent_compared ≥ 0.5) is reached only at **~10×**, not ~1× —
       0.5× and 2× yield no comparison at all, and 5× gives the right popANI but on just 30% of the genome.
       The model's coverage→breadth curve was recalibrated to this. Direct implication: low-biomass vaginal
       metagenomes frequently sit *below* this floor, which is precisely where the StrainGE fallback (M3) earns its place.
     - *Precision edge* ([`scripts/10c_reads_benchmark_scaled.sh`](../scripts/10c_reads_benchmark_scaled.sh), 3 species ×
       4 near-boundary divergences × 3 replicates = 39 real comparisons at 20×): maps the **resolution limit of the
       0.999 threshold**. popANI tracks divergence almost exactly (SD across replicates < 1×10⁻⁴), and — critically —
       **the same across *L. crispatus*, *L. iners*, and *G. vaginalis*** (species-agnostic). Result:
       0.05% divergence → popANI ~0.99952 (**called identical**), 0.1% → ~0.99903 (**knife-edge**, flips by species),
       ≥0.2% → reliably flagged different. **The standard resolves strains diverged ≳0.1–0.2%; below ~0.1% a distinct
       strain is indistinguishable from identical.** (Fig 6.)
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
- **F6** precision edge — popANI vs near-boundary divergence across species; resolution limit of the 0.999 threshold (~0.1%)
- **Table 1** the standard, versioned, side-by-side with inStrain/StrainPhlAn/StrainGE/SameStr/TRACS defaults —
  **drafted:** [`table1-tool-comparison.md`](table1-tool-comparison.md)

## Validation / claims we can defend

- Reproduces within > between relatedness on the public pilot (method sanity).
- Positive controls behave (same-site-over-time shares; unrelated-person pairs don't).
- Direction module returns `unresolved` on cross-sectional data by construction — a feature, framed
  as honesty about what strain sharing can and cannot show.
- A *rigorous negative* (no identical gut↔vaginal strain survives the full filter stack) is itself a
  publishable, defensible result given the confound literature.
- The 0.999 threshold has a **sharp, species-agnostic resolution limit of ~0.1% divergence** (empirically, SD < 10⁻⁴
  across replicates in *L. crispatus*, *L. iners*, *G. vaginalis*) — so a "shared strain" call means "diverged by less
  than ~0.1%," a claim we can state quantitatively rather than by convention.

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
