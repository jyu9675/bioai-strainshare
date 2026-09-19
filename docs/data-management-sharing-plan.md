# Data Management & Sharing Plan

*For the [rectovaginal-transmission study](study-rectovaginal-pregnancy.md). Structured to the NIH 2023
Data Management and Sharing (DMS) Policy's six elements; adaptable to Gates/Wellcome open-access terms.*

## Element 1 — Data type

- **Raw sequence** — paired rectal + vaginal shotgun metagenomes (FASTQ), ~2,450 libraries, plus
  target-enrichment libraries and per-plate controls.
- **Derived data** — per-sample inStrain profiles; cross-site `genomeWide_compare` tables; strainshare
  call sets (shared strains, within/between null, contamination flags, direction); per-sample MAGs and
  the broad reference catalogue.
- **Phenotype/metadata** — MIxS-compliant sample metadata; clinical/outcome variables (GBS/BV status,
  infection, gestational age, preterm birth); WASH/access covariates; de-identified with a linkage key
  held only by the coordinating site.
- **Estimated volume** — raw metagenomes dominate (~tens of TB); derived tables and code are small.

## Element 2 — Related tools, software & code

Analysis uses **strainshare** (open-source, MIT, tested, CI) and inStrain/bowtie2/samtools — all open.
strainshare and all study-specific pipeline code are versioned on GitHub and archived at Zenodo with a
DOI ([10.5281/zenodo.22275588](https://doi.org/10.5281/zenodo.22275588)); the exact analysis version is
cited in publications so results are reproducible.

## Element 3 — Standards

FASTQ for reads; MIxS/genomic-metadata standards for sample descriptors; GTDB taxonomy; the versioned
**strainshare spec** for thresholds (popANI ≥ 0.999, breadth ≥ 0.5, ~10× floor) so calls are comparable
across studies. Controlled vocabularies for clinical and WASH variables (e.g., WHO/JMP WASH indicators).

## Element 4 — Preservation, access & timelines

| Data | Repository | Access | Timeline |
|---|---|---|---|
| Raw human metagenomes + phenotypes | **dbGaP / SRA (controlled-access)** | Approved users via DAR/DUC | At/near publication, per policy |
| De-identified derived tables (strain calls, community matrices) | Open repository (e.g., Zenodo/figshare) | Open | At publication |
| MAGs + reference catalogue | ENA/NCBI + Zenodo | Open | At publication |
| Code & pipeline | GitHub + Zenodo (DOI) | Open (MIT) | On release / at submission |

Raw human-subjects sequence is **controlled-access** (re-identification risk); derived, non-identifiable
products are **open**. Data retained ≥ the funder-required period (NIH ≥ 3 yr post-award; longer in the
repository of record).

## Element 5 — Access, distribution & reuse considerations

- **Consent** language will permit broad secondary research and controlled data sharing; consent-group
  codes recorded for dbGaP.
- **Human data** shared only via controlled-access with a Data Use Agreement (no re-identification,
  approved users, secure storage).
- **Vulnerable population** protections: because participants are pregnant women in low-resource
  settings, sharing follows local IRB terms and any in-country data-sovereignty requirements; community
  and local-investigator engagement is built in (see [letters of support](letters-of-support.md)).

## Element 6 — Oversight

The PI and a designated data manager monitor compliance; the coordinating site holds the linkage key;
controlled-access requests are reviewed by the relevant NIH Data Access Committee. Annual review of
adherence, with corrective action logged. All sharing is clinician-independent — the plan governs data,
not care.
