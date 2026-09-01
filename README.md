# strainshare

[![CI](https://github.com/jyu9675/bioai-strainshare/actions/workflows/ci.yml/badge.svg)](https://github.com/jyu9675/bioai-strainshare/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](pyproject.toml)

**A standardized, contamination-aware framework for cross-body-site bacterial strain sharing**
(e.g. <kbd>gut ↔ cervicovaginal</kbd>). It wraps inStrain/StrainGE with a *versioned threshold
standard*, a within-vs-between-person null, a translocation-vs-contamination discriminator, a
generalist-strain filter, longitudinal-only transmission-direction inference, and a low-biomass
fallback — so shared-strain calls are **comparable across studies and labs**, the way VALENCIA
standardized vaginal community-state typing.

📖 [Install](docs/install.md) · [Tutorial](docs/tutorial.md) · [Lab onboarding](docs/ONBOARDING.md) ·
[The standard](strainshare/strainshare_standard.yaml) · [Manuscript draft](docs/manuscript-draft.md)

## Install
```bash
pip install .                 # or  pip install -e ".[dev]"  for development
strainshare version
strainshare benchmark --selftest   # validate the install in seconds, no data needed
```
The pure-Python analysis (`analyze`, `benchmark`, `diagnostic`) runs anywhere. Heavy steps
(mapping/profiling/MetaPhlAn) additionally need the conda stack: `conda env create -f environment.yml`.

## Quickstart
```bash
# Analysis half (cross-platform): compare table + metadata + community table -> tables + figures
strainshare analyze --compare compare.tsv --meta metadata.tsv --metaphlan community.tsv --outdir results

# Whole pipeline from FASTQ (needs the conda env): edit workflow/{config.yaml,samples.tsv}, then
snakemake -j8 --configfile workflow/config.yaml
```

`metadata.tsv` columns: `sample  subject  timepoint  bodysite` (bodysite ∈ {vagina, gut, oral}).
Outputs: `pairs_tagged`, `species_within_between`, `translocation_candidates(_scored)`,
`genome_generalist_flags`, `direction_calls`, and `figures/`. See the [tutorial](docs/tutorial.md).

> **Note on the codebase.** The canonical, installable, tested implementation is the
> [`strainshare/`](strainshare) Python package (used by the CLI, the Snakemake workflow, and CI).
> The numbered `scripts/` are the original pilot pipeline (heavy WSL steps + reference); folding
> their remaining logic fully into the package is tracked as Item 3. Both share one threshold
> standard.

---

## Pilot provenance

This repo began as a pilot on the public Goltsman/DiGiulio pregnancy cohort
(**PRJNA288562**), a shakedown before a 191-sample paired vaginal–rectal cohort.
See [docs/strain_pilot_plan.md](docs/strain_pilot_plan.md) for the rationale/thresholds and
[docs/goltsman-cohort-findings.md](docs/goltsman-cohort-findings.md) for the cohort result.

## Layout
```
docs/
  strain_pilot_plan.md   the plan (question → steps → deliverables)
  ONBOARDING.md          lab-member quick start
  design-note.html       where the tool is headed (design + research plan)
example/                 committed smoke-test output — what finished results look like
scripts/
  00_build_metadata.py         SraRunTable → data/metadata.tsv (sample/subject/timepoint/bodysite)
  01_download_wgs.sh            download WGS subset from ENA (filters out 16S)
  02_build_ref.sh              dRep → bowtie2 index → scaffold-to-bin map (vagref.*)
  03_map_profile.sh            per-sample bowtie2 map + inStrain profile
  04_compare.sh                inStrain compare (all profiles pairwise)
  05_shared_strain_analysis.py Steps 3–4: within-vs-between null + contamination verdict
  06_plots.py                  Figs 1–3 (within/between, translocation plane, directionality)
  07_metaphlan.sh              merged MetaPhlAn species table (feeds 05's Bray–Curtis filter)
  08_direction.py              M4: longitudinal-only transmission direction (gut-first vs vagina-first)
  09_generalist_filter.py      M5: flag strains shared across UNRELATED people (confound control)
  10_benchmark.py              Study D Fig 3: coverage-sweep + reads validation (--from-reads) + precision edge (--precision-edge)
  10b_reads_benchmark.sh       real reads validation: same vs 0.3%-diverged strain across coverage (Unix)
  10c_reads_benchmark_scaled.sh  scaled precision edge: 3 species × near-boundary divergence × reps (Unix, resumable)
  04b_between_person_compare.sh  pairwise between-person null for F1/F5 (all-N compare OOMs; Unix, resumable)
  plot_popani_breadth.py       diagnostic: popANI × breadth by pair class (confident-call box QC)
  03b_strainge_fallback.sh     M3: low-biomass StrainGE fallback (scaffold, Unix-only)
  strainshare.py               unified config-driven analysis runner (05→09→08→06; cross-platform)
  strainshare_config.py        the STANDARD — single source of truth for every threshold
  strainshare_standard.yaml    machine-readable mirror of the standard (edit to override)
  check_env.sh                 verify tool stack is installed before running
  smoke_test.py                synthetic end-to-end test of 05+08+09 (runs on Windows, no real data)
  dev/                         scratch/debug helpers (kept for provenance, not part of the pipeline)
workflow/Snakefile             M6: portable Snakemake DAG (scaffold)
environment.yml  conda env (bioai) for the Unix stack — steps 02–04, 07
refs/    reference genomes / dRep DB / bowtie2 index (vagref.*)
data/    downloaded fastqs + run/sample metadata
results/ inStrain profiles, compare output, figures/tables
```

## Pipeline order (run scripts in number order)
1. `01_download_wgs.sh` → fastqs + `wgs_runs.tsv`. Grab `SraRunTable.csv` from SRA Run Selector,
   then `00_build_metadata.py --srarun SraRunTable.csv --wgs data/wgs_runs.tsv --out data/metadata.tsv`
   (auto-detects columns; use `--col-subject/--col-site/--col-time` if it can't).
2. Put genomes in `refs/genomes/`, then `02_build_ref.sh` → `refs/vagref.*` + `vagref.stb`.
3. `03_map_profile.sh` → `results/profiles/<sample>.IS` (cov ≥5×, breadth ≥0.5).
4. `04_compare.sh` → `results/compare.IS/output/*_genomeWide_compare.tsv`.
5. `05_shared_strain_analysis.py --compare ... --meta ... --metaphlan ...`
   → `species_within_between.tsv`, `translocation_candidates.tsv`, `pairs_tagged.tsv`.
6. `06_plots.py --pairs ... --candidates ... --meta ...` → `results/figures/fig{1,2,3}.png`.

`07_metaphlan.sh` (run any time after step 1, parallel to 02–04) produces the merged MetaPhlAn
table `05` needs. Run `check_env.sh` first to confirm the tool stack is installed.

## Environment
Heavy steps (02–04, 07) need a Unix bioinformatics stack — run on **WSL2 / Linux / HPC**, not
native Windows: `conda env create -f environment.yml && conda activate bioai`, then `check_env.sh`.
The pure-Python half (00, 05, 06) runs on Windows with `conda install pandas numpy matplotlib`.

**Validate the analysis today, no data needed:** `python scripts/smoke_test.py` fabricates a tiny
dataset with known truths and runs 05+06 → tables + `results/smoke/figures/fig{1,2,3}.png`.
Expected: L. crispatus = translocation_candidate, G. vaginalis = contamination_suspect.

## Typical split
Run 01–04 + 07 on the cluster (produces a few small tables: `genomeWide_compare.tsv`,
`merged_metaphlan.tsv`), copy those + `metadata.tsv` back to Windows, run 05–06 locally.

## Key thresholds (locked for consistency with the main cohort)
- Shared strain: `popANI ≥ 0.999` (deck standard; inStrain canonical is 0.99999 — report both).
- Comparison breadth: `percent_genome_compared ≥ 0.5`; per-sample coverage `≥ 5×`.
- Contamination rule: shared strain + **similar** community (low Bray–Curtis) = suspect; shared strain + **dissimilar** community = translocation candidate.

## Metadata contract
`data/metadata.tsv` must have columns: `sample  subject  timepoint  bodysite`
with `bodysite ∈ {vagina, gut, oral}` and `sample` matching inStrain sample names.
