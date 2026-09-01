# Table 1 — strainshare vs existing strain-sharing / transmission tools

*Draft for Study D. Every threshold below is from primary sources (cited); the strainshare
row is the versioned standard in [`../scripts/strainshare_standard.yaml`](../scripts/strainshare_standard.yaml),
with the resolution limit measured empirically in this repo (`example/benchmark/`).*

## The landscape (methods as rows)

| Method | Shared-strain metric & default threshold | Overlap / breadth requirement | Low-coverage capability | Transmission direction? | Built-in confound controls | Fixed, cross-study-comparable thresholds? |
|---|---|---|---|---|---|---|
| **inStrain** | popANI (population-aware) ≥ **99.999%** ᵃ | `percent_compared` ≥ **50%** ᵃ | needs >6× for full breadth; empirically ~10× for a confident call ᵃ⋅ᵉ | **No** ᵃ | none built in (user must add) | partial — threshold documented but study-chosen ᵃ |
| **StrainPhlAn** | marker-gene consensus distance (no fixed sharing cutoff) | markers cover only **~1.4%** of genome ᵇ | cannot resolve close strains even at 10× ᵇ | **No** | none | no |
| **StrainGE** | k-mer / reference-based ANI | markers cover **~74%** of genome ᵇ | **detects sharing down to ~0.5×** ᵇ (0.1× claim unverified); assembly step weak on low-biomass ᵇ | **No** | none | no |
| **SameStr** | Maximum-Variant-profile Similarity ≥ **99.9%** | ≥ **5 kb** overlapping alignment ᶜ | marker/SNV-based | **No** | none | **yes** (fixed defaults) ᶜ |
| **TRACS** | multi-kingdom shared-SNV distance | per-species | designed for transmission networks | **No — explicit** ᵈ | shared-environment noted as confounder ᵈ | partial |
| **VALENCIA** *(template, CST-level not strain)* | nearest-centroid to 13 fixed reference CSTs | n/a (composition) | n/a | n/a | replaces per-study clustering | **yes** — the standardization template ᶠ |
| **strainshare** *(this work)* | popANI ≥ **0.999** (lead) **and 0.99999** (canonical), both reported | `percent_compared` ≥ **0.5**, coverage ≥ **5×** | **StrainGE fallback (M3)** below the inStrain floor (~0.5×) | **Yes** — from longitudinal acquisition timing; cross-sectional → `direction_unresolved` (never guessed) | within-vs-between-person **null** + **contamination** discriminator + **generalist** filter | **yes** — versioned spec (`spec_version`), reference-based |

## Where strainshare is differentiated

No existing tool combines these for the gut↔FGT use case; strainshare is an *integration + standard*, not a new aligner:

1. **Honest direction.** Every method above declines to call direction. strainshare infers it *only* from longitudinal timing and explicitly returns `direction_unresolved` otherwise — it never manufactures a direction from a sharing call.
2. **Controls shipped, not assumed.** The within/between-person null, the community-similarity contamination check, and the generalist-strain filter are built in — addressing the confounds (shared environment, cross-swab contamination) that the transmission literature flags as the main false-positive sources.
3. **Low-biomass path.** An explicit StrainGE fallback for vaginal samples that fall below inStrain's ~5–10× confidence floor (empirically established here).
4. **A fixed, versioned standard with a *measured* resolution.** Like SameStr and VALENCIA, thresholds are fixed and comparable across studies — but strainshare additionally ships an **empirical characterization of what its threshold means**: a species-agnostic resolution limit of **~0.1% divergence** (SD < 10⁻⁴ across *L. crispatus*, *L. iners*, *G. vaginalis*; `example/benchmark/fig_precision_edge.png`). A "shared strain" is thus a quantitative claim ("diverged < ~0.1%"), not a convention.

## Caveats / honest scoping

- The comparison is about **defaults and design intent**, not head-to-head accuracy on one dataset (that is Fig 3 / the benchmarks).
- StrainGE's low-coverage advantage comes partly from an author-run benchmark; its assembly step reportedly underperforms on real low-biomass input, so M3 is a *fallback*, not a wholesale replacement.
- strainshare's direction and null modules require **longitudinal, paired-site** sampling to be informative; on cross-sectional cohorts they correctly return "unresolved" rather than a result.
- The VALENCIA row is a **design template** (community-state-type level), included to show the standardization pattern strainshare follows — not a strain-level competitor.

## Sources

- ᵃ inStrain — https://instrain.readthedocs.io/en/latest/important_concepts.html (99.999% popANI, ≥50% percent_compared, coverage/breadth)
- ᵇ StrainGE (incl. StrainPhlAn comparison) — Genome Biology 2022, https://genomebiology.biomedcentral.com/articles/10.1186/s13059-022-02630-0 (0.5× bound; ~74% vs ~1.4% genome coverage). The 0.1× / <0.1%-abundance claim did **not** survive verification.
- ᶜ SameStr — Microbiome 2022, https://microbiomejournal.biomedcentral.com/articles/10.1186/s40168-022-01251-w (MVS ≥99.9% over ≥5 kb)
- ᵈ TRACS — Nature Microbiology 2026, https://www.nature.com/articles/s41564-026-02339-x ("does not determine transmission direction")
- ᵉ Empirical confidence floor (~10×) — this repo, `example/benchmark/reads_summary.tsv` (10b)
- ᶠ VALENCIA — Microbiome 2020, https://microbiomejournal.biomedcentral.com/articles/10.1186/s40168-020-00934-6 (fixed reference centroids vs per-study clustering)
- Resolution limit (~0.1%, species-agnostic) — this repo, `example/benchmark/precision_edge_summary.tsv` (10c)
