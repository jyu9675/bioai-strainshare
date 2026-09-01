# BIOAI — Gut↔Vaginal Strain Sharing Pilot

Pilot strain-transmission analysis on the public Goltsman/DiGiulio pregnancy cohort
(**PRJNA288562**), as a pipeline shakedown before the 191-sample paired V–R cohort.

See [docs/strain_pilot_plan.md](docs/strain_pilot_plan.md) for the full rationale, thresholds, and figures,
and [docs/ONBOARDING.md](docs/ONBOARDING.md) for a lab-member quick start.

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
  10_benchmark.py              Study D Fig 3: coverage-sweep sensitivity/specificity + inStrain→StrainGE crossover
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
