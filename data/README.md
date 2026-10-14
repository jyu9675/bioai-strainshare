# data/ (runtime — contents are gitignored)

Input fastqs and metadata live here. Sequence files are **not** committed to GitHub
(they are large and often controlled-access); only this README and `.gitkeep` are tracked.

Expected contents when running:
- `*_1.fq.gz`, `*_2.fq.gz` — paired shotgun reads (downloaded by `scripts/01_download_wgs.sh`)
- `metadata.tsv` — columns: `sample  subject  timepoint  bodysite`

To track a specific small metadata file anyway: `git add -f data/metadata.tsv`.
