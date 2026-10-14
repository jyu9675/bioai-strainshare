# BIOAI — Onboarding for lab members

**What it is:** a contamination-aware, reproducible pipeline that asks whether two
body sites in the same person share the *identical* bacterial strain — and whether
that sharing is real biology (translocation) or a swab artifact. Built for
gut&#8596;vaginal, but works on **any paired-site shotgun cohort**.

---

## Try it in ~2 minutes (no data, even on plain Windows)

```bash
conda install pandas numpy matplotlib     # if you don't have them
python scripts/smoke_test.py
# -> tables + results/smoke/figures/fig1..3.png
# Expected: L. crispatus = translocation_candidate, G. vaginalis = contamination_suspect
```

This fabricates a tiny dataset with three planted truths and runs the whole
analysis + plotting half end-to-end. It's the fastest way to see what the tool does.
A committed copy of that output lives in [`../example/`](../example) if you just want
to look.

## Run it on your own paired cohort (heavy steps: WSL2 / Linux / HPC)

```bash
conda env create -f environment.yml && conda activate bioai
bash scripts/check_env.sh                 # confirm the tool stack
# NOTE: bioconda's inStrain is ancient; after creating the env run:
#   pip install --upgrade instrain
# drop reference genomes in refs/genomes/, put fastqs + a metadata.tsv in data/
bash scripts/run_pipeline.sh 8            # runs 03 -> 04 -> 07 -> 05 -> 06 to finished figures
```

## What you provide

A metadata table with exactly these columns:

| sample | subject | timepoint | bodysite |
|--------|---------|-----------|----------|
| S1_vagina_30 | S1 | 30 | vagina |
| S1_gut_30 | S1 | 30 | gut |

`bodysite` in `{vagina, gut, oral}`; `sample` must match the inStrain sample names.

## What you get

- `pairs_tagged.tsv` — every genome × sample-pair, classified + shared-strain flag + Bray–Curtis
- `species_within_between.tsv` — per-species within- vs between-person shared-strain rate
- `translocation_candidates.tsv` — within-person shared strains with a translocation/contamination verdict
- `translocation_candidates_scored.tsv` — the above + generalist flag + confidence (M5)
- `genome_generalist_flags.tsv` — per-genome between-person shared rate; generalists are down-ranked (M5)
- `direction_calls.tsv` — per shared strain: `gut_to_vagina` / `vagina_to_gut` / `direction_unresolved` (M4)
- **Fig 1** within-vs-between-person popANI · **Fig 2** translocation-vs-contamination plane · **Fig 3** directionality timeline

### One-command analysis (cross-platform)

Once you have the cluster outputs (compare table + metadata + MetaPhlAn table), run everything at once:

```bash
python scripts/strainshare.py \
  --compare  results/compare.IS/output/genomeWide_compare.tsv \
  --meta     data/metadata.tsv \
  --metaphlan results/metaphlan/merged_metaphlan.tsv \
  --outdir   results
```

Thresholds come from `scripts/strainshare_standard.yaml` (the shared standard) — don't hand-edit
cutoffs in the scripts; change them there so results stay comparable across everyone's runs.

## Key thresholds (locked, so results are comparable across runs)

- Shared strain: `popANI >= 0.999` (canonical inStrain bar is 0.99999 — both are reported)
- Comparison breadth `>= 0.5`; per-sample coverage `>= 5x`
- Contamination rule: shared strain + **similar** community = suspect; + **dissimilar** community = translocation candidate

## Honest limits (so you don't misuse it)

- Needs **shotgun depth** — 16S can't reach strain resolution; at low depth only dominant
  species (*L. iners / L. crispatus / G. vaginalis*) qualify.
- **Direction** needs longitudinal timepoints; cross-sectional data gives "shared," not "who seeded whom."
- **Low-biomass vaginal samples** can fail inStrain's coverage floor (a StrainGE fallback is roadmap, not built).
- Heavy steps (map/profile/compare/MetaPhlAn) are **Unix-only**; the analysis + plotting half runs on Windows.

## Reusable beyond gut&#8596;vaginal

Swap the `bodysite` values and the reference set and the same machinery handles any
two-site question — FMT donor&#8596;recipient, mother&#8596;infant, oral&#8596;gut.

Questions? Ping the maintainer. See [`strain_pilot_plan.md`](strain_pilot_plan.md)
for the full scientific rationale and [`design-note.html`](design-note.html) for where the tool is headed.
