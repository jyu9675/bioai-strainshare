# MOMS-PI (dbGaP phs001523) — data-access scoping

*How to obtain, and whether to rely on, the MOMS-PI shotgun data as a validation/comparator cohort for
the [rectovaginal-transmission study](study-rectovaginal-pregnancy.md). Verified 2026-09.*

## What MOMS-PI is

The **Multi-Omic Microbiome Study – Pregnancy Initiative** (MOMS-PI), Virginia Commonwealth University
Vaginal Microbiome Consortium with GAPPS; PI **Jennifer Fettweis**. dbGaP **phs001523.v1.p1**.

- **Scale:** ~1,527 pregnancies, ~206,437 specimens across ~7,000 visits; a deeply-profiled subset
  (~597 pregnancies / ~12,039 samples) drove the flagship analysis (Fettweis et al., *Nat. Med.* 2019).
- **Body sites (maternal):** ten, **including vaginal, cervical, buccal, and *rectal* mucosa**, plus
  blood, urine, skin, nares — so *rectal specimens exist*.
- **Omics:** 16S rRNA, **shotgun metagenome (WGS)**, metatranscriptome, metabolomics/lipidomics,
  immunoproteomics/cytokines.
- **Population:** US (Virginia + GAPPS sites) — **well-resourced**, predominantly a high-risk /
  racially-diverse US cohort. *Not* a low-resource setting.

## The one thing to confirm *before* applying

16S was run broadly across body sites, but the **deep omics (WGS/metatranscriptome) in the flagship work
were vaginal-focused.** The study therefore has rectal *specimens* and WGS *capability*, but it is **not
yet confirmed that paired rectal WGS exists at usable scale and depth** for the same women across
timepoints — which is exactly what this study needs.

**Confirm via, in order:**
1. The **phs001523 data dictionary + "Molecular Data" / sample-count tables** on the dbGaP study page
   (public metadata, no access needed): look for `analyte`/`body site` × `WGS` cross-tabs showing rectal
   metagenomes and per-subject timepoint counts.
2. The **VMC / MOMS-PI portal** (vmc.vcu.edu/momspi) manifest.
3. A **direct inquiry to the study contact** (draft below) — fastest definitive answer.

If rectal WGS is thin or absent, MOMS-PI still serves as a **vaginal-side validation / well-resourced
comparator** (does the healthy US baseline differ from the low-resource cohort?), not the paired-transfer
cohort — and the prospective cohort remains the primary vehicle.

## Access model (dbGaP controlled-access)

MOMS-PI's individual-level omics are **controlled-access**. The path:

1. **eRA Commons account** for the PI (and an **NIH login**).
2. **Institutional Signing Official (SO)** registered in dbGaP — the SO co-signs the request.
3. **Data Access Request (DAR)** in the dbGaP Authorized Access system, naming phs001523, a written
   **research use statement**, and the **cloud-use** intention if analyzing in a cloud environment.
4. **Consent-group match** — request only the consent group(s) your use qualifies for (e.g.,
   general research use vs disease-specific); the study page lists the codes.
5. **Data Use Certification (DUC/DUA)** agreeing to the terms (no re-identification, approved-users only,
   secure storage, annual renewal, publication/acknowledgment rules).
6. **Local IRB** determination — typically "not human subjects" / exempt for de-identified controlled
   data, but obtain the written determination your SO requires.
7. **Approval → download** via dbGaP/SRA with an NIH-issued repository key (prefetch/​dbGaP-aware SRA
   tools), or analyze in an approved cloud workspace.

**Typical wall-clock:** account + SO registration (days–weeks) → DAR review (a few weeks) → download.
Budget ~4–8 weeks from a clean submission.

## What to request / extract (if it clears the pre-check)

- **Molecular:** rectal + vaginal **WGS** for the same women with **≥2 timepoints** (for direction),
  raw reads (FASTQ) for strainshare.
- **Phenotype file:** visit dates / gestational age (for direction & timing), GBS/BV status, infection
  and **preterm-birth outcomes**, demographics, antibiotic exposure — mapped to sample IDs.
- **Run** through the same pipeline (broad reference + MAGs → inStrain → strainshare `--site-pair
  rectum,vagina`) as the prospective cohort, so results are directly comparable.

## Checklist

- [ ] Read phs001523 data dictionary; cross-tab rectal × WGS × timepoints (public)
- [ ] Confirm paired rectal WGS scale/depth (portal or study contact)
- [ ] PI eRA Commons + NIH login active
- [ ] Identify institutional Signing Official; confirm dbGaP registration
- [ ] Draft research-use statement + cloud-use plan
- [ ] Identify eligible consent group(s)
- [ ] Local IRB determination letter
- [ ] Submit DAR; track review; sign DUC on approval

## Draft inquiry email (to the MOMS-PI / VMC study contact)

> **Subject:** phs001523 (MOMS-PI) — availability of paired rectal + vaginal shotgun (WGS) data
>
> Dear Dr. Fettweis / MOMS-PI team,
>
> I am scoping a strain-resolved study of rectum→vagina bacterial transmission in pregnancy and am
> evaluating MOMS-PI (phs001523) as a comparator cohort. Before initiating a dbGaP Data Access Request, I
> would be grateful to confirm: (1) for how many participants **shotgun metagenome (WGS)** data exist for
> **both rectal and vaginal** specimens from the **same women**, ideally at **≥2 timepoints**; (2) the
> typical sequencing depth of the rectal WGS libraries; and (3) which consent group(s) cover secondary
> analysis of transmission between body sites. We use an open, contamination-aware strain-sharing
> pipeline (inStrain + strainshare) and would cite MOMS-PI per your data-use terms.
>
> Thank you — [name, institution, eRA Commons ID]

## Honest bottom line

MOMS-PI is the **best-designed pregnancy cohort with rectal specimens and WGS capability**, but it is a
**well-resourced US** population and its **paired-rectal-WGS content is unconfirmed**. Treat it as a
validation/comparator to pursue **in parallel** with — not instead of — the prospective low-resource
cohort that the [Aims](specific-aims.md) require.
