# Runbook — HMP gut↔vaginal strain-sharing on AWS (34 paired women)

**What this runs.** A cohort-scale (n=34) test of the prior question behind the
[rectovaginal-pregnancy study](study-rectovaginal-pregnancy.md): *in healthy women, does any
gut strain also appear in the vagina?* It uses the Human Microbiome Project WGS (dbGaP phs000228 /
HMASM), the only **fully open** (no dbGaP application) paired gut+vaginal shotgun set.

**Honest scope (read first).** HMP is **healthy, non-pregnant, well-resourced US** women, and the gut
sample is **stool**, not a rectal swab. So this tests the **baseline mechanism**, not the pregnancy /
low-hygiene hypothesis. Interpret accordingly:
- A **clean negative at n=34** → gut↔vaginal strain sharing is rare in healthy adults → sharpens the case
  that pregnancy + limited hygiene is the *specific* condition to study prospectively.
- A **positive** → the mechanism is real in healthy adults and must be controlled for as a baseline.
- Target the **shareable** taxa — *E. coli*/Enterobacteriaceae, *Prevotella*, *Bacteroides* — since our
  pilot already showed the *Lactobacillus*/*Gardnerella* vaginal commensals are **not** gut-resident.

**Why AWS us-west-2.** The data live in `s3://human-microbiome-project/` in **us-west-2**. Pulling
~342 GB over a home link is ~5 days; from an instance *in the same region* it is fast and **egress-free**.
Run the analysis next to the data, keep only the small profiles, download just the results.

---

## Quick start (one-shot)
On a fresh **us-west-2** instance (Ubuntu 22.04 / AL2023, ≥16 vCPU, ≥32 GB RAM, a **≥250 GB** data
volume), point `WORK` at the big volume and run one script — it installs tools, builds the reference,
downloads + profiles all 34 women, and writes the funnel:
```bash
export WORK=/data/hmp                      # a path on your >=250 GB volume
curl -LsSf https://raw.githubusercontent.com/jyu9675/bioai-strainshare/main/scripts/dev/ec2_hmp_run.sh -o run.sh
nohup bash run.sh > $WORK.log 2>&1 &       # detached, so it survives your SSH session
tail -f $WORK.log
```
Results when it finishes (an afternoon on 16–32 vCPU):
- `"$WORK"/run/aim1_funnel/FUNNEL.txt` — the integrity-gated Aim-1 funnel over all 34 women
- `"$WORK"/run/CODETECTIONS.log` — every within-woman gut↔vagina co-detection (species ≥5× at both
  sites), tagged **EVALUABLE** vs **low-breadth/UNRESOLVED**; empty = none found
- Retrieve with `aws s3 cp --recursive "$WORK"/run/aim1_funnel s3://<your-bucket>/` (or scp), then
  **terminate the instance**.

The sections below explain each step and the choices baked into that script (why us-west-2, instance
sizing, the reference, the `SRS013521` skip, cost, interpretation).

---

## 0. Cohort at a glance
| | |
|---|---|
| Women (paired stool + vaginal WGS) | **34** |
| Samples | 51 vaginal (posterior fornix) + 48 stool = **99** |
| Longitudinal | several women have 2–6 visits (usable for direction, not designed for it) |
| Raw download | vaginal 9.5 GB + stool 332 GB ≈ **342 GB** (streamed per-sample, not held at once) |
| Sample map | [`scripts/dev/hmp_metadata.tsv`](../scripts/dev/hmp_metadata.tsv) (sample·subject·timepoint·bodysite), raw pairs in `scripts/dev/paired_women2.tsv` |

## 1. Launch an instance
- **Region:** `us-west-2` (required — data locality).
- **Type:** `c6i.4xlarge` (16 vCPU / 32 GB) is a good default; use `m6i.4xlarge` (64 GB) if inStrain
  runs OOM on the deepest stool samples. **Spot** cuts cost ~3–4×.
- **Storage:** 200 GB `gp3` EBS. Peak disk is small because each sample's raw reads are deleted right
  after profiling; what accumulates is the 99 `.IS` profiles (~30–40 GB) + the reference.
- **AMI:** Amazon Linux 2023 or Ubuntu 22.04. No IAM role or credentials needed — the bucket is public
  (`--no-sign-request`).

## 2. Set up the environment
```bash
# miniforge + tools
curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh -b -p $HOME/mf && source $HOME/mf/etc/profile.d/conda.sh
mamba create -y -n hmp -c bioconda -c conda-forge \
  bowtie2 samtools instrain awscli pandas python=3.11
conda activate hmp

# strainshare (this repo)
git clone https://github.com/jyu9675/bioai-strainshare.git && cd bioai-strainshare
pip install -e .
strainshare version
```

## 3. Build the reference (the sensitivity lever)
Reference **breadth is what limits cross-site detection** (the pilot showed a narrow reference throttles
it). Build a broad gut+vaginal catalog that *covers the HMP targets*:
```bash
# starting point — extend the target list inside the script to include the gut<->vaginal candidates:
#   E. coli / Klebsiella / Enterobacter, Prevotella spp., Bacteroides spp., Enterococcus,
#   plus the vaginal set (Lactobacillus crispatus/iners/jensenii/gasseri, Gardnerella, Fannyhessea).
REF=/data/refs/broadref bash scripts/dev/_build_broadref.sh
# result: /data/refs/broadref.fna + .stb + bowtie2 index (broadref.*.bt2)
```
For a definitive run, prefer a comprehensive catalog (GTDB representatives + a vaginal collection such
as VMGC) and add per-sample MAGs for organisms absent from the catalog — but the targeted broad
reference above is enough to answer the baseline question for the priority taxa.

## 4. Run it
```bash
REF=/data/refs/broadref OUT=/data/hmp \
MANIFEST=scripts/dev/hmp_metadata.tsv THREADS=16 \
nohup bash scripts/dev/_hmp_run.sh > /data/hmp.run.log 2>&1 &
tail -f /data/hmp.run.log
```
The driver streams each sample from S3 → extracts the QC'd/host-removed FASTQs → maps **unpaired**
(`-U`, because host removal desyncs mates) → `inStrain profile --pairing_filter all_reads` → deletes the
raw reads → then `inStrain compare` across all 99 profiles → `strainshare analyze --site-pair gut,vagina`.
It is **resumable**: a finished sample has `profiles/<SRS>.IS/.done` and is skipped on re-launch.

**Staging option (recommended).** The cohort splits into two drop-in manifests so you can answer the
cheap question first:
- **Tier 1 — [`hmp_metadata_tier1_singlepair.tsv`](../scripts/dev/hmp_metadata_tier1_singlepair.tsv)**:
  21 women with a clean 1 vaginal + 1 stool pair (42 samples). Run this first — it gives the baseline
  "does any within-woman gut↔vaginal sharing occur" answer at ~half the cost.
- **Tier 2 — [`hmp_metadata_tier2_multivisit.tsv`](../scripts/dev/hmp_metadata_tier2_multivisit.tsv)**:
  13 women with **true repeat collections** of the same body site (57 samples) — the longitudinal biology
  for direction exists here.
  **⚠ Direction (Aim 2) is NOT possible on open HMP.** Verified: the open ENA/SRA metadata carries **no
  `visit_number` and no `collection_date`** — only subject id, body sub-site, sex. Sample-id order
  (`700023119` < `700023728`) is only a *proxy* and must not ground a directional claim. Real visit order
  lives in the **dbGaP controlled phenotype files** (phs000228) → a data-access application is required.
  So: run **Aim 1** (cross-sectional sharing) on open HMP; pursue the dbGaP visit data for **Aim 2** only
  *if* Aim 1 finds within-woman shared strains. The `timepoint` column here is a placeholder, not a time.

Point `MANIFEST=` at whichever tier (or the full `hmp_metadata.tsv`). Profiles accumulate in the same
`profiles/` dir, so you can run Tier 1, then Tier 2, then one combined `inStrain compare` over all `.IS`.

**Runtime:** ~30–40 min/sample dominated by mapping ⇒ ~2–3 days on one 16-vCPU box. To finish in hours,
**shard**: split `hmp_metadata.tsv` into N chunks, run one instance per chunk (each writes its own
`profiles/`), then rsync all `.IS` dirs to one box for the single `inStrain compare` + `strainshare` step.

## 5. Collect results & tear down
```bash
# the outputs you keep are tiny — copy them off, then STOP the instance
aws s3 cp --recursive /data/hmp/strainshare_out  s3://<your-bucket>/hmp_out/   # or scp to your laptop
#   strainshare_out/  -> shared-strain calls, within-vs-between-person null, contamination flags, figures
#   /data/hmp/genomeWide_compare.tsv, community.tsv  -> raw compare + community matrix
```
**Terminate the instance** when done (or `stop` to keep the EBS volume for a resume). Don't leave it running.

## 6. Cost (rough)
| Item | Estimate |
|---|---|
| Compute — `c6i.4xlarge` **spot** ~$0.20/hr × ~60 h | **~$12** (on-demand ~$41) |
| EBS 200 GB gp3, a few days | **~$2** |
| S3 GET + egress (same region) | **$0** |
| **Total** | **~$15 (spot) – $45 (on-demand)** |

## 7. What you get / how to read it
`strainshare analyze` produces the standardized call set:
- **Shared-strain calls:** within-woman gut↔vaginal pairs at popANI ≥ 0.999 on ≥ 50% breadth.
- **Within-vs-between null:** the real signal is a strain shared *within* women but not between unrelated
  women (a strain shared across everyone is a generalist/DB artifact, filtered by M5).
- **Contamination discriminator:** shared strain + *dissimilar* community = candidate translocation;
  + *similar* community = down-ranked as possible cross-sample contamination.
- **Depth caveat carries over:** a cross-site call needs the shared organism at ≥ ~10× at *both* sites
  (the empirical confidence floor). Many candidate taxa will be depth-limited at one site → report
  "no evidence of sharing (depth-limited)", not "evidence of none".

Record the outcome honestly whichever way it falls; fold it into
[study-rectovaginal-pregnancy.md](study-rectovaginal-pregnancy.md) §7 as the baseline-mechanism result.
