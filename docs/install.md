# Installing strainshare

strainshare has two halves with different requirements:

| Half | What it does | Requirements |
|---|---|---|
| **Analysis** (`strainshare analyze / benchmark / diagnostic`) | shared-strain calls, null, contamination, generalist, direction, benchmarks, figures | pure Python — runs on Linux/macOS/**Windows** |
| **Heavy** (mapping / profiling / MetaPhlAn) | FASTQ → inStrain profiles → compare table + community table | Unix bioinformatics stack (conda) |

## 1. The Python package (analysis half)

```bash
git clone https://github.com/jyu9675/bioai-strainshare
cd bioai-strainshare
pip install .                      # or: pip install -e ".[dev]"  (editable + pytest)
strainshare version
strainshare benchmark --selftest   # ~1s sanity check, no data
```
Dependencies (pandas, numpy, matplotlib, pyyaml) install automatically.

### Docker (analysis half, zero local setup)
```bash
docker build -t strainshare .
docker run --rm strainshare version
docker run --rm -v "$PWD":/data strainshare analyze \
  --compare /data/compare.tsv --meta /data/metadata.tsv --metaphlan /data/community.tsv --outdir /data/out
```

## 2. The conda stack (heavy half)

```bash
conda env create -f environment.yml     # creates env `bioai`
conda activate bioai
# bioconda's inStrain is old; upgrade it:
pip install --upgrade instrain
bash scripts/check_env.sh                # confirm bowtie2 / samtools / inStrain / metaphlan / strainge
```

Then either drive the whole thing with Snakemake (`snakemake -j8 --configfile workflow/config.yaml`)
or run the numbered `scripts/` directly (see [ONBOARDING.md](ONBOARDING.md)).

## Verifying

```bash
pytest -q                 # unit tests (needs the [dev] extra)
strainshare benchmark --selftest
```
CI runs these on Python 3.9 / 3.11 / 3.12 on every push.
