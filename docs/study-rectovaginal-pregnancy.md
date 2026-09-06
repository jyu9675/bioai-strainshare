# Study Design — Rectal-to-Vaginal Bacterial Transmission in Pregnancy, in Low-Resource Settings

**Aim in one line:** Determine, at the strain level, whether bacteria move from the rectum to the
vagina during pregnancy and drive vaginal colonization/infection — and whether limited access to
water, hygiene, and healthcare increases that risk.

*Analysis engine: the [strainshare](../README.md) pipeline (contamination-aware shared-strain calls,
within-vs-between-person null, longitudinal direction inference). Motivated by a lived clinical case
and grounded in established GBS biology.*

---

## 1. Background & significance

**The rectal reservoir is established biology — for pathogens, not commensals.**
- The gastrointestinal tract is the recognized reservoir and source of vaginal **Group B *Streptococcus*
  (GBS, *Streptococcus agalactiae*)** colonization; GBS resides mainly in the lower digestive/rectal
  tract and seeds the vagina. This is *why* pregnant people receive a **recto-vaginal** GBS swab at
  ~36 weeks and intrapartum antibiotics if positive. ~**19.7 million** pregnant women carried
  rectovaginal GBS in 2020. [1]
- **_E. coli_** and other Enterobacteriaceae follow the same rectum→vagina/urethra route (a major driver
  of UTIs and neonatal sepsis). **BV-associated taxa** (*Gardnerella*, *Prevotella*, *Sneathia*,
  *Atopobium/Fannyhessea*) and *Candida* are also implicated in cross-site movement.
- **What is NOT a gut reservoir:** the dominant vaginal *commensals* (*Lactobacillus*, and vaginal
  *Gardnerella* genomospecies). In our own strain-level pilot (3 women, deep rectal+vaginal, 33-genome
  reference), these were deeply covered vaginally (up to 185×) yet **absent from the rectum (0×)** —
  a clean negative. **So the transmission question must target pathogens/opportunists, not commensals.**

**The gap.** Rectovaginal GBS/*E. coli* colonization is well documented by *culture/PCR*, and *isolate*
whole-genome sequencing exists (incl. low-resource cohorts in Ethiopia, Nigeria, Sri Lanka [2]). But
**strain-resolved, longitudinal, paired rectal+vaginal metagenomics that demonstrates the same strain
moving rectum→vagina *within a woman over pregnancy* — and links it to infection and to hygiene/access —
is largely missing**, especially in low-resource settings.

**Why low-resource settings matter.** Limited clean water, bathing facilities, and antenatal care
plausibly increase rectal→vaginal transfer and reduce timely screening/treatment — yet these are the
populations least represented in microbiome cohorts. This is both a scientific and an equity gap.

## 2. Hypothesis & specific aims

**Hypothesis:** In pregnancy, specific rectal bacteria (GBS, *E. coli*, BV-associated taxa) seed the
vagina as the *same strain*, contributing to vaginal colonization/infection; transfer is more frequent
under limited hygiene/healthcare access.

- **Aim 1 — Does it happen?** Detect within-woman rectum↔vagina **shared strains** (inStrain popANI
  ≥ 0.999 on ≥50% breadth), contamination-controlled, focused on GBS/*E. coli*/BV taxa.
- **Aim 2 — Which direction & which bugs?** Use **longitudinal** sampling to infer direction
  (rectum-first → vagina-later) and rank taxa by transmission rate, directionality, and persistence.
- **Aim 3 — Does it cause disease?** Associate cross-site strain sharing with vaginal
  infection/dysbiosis outcomes (BV, GBS colonization status, symptomatic infection, preterm birth).
- **Aim 4 — Who is at risk & what helps?** Test association with **hygiene/access covariates** (water,
  sanitation, bathing frequency, antenatal-care access) and identify actionable prevention points.

## 3. Study population

- **Pregnant women in low-resource settings** — e.g., peri-urban/rural sub-Saharan Africa or South Asia,
  with documented WASH (water/sanitation/hygiene) and healthcare-access variation. (Existing consortia to
  partner with or draw comparators from: South African / Nigerian / Kenyan pregnancy cohorts — see §7.)
