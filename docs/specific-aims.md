# Specific Aims

**Rectum-to-vagina bacterial transmission in pregnancy: a strain-resolved, longitudinal study in low-resource settings**

Bacterial vaginosis and vaginal colonization by enteric pathogens in pregnancy drive preterm birth, low
birthweight, and neonatal infection — outcomes that fall hardest on low- and middle-income settings, where
**24.1%** of pregnant women carry rectovaginal Group B *Streptococcus* (GBS) and screening and treatment are
least available. The gastrointestinal tract is the recognized reservoir for these organisms, and their
movement to the vagina is supported by several independent lines of evidence: the **same GBS genotype is
found in the rectum and vagina of 18 of 19 colonized women**; ~85% of a woman's paired vaginal and urinary
*E. coli* isolates are one strain; **rectal carriage is the single strongest predictor of vaginal
colonization**; and after intrapartum antibiotics clear the vagina, the organism persists in the bowel and
re-seeds it. Yet every one of these observations is **cross-sectional and culture-based**. No study has
resolved the *same strain moving rectum→vagina, in situ from metagenomes, across the whole microbial
community, over the course of pregnancy* — and none has asked whether limited access to water, sanitation,
and hygiene (WASH) and antenatal care makes that transfer more likely. **This gap is decision-relevant:** the
right point of intervention — screening depth, WASH, microbiome-directed prevention — depends on *which*
organisms move, *when*, and *in whom*.

**Long-term goal & objective.** Our long-term goal is to reduce maternal and neonatal infection arising from
rectovaginal transmission in low-resource pregnancy. The **objective of this proposal** is to define, at
strain resolution and longitudinally, which bacteria move from the rectum to the vagina during pregnancy,
whether that movement contributes to vaginal infection, and how hygiene and healthcare access govern it.

**Central hypothesis.** In pregnancy, specific rectal bacteria (GBS, *E. coli*, BV-associated taxa) seed the
vagina as the *same strain*, contributing to colonization and infection; transfer is more frequent under
limited hygiene and healthcare access.

**Approach.** We will enroll **~350 pregnant women** spanning a WASH/access gradient and collect **paired
rectal + vaginal shotgun metagenomes at 3–4 timepoints** (per trimester and at/near delivery). Samples are
analyzed with **strainshare** — our published, DOI-archived pipeline (contamination-aware shared-strain calls
at inStrain popANI ≥ 0.999 on ≥ 50% breadth, a within- vs between-person null, a generalist filter, and
longitudinal direction inference) — against a broad vaginal + gut reference augmented with per-sample
assembled genomes. Power is set by the hygiene-association arm (two-proportion comparison, 80% power,
α = 0.05): this cohort yields ~180–220 evaluable women, sufficient to estimate the transmission proportion to
± 8–10% and to detect a 20–25 percentage-point difference in cross-site sharing across access strata.

- **Aim 1 — Does it happen, and how often?** Detect within-woman rectum↔vagina shared strains for the target
  pathogens, contamination-controlled, and estimate the transmission proportion. *Deliverable:* a ranked,
  contamination-controlled list of organisms that share a strain across sites within a woman.

- **Aim 2 — Which direction, which organisms?** Use the longitudinal design to establish rectum-before-vagina
  acquisition and rank taxa by transmission rate, directionality, and persistence. *Deliverable:* directional,
  time-resolved transmission calls (with `direction_unresolved` where timing is ambiguous — never inferred).

- **Aim 3 — Does it cause disease?** Associate cross-site strain sharing with vaginal infection/dysbiosis
  (BV by Nugent/Amsel, GBS status, symptomatic infection) and with preterm birth. *Deliverable:* effect
  estimates linking sharing to adverse outcomes.

- **Aim 4 — Who is at risk, and what helps?** Model transmission against WASH and antenatal-care covariates to
  identify the women at greatest risk and the actionable points for prevention. *Deliverable:* risk-factor
  models and prevention targets (screening depth, WASH, microbiome-directed approaches).

**Innovation & impact.** This will be the **first in-situ, strain-resolved, longitudinal demonstration** of
rectovaginal transmission in pregnancy, and the first to tie it to hygiene and access. It targets the
organisms that already have prevention levers — GBS intrapartum antibiotic prophylaxis, WASH interventions,
and an oral probiotic shown in a randomized trial to reduce *both rectal and vaginal* GBS — so its outputs are
directly actionable for the populations bearing the greatest burden. The study **generates evidence; clinical
decisions remain with providers.**

---

*This one-page Aims summary condenses the full proposal ([study-rectovaginal-pregnancy.md](study-rectovaginal-pregnancy.md))
and its evidence base ([designed brief](rectovaginal-route.html)). Analysis engine:
[strainshare](../README.md), DOI [10.5281/zenodo.22275588](https://doi.org/10.5281/zenodo.22275588).*
