# Budget & timeline sketch — ~350-woman cohort

> **Order-of-magnitude planning figures, not a costed budget.** Real numbers require institutional
> salary rates, a core-facility sequencing quote, and in-country site costs. Ranges below are for
> feasibility scoping and a modular-grant first pass. Companion to the
> [Research Strategy](research-strategy.md) and [Specific Aims](specific-aims.md).

## Sample & sequencing math

| Quantity | Value |
|---|---|
| Women enrolled | ~350 (≥2× the ~180 evaluable target, absorbing colonization + depth attrition) |
| Timepoints | 3–4 (per trimester + at/near delivery) |
| Sites per visit | 2 (rectal + vaginal) |
| **Shotgun libraries** | ~350 × 3.5 × 2 ≈ **~2,450** |
| Depth | ~20–40 M read pairs/sample (deeper for low-biomass vaginal) |
| Target-enrichment libraries (GBS/*E. coli*, colonized subset) | ~400–800 add-on |
| Controls | per-plate negative + mock-community positive |

## Timeline (5 years)

| Phase | Y1 | Y2 | Y3 | Y4 | Y5 |
|---|:--:|:--:|:--:|:--:|:--:|
| Protocol, IRB (US + in-country), site MOUs | ██ | | | | |
| Reference + MAG catalogue build; pipeline hardening | ██ | ▓ | | | |
| Enrollment & longitudinal sampling | ▓ | ██ | ██ | ▓ | |
| Extraction, libraries, sequencing | | ██ | ██ | ▓ | |
| Bioinformatics: profiling, strain calls, direction | | ▓ | ██ | ██ | ▓ |
| Aim 3/4: outcome + WASH association models | | | ▓ | ██ | ██ |
| MOMS-PI comparator (parallel, if access clears) | | ▓ | ▓ | ▓ | |
| Dissemination, data/code release, DAC deposit | | | | ▓ | ██ |

`██` primary effort · `▓` ramp/overlap. Enrollment leads sequencing; direction analysis needs ≥2
timepoints per woman, so cross-site calls mature in Y3–Y4.

## Budget by category (5-year, direct costs — rough ranges)

| Category | What it covers | 5-yr direct (order of magnitude) |
|---|---|---|
| **Personnel** | PI (10–20%), co-I(s), project coordinator, 1–2 wet-lab techs, bioinformatician, biostatistician (25%), in-country site coordinators/field staff | **$1.5–2.3 M** |
| **Sequencing & wet-lab** | extraction, ~2,450 shotgun libraries + enrichment add-ons, NovaSeq, QC | **$0.7–0.9 M** |
| **Participant & site** | enrollment, collection kits, stabilizing buffer, participant incentives, clinic partnership/infrastructure | **$0.15–0.30 M** |
| **Compute & storage** | assembly/MAGs, cloud or cluster compute, long-term storage of ~2,450 deep metagenomes | **$0.05–0.12 M** |
| **Other** | shipping/cold-chain, publication/open-access, travel, DAC/data-deposit | **$0.08–0.15 M** |
| **Total direct** | | **≈ $2.5–3.7 M** |
| **+ Indirect (F&A, ~50–65%)** | | **total ≈ $4–6 M** |

This is **program-scale** (a multi-year R01-plus, U01, or multi-PI/foundation mechanism). A leaner
**pilot/R21** first phase — one site, ~80–120 women, 2–3 timepoints, GBS/*E. coli*-focused — would run
**~$0.4–0.7 M direct** and de-risk enrollment, the enrichment protocol, and the transmission-rate
estimate before the full cohort.

## Cost levers & de-risking

- **Reuse the in-hand 382 paired vaginal–rectal set** where consent allows — could offset a large share
  of new sequencing and accelerate Aims 1–2.
- **MOMS-PI in parallel** (see [dbGaP scoping](momspi-dbgap-scoping.md)) — a controlled but *free*
  comparator; cost is effort, not sequencing.
- **Target-enrichment only for the colonized subset** keeps per-sample cost down while lifting the
  pathogens above the ~10× strain-calling floor.
- **Analyze in-region / in-cloud** next to the data to cut egress and turnaround (the HMP scoping showed
  in-cloud analysis is the practical route for large metagenome sets).

## Assumptions & caveats

Figures assume Illumina shotgun at a shared core facility, de-identified analysis, and partnership with
existing antenatal cohorts (not standing up field infrastructure from zero). They exclude clinical care
costs (management of any infection found is standard care, clinician-led). Currency USD, 2026. Replace
every range with institutional rates and a facility quote before submission.