- **Covariates to capture:** access to clean water, bathing/washing frequency, sanitation type, antenatal
  visits, antibiotic use, GBS/BV status, socioeconomic indicators, gestational age, parity.

## 4. Design & sampling

- **Longitudinal, paired within-woman:** rectal swab + vaginal swab at each visit across pregnancy
  (e.g., per trimester + at/near delivery). Longitudinal sampling is essential for *direction* and
  *persistence*, and for separating transmission from shared-environment confounding.
- **Deep shotgun metagenomics** (target ≥10× breadth on candidate shared taxa — from our benchmarks the
  usable strain-call floor is ~10× on the *compared* organism; low-biomass vaginal samples need depth).
- **Contamination controls:** negative controls per plate + plate layout recorded, so cross-sample /
  cross-swab contamination can be flagged (CroCoDeEL + strainshare's community-similarity check) and
  removed — critical, because whole-community contamination mimics sharing.
- **Reference:** a broad vaginal+gut catalog (GTDB + a vaginal collection such as VMGC; per-sample MAGs
  for organisms absent from the catalog) — the narrow reference is what limits sensitivity (see §9).

## 5. Target organisms (and what to ignore)

| Priority | Organisms | Why |
|---|---|---|
| **Primary** | GBS (*S. agalactiae*), *E. coli* / Enterobacteriaceae | Established rectovaginal transmitters; direct neonatal/maternal disease relevance |
| **Secondary** | BV-associated: *Gardnerella* spp., *Prevotella bivia/amnii/disiens*, *Sneathia*, *Fannyhessea*, *Atopobium* | Cause vaginal dysbiosis/infection; several co-occur across sites |
| **Also** | *Candida*, enterococci | Clinically relevant cross-site colonizers |
| **Not the target** | *Lactobacillus*, vaginal commensal *Gardnerella* | Not a gut reservoir (shown in our pilot) — including them dilutes the signal |

## 6. Analysis plan (strainshare pipeline)

1. **Per-sample profiling** → inStrain profiles against the broad reference (`--pairing_filter all_reads`
   for host-removed data).
2. **Shared-strain calls (M1):** `strainshare analyze --site-pair rectum,vagina` → popANI ≥ 0.999,
   breadth ≥ 0.5, with the **within-vs-between-person null** (a rectal↔vaginal strain that is shared
   *within* women but not *between* unrelated women is the real signal).
3. **Contamination discrimination (M2):** shared strain + *dissimilar* community = translocation;
   + *similar* community / same-plate = contamination — down-ranked.
4. **Direction (M4):** from longitudinal acquisition timing (rectum-before-vagina ⇒ rectum→vagina);
   cross-sectional visits reported `direction_unresolved`.
5. **Generalist filter (M5):** drop globally-shared strains that inflate false positives.
6. **Ranked transmission table** (Aim 2): taxon × transmission rate × direction × persistence.
7. **Outcome association (Aim 3):** shared-strain status vs BV/GBS/infection/preterm-birth.
8. **Risk-factor models (Aim 4):** transmission vs WASH/access covariates (logistic/mixed models).

## 7. Available public data — honest map (verified 2026-09)

The five requirements for a strain-level test are: **(i) DNA shotgun** (not 16S/RNA), **(ii) paired
rectal + vaginal from the same women**, **(iii) pregnancy**, **(iv) low-resource setting**, **(v) open
access**. We checked the leading candidates against all five:

| Dataset | (i) DNA shotgun | (ii) rectal+vaginal | (iii) pregnancy | (iv) low-resource | (v) open | Verdict |
|---|:--:|:--:|:--:|:--:|:--:|---|
| **PRJNA798597** (South Africa) | ❌ RNA-Seq | ✅ (R/V/O) | ✅ | ✅ | ✅ | **Not usable for strain** — metatranscriptomic (60 runs, `RNA-Seq`); right cohort, wrong molecule. Could show *active* taxa co-occurrence only. |
| **MOMS-PI** (phs001523) | ✅ | ⚠️ WGS looks **vaginal-only** | ✅ | ❌ US | ❌ dbGaP | Best design, but shotgun is **controlled** (eRA Commons+IRB+DUA) and appears vaginal-swab-focused — **confirm rectal WGS before applying**. Open portion is 16S/cytokines only. |
| **PRJNA826539** (Fijian, n=10) | ✅ | ✅ | ❓ not confirmed | ✅ Pacific | ✅ | **Only open DNA rectal+vaginal set** — but *E. coli* was rectum-only and GBS undetected in the 3 women tested, so it doesn't show pathogen transmission either. |
| **PRJDB10581** (pregnancy R/V/O pilot) | ⚠️ likely 16S | ✅ | ✅ | ❌ Japan | ✅ | verify amplicon vs shotgun; small pilot. |
| **GBS isolate WGS** (Ethiopia/Nigeria/Sri Lanka) [2] | ✅ (isolates) | ❌ | ✅ | ✅ | ✅ | *Cultured isolates*, not paired metagenomes — valuable as **GBS strain reference/context**, not for in-situ transmission. |

**Verified bottom line:** **no open dataset satisfies all five criteria** — the pieces are split across
molecule, sites, population, and access. This is not a dead end; it is the **justification for the
proposed study**: the definitive cohort must be **prospectively collected** (a low-resource pregnancy
cohort with paired rectal+vaginal *DNA* shotgun, longitudinal) — or accessed via a **dbGaP application to
MOMS-PI** (after confirming it contains paired rectal WGS). The Kwon Lab's 382-sample paired
vaginal–rectal set is the closest deep, in-hand vehicle to adapt the pregnancy/low-resource arms onto.

## 8. Expected outcomes & translational value

- **Aim 1–2:** a ranked, contamination-controlled list of bacteria that demonstrably move rectum→vagina
  in pregnancy, with directionality and persistence.
- **Aim 3:** whether cross-site sharing predicts vaginal infection/dysbiosis/preterm birth.
- **Aim 4:** which women (by hygiene/access) are at higher risk — evidence for **targeted prevention**.
- **Prevention/treatment (informs clinicians & policy — not prescribing):** the study's outputs feed
  established clinical levers — GBS **intrapartum antibiotic prophylaxis** is already standard of care;
  **WASH interventions** (clean water, sanitation) are candidate structural preventions in low-resource
  settings; microbiome-directed approaches (e.g. *Lactobacillus* live biotherapeutics — the Kwon Lab's
  own area) are research-stage. **All treatment decisions require a clinician; the study generates the
  evidence, not the prescription.**

## 9. Limitations & feasibility

- **Reference breadth** is the key sensitivity lever (our pilot showed a narrow reference throttles
  detection); a comprehensive vaginal+gut catalog + MAGs is required.
- **Depth**: candidate taxa are often low-abundance at one site → need deep sequencing (or targeted
  enrichment/culture for GBS/*E. coli*).
- **Confounding**: sexual activity and shared environment can mimic rectal seeding; longitudinal design +
  the between-person null + contamination checks mitigate this.
- **Ethics**: IRB approval, informed consent, and clinician-led management of any infection found;
  particular care with vulnerable, low-resource participants.

## References
1. Rectovaginal GBS: gut reservoir & burden — Frontiers in Microbiology 2026, https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2026.1871541/full ; recto-vaginal GBS in low-resource pregnancy — Ethiopia, https://pmc.ncbi.nlm.nih.gov/articles/PMC10642950/
2. GBS WGS from colonized pregnant women, Nigeria — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8382210/ ; Sri Lanka — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9029214/
3. Gut/vaginal/oral microbiome in South African pregnancy — https://www.frontiersin.org/journals/global-womens-health/articles/10.3389/fgwh.2022.810673/full ; racioethnic diversity in the pregnancy vaginal microbiome (MOMS-PI) — https://www.nature.com/articles/s41591-019-0465-8
