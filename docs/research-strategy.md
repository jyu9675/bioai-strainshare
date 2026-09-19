# Research Strategy

*Rectum-to-vagina bacterial transmission in pregnancy: a strain-resolved, longitudinal study in
low-resource settings.* Companion to the [Specific Aims](specific-aims.md) and the
[full proposal](study-rectovaginal-pregnancy.md); analysis engine
[strainshare](../README.md) (DOI [10.5281/zenodo.22275588](https://doi.org/10.5281/zenodo.22275588)).

---

## A. Significance

**The clinical problem.** Vaginal colonization by enteric pathogens and the dysbiosis of bacterial
vaginosis (BV) in pregnancy drive preterm birth, low birthweight, chorioamnionitis, and early-onset
neonatal sepsis. These outcomes are concentrated in low- and middle-income countries (LMICs), where
maternal rectovaginal Group B *Streptococcus* (GBS) colonization reaches **24.1%** across LMIC cohorts
([Africa pooled **18%**, with **47%** vertical transmission](https://www.sciencedirect.com/science/article/pii/S1201971226003371)),
an estimated **19.7 million** women carried rectovaginal GBS in 2020, and screening plus intrapartum
prophylaxis are least available. Multidrug-resistant Enterobacteriaceae compound the risk: **ESBL
*E. coli* rectal carriage in pregnant women reaches ~18.5%** in low-income settings
([e.g., Madagascar](https://journals.asm.org/doi/full/10.1128/aac.00029-15)) — a maternal reservoir that
seeds neonatal sepsis where its burden is highest.

**The reservoir and the route are established — but only cross-sectionally.** Six independent lines
converge on the gut/rectum seeding the vagina for the pathogens: (i) the recto-vaginal GBS swab is
standard of care because the bowel is the recognized source; (ii) the *same strain* is found at both
sites — an identical GBS genotype in the rectum and vagina of **18/19** colonized women, and ~85% of a
woman's matched vaginal/urinary *E. coli* isolates; (iii) **rectal carriage is the single strongest
predictor of vaginal colonization** (direction); (iv) after intrapartum antibiotics clear the vagina,
GBS persists in the bowel and **re-seeds** it; (v) an oral probiotic reduces *both* rectal and vaginal
GBS; (vi) the gut and vaginal communities converge (30–60% overlap) in late pregnancy. Every one of
these is culture/genotype-based and cross-sectional.

**The gap.** No study has resolved the *same strain moving rectum→vagina, in situ from metagenomes,
across the whole community, longitudinally over pregnancy* — nor linked that transfer to infection and to
water/sanitation/hygiene (WASH) and antenatal-care access. This gap is **decision-relevant**: whether the
right lever is deeper/earlier screening, WASH investment, or microbiome-directed prevention depends on
*which* organisms move, *when* in gestation, and *in whom*.

**Hygiene plausibly governs the transfer (Aim 4 rationale).** In a cluster-randomized cohort, water
source, latrine type, and rainfall were associated with detection of *enteric* bacteria in the vaginal
microbiome, and BV is consistently elevated where WASH is poor — direct, if preliminary, support that
limited hygiene increases gut→vaginal transfer. Disease risk is also **clone-specific**: GBS
**CC17/ST-17** (serotype III, HvgA+/rib, blood–brain-barrier-tropic) is over-represented in neonatal
invasive disease (~23% of infection vs ~2% of colonizing isolates), and *E. coli* **ST131** (a pandemic
gut-reservoir uropathogen; ~30% of maternal-neonatal ESBL isolates, with **ST1193** emerging) is a
persistent gut-and-vaginal colonizer. [Multi-country work already documents vaginal GBS and *E. coli*
carriage in resource-poor settings](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4727807/) — so the
analysis will type shared strains to clonal-complex/ST level, not species alone.

## B. Innovation

- **First in-situ, strain-resolved, longitudinal** demonstration of rectovaginal transmission in
  pregnancy, and the first to tie it to hygiene and access.
- **A standardized analytic layer.** strainshare converts inStrain output into contamination-aware
  shared-strain calls with a *within- vs between-person null*, a translocation-vs-contamination
  discriminator (community-similarity), a generalist filter, and longitudinal direction inference — a
  "VALENCIA-for-strains" standard so calls are comparable across sites and studies.
- **Reference breadth as a designed lever.** A broad vaginal+gut catalogue (GTDB + a vaginal collection
  such as VMGC) augmented with *per-sample assembled genomes (MAGs)* — our pilot showed a narrow
  reference is the dominant sensitivity limit.
- **Equity by design.** Enrollment across a WASH/access gradient makes the disparity itself a testable
  variable, in the populations least represented in microbiome cohorts.

## C. Approach

### C.0 Preliminary data (feasibility established)

- **The engine exists and is validated.** strainshare is installable, tested (CI on Py 3.9–3.12), and
  archived with a DOI. On a real 8-woman cervix↔vagina cohort it cleanly detected within-person sharing
  with a correct within- vs between-person null (positive control); on a 3-woman deep rectal+vaginal set
  it returned an honest, reference-controlled negative for the *commensals* (they are not gut-resident) —
  which is *why* this study targets pathogens/opportunists.
- **Benchmarks define the operating point.** Read-simulation benchmarks show the confident-popANI floor
  is **~10×** on the compared organism at both sites (not ~1×), and the 0.999 popANI threshold resolves
  strains to **~0.1% divergence**, species-agnostically. These set the depth and interpretation rules
  below.
- **Data landscape scoped.** No open dataset satisfies all five requirements (DNA shotgun + paired
  rectal+vaginal + pregnancy + low-resource + open); HMP provides an open, non-pregnant baseline
  (34 women, stool+vaginal) and MOMS-PI is the controlled comparator (see
  [dbGaP scoping](momspi-dbgap-scoping.md)).
- **Pathogen-targeted re-analysis (this work).** Re-scanning our Fijian (n=3) and HMP (7 complete women)
  profiles specifically for GBS, *E. coli*, and BV *Prevotella* shows the primary pathogens are **not
  vaginally colonized in these largely healthy/non-carrier women** — *E. coli* is gut/rectum-only where
  present, GBS is undetected, and the only cross-site co-detections (BV-*Prevotella* in one woman) are
  breadth-limited (not strain-callable). This is **not evidence against transmission**; it is a
  *not-evaluable* result that quantifies why the study must enroll a **colonized** low-resource cohort
  (vaginal GBS carriage ~24%, not ~0) rather than an unselected or healthy one.

### C.1 Overview & design

A **prospective longitudinal cohort of ~350 pregnant women** spanning a documented WASH/healthcare-access
gradient, with **paired rectal + vaginal shotgun metagenomes at 3–4 timepoints** (one per trimester and
at/near delivery). Deep sequencing + a broad reference + MAGs feed the strainshare pipeline to call
within-woman cross-site shared strains, infer direction, and associate them with infection outcomes and
access covariates. Design mirrors, and can adapt onto, the lab's in-hand 382 paired vaginal–rectal set.

### C.2 Sampling & cohort

- **Enrollment.** ~350 women in the first or early second trimester at partnering antenatal clinics
  across a WASH gradient (peri-urban/rural sub-Saharan Africa or South Asia; existing Kenya/Rwanda and
  South African pregnancy-microbiome cohorts are natural partners/comparators). Enrollment is inflated
  ~1.5–2× over the evaluable target to absorb colonization prevalence and depth attrition.
- **Specimens.** Self- or clinician-collected **rectal swab + vaginal swab** at each visit, into
  DNA/RNA-stabilizing buffer; aliquot for culture (GBS/*E. coli*). Store at −80 °C.
- **Covariates (Aim 4).** Access to clean water, sanitation type, bathing/washing frequency, antenatal
  visit count, antibiotic exposure, GBS/BV status, socioeconomic indices, gestational age, parity,
  sexual activity, and mode/timing of delivery. Captured by standardized questionnaire + clinical record.
- **Contamination controls.** Per-plate negative (buffer) and positive (mock community) controls; plate
  layout recorded so cross-well/cross-swab contamination can be flagged and removed.

### C.3 Wet-lab

- **Extraction.** A single validated protocol across body sites (kit chosen for even lysis of
  Gram-positives incl. GBS and *Lactobacillus*); reagent-blank controls.
- **Libraries & depth.** Illumina shotgun, **~20–40 M read pairs/sample** — deeper on low-biomass
  vaginal samples. Because candidate pathogens are often low-abundance at one site, **culture- or
  target-enrichment for GBS and *E. coli*** (selective broth pre-enrichment, or hybrid-capture) is used
  to lift them above the ~10× strain-calling floor without distorting the community estimate (a paired
  un-enriched library preserves relative abundance for the community-similarity discriminator).
- **Host removal.** Map-and-remove human reads; retain read-pairing metadata where possible (host
  removal desyncs mates — the pipeline maps unpaired with `--pairing_filter all_reads` when it does).
- **Reference & MAGs.** Build a broad vaginal+gut reference (GTDB representatives + VMGC + multiple
  *Gardnerella* genomospecies) and assemble **per-sample MAGs** for organisms absent from the catalogue;
  dRep-dereplicate; index for competitive mapping with a scaffold-to-bin map.

### C.4 Bioinformatics

1. **QC/host-removal** → trimmed, human-screened reads.
2. **Per-sample profiling** → `inStrain profile` against the broad reference (+ MAGs), `--database_mode`.
3. **Coverage/evaluability gating** — an organism below the coverage/breadth floor at *either* site of a
   woman is labeled **not-evaluable**, never "not shared" (the integrity rule, enforced in code).
4. **Cross-site comparison** → `inStrain compare`; **strainshare analyze `--site-pair rectum,vagina`** →
   shared-strain calls at **popANI ≥ 0.999, breadth ≥ 0.5**, with the within- vs between-person null.
5. **Contamination discrimination** — shared strain + *dissimilar* community ⇒ candidate translocation;
   + *similar* community / same-plate ⇒ down-ranked as contamination (CroCoDeEL + community proxy).
6. **Direction (Aim 2)** — longitudinal acquisition timing (rectum-before-vagina ⇒ rectum→vagina);
   ambiguous timing ⇒ `direction_unresolved`, never guessed.
7. **Generalist filter** — drop globally shared strains that inflate false positives.

### C.5 Statistics

- **Power (binding endpoint = Aim 4).** Two-proportion comparison of cross-site sharing across access
  strata (80% power, α = 0.05, two-sided): ~80 women for a 30-pt difference, ~120 for 25, ~180 for 20,
  ~330 for 15. Estimating the transmission proportion alone to ±10% needs ~90 evaluable women; ±8%, ~145.
  The ~350-woman cohort yields ~180–220 evaluable women.
- **Models.** Aim 1: proportion with 95% CI. Aim 2: mixed-effects / survival models for acquisition
  timing and persistence, taxon random effects. Aim 3: logistic/mixed models linking sharing to BV,
  GBS status, symptomatic infection, and preterm birth, adjusted for confounders. Aim 4: logistic/mixed
  models of sharing vs WASH/access covariates.
- **Multiplicity & confounding.** Benjamini–Hochberg FDR across organisms; pre-registered primary
  organisms (GBS, *E. coli*); sensitivity analyses for shared-environment and sexual-activity confounding
  (the within- vs between-person null is the primary guard).

### Aim-by-aim

- **Aim 1 — detection & rate.** Call within-woman rectum↔vagina shared strains for the primary organisms;
  report the transmission proportion. *Pitfall:* low abundance at one site → not-evaluable; *mitigation:*
  depth + enrichment + MAGs. *Expected:* a ranked, contamination-controlled shared-strain list.
- **Aim 2 — direction & ranking.** From longitudinal timing, establish rectum-before-vagina acquisition;
  rank taxa by transmission rate, directionality, persistence; **type GBS/*E. coli* shared strains to
  clonal complex / ST** (e.g., CC17, ST131) so disease-relevant clones are distinguished. *Pitfall:* both
  sites colonized at baseline → direction unresolvable; *mitigation:* early first visit, ≥3 timepoints,
  report `direction_unresolved` honestly.
- **Aim 3 — outcomes.** Associate sharing with infection/dysbiosis and preterm birth. *Pitfall:*
  outcome rarity → underpowered subgroups; *mitigation:* composite adverse-outcome endpoint, pre-specified.
- **Aim 4 — risk factors.** Model sharing vs WASH/access. *Pitfall:* collinear socioeconomic variables;
  *mitigation:* pre-specified covariate set, regularized models.

### C.6 Rigor & reproducibility

Standardized thresholds versioned in the strainshare spec; contamination controls per plate;
pre-registered primary organisms and endpoints; all code open-source and DOI-archived; the
not-evaluable/negative distinction enforced in code so depth-limited results are never reported as
biological absence.

### C.7 Timeline (see [budget & timeline](budget-timeline.md))

Y1 protocol/IRB/site setup + reference build; Y1–Y3 enrollment & longitudinal sampling; Y2–Y4 sequencing
& analysis; Y4–Y5 outcome association, risk-factor models, dissemination.

### C.8 Pitfalls & alternatives (summary)

| Risk | Mitigation / alternative |
|---|---|
| Target pathogen too sparse to strain-type | Culture/target enrichment; deeper sequencing; MAGs |
| Reference too narrow (our pilot's lesson) | Broad GTDB+VMGC catalogue + per-sample MAGs |
| Direction unresolvable (both sites colonized early) | Early first visit; ≥3 timepoints; `direction_unresolved` |
| Cross-sample contamination mimics sharing | Per-plate controls + community-similarity discriminator |
| Enrollment/retention in low-resource settings | Local partnerships; simple self-collection; ~1.5–2× inflation |
| No open pilot meets all criteria | HMP baseline now; MOMS-PI via dbGaP; then the prospective cohort |
