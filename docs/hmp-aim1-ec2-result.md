# HMP Aim-1 (gut ↔ vaginal strain sharing) — full-cohort EC2 run

Run date: 2026-10-01/02. Instance: r6i.12xlarge (48 vCPU / 384 GB / 1 TB), us-west-2 (data-local to
the HMP S3 bucket). Pipeline: stream HMASM WGS from S3 → bowtie2 (`--no-unal`) to the 33-genome
broadref → inStrain profile → coverage-based Aim-1 co-detection funnel. Scripts: `scripts/dev/ec2_hmp_run.sh`
+ `_hmp_run.sh` (fixes below). Cohort manifest: `hmp_metadata_run.tsv` (34 women / 98 samples).

## Result

**A clean, healthy-baseline NEGATIVE — "no evidence of gut↔vaginal strain sharing (depth-limited)."**

| metric | value |
|---|---|
| Samples profiled | **75 / 98** (23 deep-stool samples unprofilable — see Limits) |
| Women with **both** gut + vaginal profiles | **20 / 34** (evaluable for cross-site) |
| Species co-detected **≥5× at both sites** (strain-typing floor) | **0** in any woman |
| Species co-detected **≥1× at both sites** (sub-threshold) | only ***Prevotella amnii***, in **2 women** |
| …its coverage / breadth | gut ~1.1×, vaginal 2–4×, **breadth ~0.01** (floor 0.50) |
| Pairs strain-evaluable (breadth ≥0.5 both sites) | **0** |

The gut (Bacteroides/Phocaeicola-dominated) and vaginal (Lactobacillus-dominated) communities are
compositionally distinct; the only cross-site overlap is *P. amnii* at trace gut coverage, far too
sparse to strain-type. So this is "no evidence of sharing (depth-limited)", **not** "evidence of none".

## Consistency with prior cohorts

The recurring hit is **Prevotella amnii** — co-detected gut+vaginal but sub-threshold in:
- the **Fijian** rectovaginal pilot (P. amnii / P. bivia co-detected, breadth below floor),
- the **laptop** partial HMP run (P. amnii, low-breadth/UNRESOLVED), and now
- the **full HMP** cohort (P. amnii in 2/20 women, breadth ~0.01).

A BV-associated *Prevotella* appearing at both sites across three independent cohorts, always
depth-limited — a reproducible pattern and a concrete argument for the deeper sequencing the
rectovaginal proposal calls for (power the cohort for cross-site **taxon depth ≥10×**).

## Limits (honest)

- **23 deep-stool (gut) samples could not be profiled.** inStrain OOMs them at high concurrency
  (~27 GB RAM each on high-coverage stool) and hangs / exceeds a 3 h timeout at low concurrency — the
  long-standing "~13 h per deep stool / inStrain hangs at scale" wall, confirmed even on a 48-core box.
  They are gut-side samples, so some women lack their gut profile (20 of 34 remained cross-site-evaluable).
- **All-N `inStrain compare` is impractical at this scale** (75 profiles × all pairs > 2 h, the known
  compare-hang issue). Moot for the conclusion here, since **nothing reaches the ≥5× / ≥0.5-breadth
  strain-typing floor at both sites** — there is nothing to strain-compare. For a cohort that *does*
  clear the floor, use the pairwise within-woman + null compare (`05b_pairwise_compare.py`) rather than all-N.

## Pipeline fixes applied (committed)

- inStrain via **pip (≥1.9)** not bioconda (the default resolves to ancient 1.3.4 that crashes on
  modern Biopython); build-essential for biopython's C extension.
- **No `--database_mode`** in profile/compare (it drops covT → `KeyError 'covT'` in compare).
- **`--no-unal`** in bowtie2 (deep stool: only a tiny fraction maps to the targets; avoids sorting
  tens of millions of unmapped records).
- Fast **SRA/AWS in-region download**; correct reference prefix (`broadref/broadref`); parallel
  per-sample driver with RAM-aware concurrency + per-sample inStrain timeout.

## Files

`results_hmp_ec2/`: `co_detected_1x.tsv` (the P. amnii sub-threshold hits), `coverage_summary.tsv`
(per-sample genomes ≥5×), `aim1_funnel/`.
