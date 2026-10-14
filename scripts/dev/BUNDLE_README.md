# strainshare — script bundle

Everything needed to run the contamination-aware strain-sharing analysis end-to-end. Full project +
history: **github.com/jyu9675/bioai-strainshare** (MIT; DOI 10.5281/zenodo.22275588).

## Contents
```
strainshare/              the Python package (CLI: analyze | fetch | benchmark | diagnostic | version)
pyproject.toml            install metadata  ->  pip install -e .
scripts/dev/
  _cx_test.sh             download -> bowtie2 map -> inStrain profile -> compare  (any site pair; ENA)
  _hmp_run.sh             same chain, streaming HMP samples from public AWS S3
  _hmp_run_full.sh        whole-cohort HMP wrapper (seeds finished profiles, runs the funnel)
  ec2_hmp_run.sh          ONE-SHOT turnkey HMP run on a fresh EC2 instance (us-west-2)
  _build_broadref.sh      build the broad vaginal+gut reference (reuses local genomes)
  _build_broadref_ec2.sh  self-contained 33-genome reference build (fresh machine)
  hmp_aim1_funnel.py      integrity-gated funnel: QC -> evaluable -> shared species -> shared strains
  hmp_codetect_watch.py   flags within-woman gut<->vagina co-detections (EVALUABLE vs low-breadth)
  build_pptx.py           regenerate the progress deck
  *.tsv                   sample manifests (HMP paired-women maps, etc.)
```

## Environment (once)
```bash
mamba create -n strainshare -c bioconda -c conda-forge bowtie2 samtools instrain awscli pandas python=3.11
conda activate strainshare
pip install -e .            # gives the `strainshare` command
strainshare version
```

## Workflow
1. **Get a sample sheet from public data**
   `strainshare fetch --bioproject PRJNA982400 --outdir data`   (parses aliases → subject + body site)
2. **Build a reference** (breadth is the sensitivity lever)
   `OUT=refs/broadref bash scripts/dev/_build_broadref.sh`      (or `_build_broadref_ec2.sh` on a fresh box)
3. **Run the chain** (download → map → profile → compare). For a cervix/vaginal or arbitrary pair:
   `PICK=pick.tsv OUT=run REF=refs/broadref bash scripts/dev/_cx_test.sh`
   For HMP gut↔vaginal from AWS: `... bash scripts/dev/_hmp_run_full.sh`   (turnkey EC2: `ec2_hmp_run.sh`)
4. **Analyze**
   `strainshare analyze --compare run/genomeWide_compare.tsv --meta run/metadata.tsv \`
   `  --metaphlan run/community.tsv --site-pair cervix,vagina --outdir run/out`
   → shared-strain calls, within-vs-between null, translocation-vs-contamination, direction, figures.

## Operational notes (hard-won)
- inStrain confident-popANI floor is ~10× on the organism at BOTH sites; shared-strain popANI ≥ 0.999.
- Reads from host-removed datasets have desynced mates → the drivers map **unpaired** with
  `--pairing_filter all_reads`.
- Run on native ext4, not a 9p/DrvFs mount — heavy I/O on 9p destabilizes WSL.
- `DL_RETRY_SLEEP` (in `_cx_test.sh`) paces retries to avoid ENA download-host rate-limits.
- Very deep stool can profile pathologically slowly / stress low-RAM VMs — run HMP on EC2 for the full set.
- Only comparisons powered at both sites are called; low coverage is labelled **not-evaluable**, never negative.
