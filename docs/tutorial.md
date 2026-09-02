# Tutorial

Two ways in: (A) run the **analysis half** on a compare table you already have (works anywhere,
~seconds), or (B) run the **whole pipeline from FASTQ** with Snakemake (needs the conda stack).

---

## A. Analysis half on your own data (no cluster)

You provide three files:

1. **`compare.tsv`** — an inStrain `genomeWide_compare.tsv` with columns
   `genome  name1  name2  popANI  percent_genome_compared` (extra columns are ignored).
2. **`metadata.tsv`** — one row per sample:
   ```
   sample        subject  timepoint  bodysite
   S1_vagina_30  S1       30         vagina
   S1_gut_30     S1       30         gut
   ```
   `bodysite ∈ {vagina, gut, oral}`; `sample` must match the names in the compare table.
3. **`community.tsv`** — a community table (rows = features/species, columns = samples) used for the
   translocation-vs-contamination check. A merged MetaPhlAn table works directly.

Run it:
```bash
strainshare analyze --compare compare.tsv --meta metadata.tsv --metaphlan community.tsv --outdir results
```

You get:

| Output | What it is |
|---|---|
| `pairs_tagged.tsv` | every genome × sample-pair: class, popANI, breadth, shared flag, Bray–Curtis |
| `species_within_between.tsv` | per-genome within- vs between-person shared rate (the null) |
| `translocation_candidates.tsv` | within-person shared strains + translocation/contamination verdict |
| `translocation_candidates_scored.tsv` | the above + generalist flag + confidence |
| `genome_generalist_flags.tsv` | per-genome between-person shared rate; generalists down-ranked |
| `direction_calls.tsv` | per shared strain: `gut_to_vagina` / `vagina_to_gut` / `direction_unresolved` |
| `figures/fig1..3.png` | within/between, translocation plane, directionality timeline |

**A quick diagnostic** — the single most honest view of a result (are calls real, or high-popANI
artifacts on tiny breadth?):
```bash
strainshare diagnostic --pairs results/pairs_tagged.tsv --out results/figures/popani_breadth.png --title "My cohort"
```
Only points in the top-right box (popANI ≥ 0.999 **and** breadth ≥ 0.5) are confident calls.

## B. Whole pipeline from FASTQ (Snakemake)

1. Build/point at a reference (`refs/vagref.fna`, `.stb`, bowtie2 index — see `scripts/02_build_ref.sh`).
2. Edit `workflow/samples.tsv` (columns `sample subject timepoint bodysite fq1 fq2`) and
   `workflow/config.yaml` (paths, threads).
3. Dry-run, then run:
   ```bash
   conda activate bioai && pip install .
   snakemake -j8 --configfile workflow/config.yaml -n     # dry-run
   snakemake -j8 --configfile workflow/config.yaml
   ```

> **Scaling caveat.** The all-samples `inStrain compare` can exhaust memory on large cohorts. A
> chunked/streaming compare is the Item-3 work; for moderate cohorts the standard path is fine.

## Fetch a public dataset (ENA → sample sheet)

`strainshare fetch` turns an ENA BioProject into a ready sample sheet by parsing each sample's
alias into a subject id + a site code (many cohorts encode this, e.g. `95V` = subject 95 vaginal,
`90C` = cervical). It keeps only WGS runs and, by default, only subjects sampled at ≥2 sites.

```bash
# 12 paired subjects (vagina + cervix) from a public cohort, metadata only:
strainshare fetch --bioproject PRJNA982400 --site-map "V=vagina,C=cervix,R=rectum" \
    --max-subjects 12 --outdir data/mycohort
# -> data/mycohort/samples.tsv (fq1/fq2 are ENA URLs)

# add --download to pull the fastqs (large!), then point the workflow at the sheet:
snakemake -j8 --configfile workflow/config.yaml     # samples: data/mycohort/samples.tsv
strainshare analyze --compare ... --site-pair cervix,vagina ...
```

Finding datasets: they must be **shotgun WGS** and sample **≥2 body sites from the same people**.
Good public options: **HMP1** (stool + posterior-fornix + oral, portal.hmpdacc.org), **PRJNA982400**
(vaginal + cervical), **Goltsman PRJNA288562** (vaginal + gut, shallow). MOMS-PI (vagina+rectum) is
dbGaP controlled-access.

## Other body-site pairs

The default is gut↔vagina, but the same machinery works for **any two sites** present in your
metadata `bodysite` column — oral↔gut, mother↔infant, FMT donor↔recipient, skin sites, etc.
Override per run:
```bash
strainshare analyze --compare compare.tsv --meta metadata.tsv --metaphlan community.tsv \
  --outdir results --site-pair oral,gut
```
or set it once in your standard (`site_pair: [oral, gut]`). Class labels and direction calls follow
the names you give — e.g. `within_oral_gut`, `oral_to_gut`, columns `earliest_oral_tp` /
`earliest_gut_tp`.

## Thresholds

Every cutoff lives in one place — [`strainshare/strainshare_standard.yaml`](../strainshare/strainshare_standard.yaml).
Don't hand-edit cutoffs in code; change them there (and bump `spec_version`) so results stay
comparable across runs. Pass a custom copy with `--config my_standard.yaml`.

## What the numbers mean

From the benchmarks (`example/benchmark/`): a shared-strain call means **diverged by < ~0.1%**
(the threshold's measured resolution), and confident calls need **~10× coverage** on the compared
taxon. Below that, expect `direction_unresolved` and sub-breadth points rather than false positives.
