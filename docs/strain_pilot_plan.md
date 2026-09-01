# Pilot Plan — Gut↔Vaginal Strain Sharing on the Goltsman/DiGiulio Cohort (PRJNA288562)

**Goal of the pilot:** validate a modern, contamination-aware strain-sharing pipeline on a public dataset that *already shows the signal but never confirmed strain identity* — before running it on our own 191-sample paired cohort.

**Why this dataset:** Goltsman 2018 found vaginal *Lactobacillus*/*Gardnerella* sequences in the gut of 7/10 subjects, and within-subject sequences were phylogenetically closer than between-subject — but (a) they showed *related*, not *identical* strains, (b) used low-depth (0.4M reads) assembly + VarScan, n=10, and (c) had **no contamination control**. It is also **longitudinal**, so it can address directionality, which our cross-sectional cohort cannot.

**The claim we're testing:** *Do any within-person gut–vaginal pairs share the identical strain (popANI ≥ 99.9%), and does the signal survive contamination control?* Either answer is publishable.

---

## Reference genome set (decide first)

Focused DB keeps the pilot tractable and interpretable. Pull representative genomes for the taxa that can actually reach strain resolution at this depth:

- *Lactobacillus iners*, *L. crispatus*, *L. jensenii*
- *Gardnerella / Bifidobacterium vaginale* complex
- *Prevotella bivia* (and a few gut-abundant controls, e.g. *Bacteroides fragilis*, so non-shared species act as internal negatives)

Sources: GTDB reps + NCBI; optionally add Goltsman's own 29 GenBank assemblies + Stanford Digital Repository genomes (purl.stanford.edu/vp282bh3698) as a bonus positive control. Dereplicate before mapping.

```bash
dRep dereplicate genome_db/ -g genomes/*.fna -p 16
cat genome_db/dereplicated_genomes/*.fna > vagref.fna
bowtie2-build --threads 16 vagref.fna vagref
parse_stb.py --reverse -f genome_db/dereplicated_genomes/*.fna -o vagref.stb   # scaffold→genome map
```

---

## Step 0 — Download the shotgun subset

Filter PRJNA288562 to WGS (most runs are 16S — useless for strain calls). See earlier: pull `library_strategy == WGS` fastqs via ENA filereport. Recover **subject / timepoint / body site** from the SraRunTable — you need all three columns downstream.

## Step 1 — Map + profile each sample

```bash
# per sample
bowtie2 -x vagref -1 ${S}_1.fq.gz -2 ${S}_2.fq.gz -p 16 \
  | samtools sort -@8 -o ${S}.bam && samtools index ${S}.bam

inStrain profile ${S}.bam vagref.fna -o ${S}.IS -s vagref.stb \
  -p 16 --database_mode          # database_mode: recommended when mapping to a multi-genome DB
```

Keep only genome×sample instances with **coverage ≥ 5×** and **breadth ≥ 0.5** — below that, popANI is unreliable (this is why only dominant species will qualify at 0.4M reads).

## Step 2 — Compare pairs (the signal + the null in one run)

Run `compare` across **all samples**, then slice pairs in analysis. This gives you within-person and between-person comparisons from the same call.

```bash
inStrain compare -i *.IS -o compare.IS -s vagref.stb -p 16 --database_mode
# key output: compare.IS/output/*_genomeWide_compare.tsv
#   columns: genome, name1, name2, popANI, conANI, percent_genome_compared
```

**Shared-strain call:** `popANI ≥ 0.999` AND `percent_genome_compared ≥ 0.5`.
> ⚠️ Threshold note: our deck uses **99.9%**; inStrain's canonical "same strain" bar is stricter (**99.999%**). Pick one and be consistent across the pilot and the main cohort — I'd report both columns and lead with 99.9% to match the deck.

## Step 3 — Build the null (within vs between person)

From `genomeWide_compare.tsv`, tag each pair using the metadata:

| Comparison class | meaning |
|---|---|
| within-person, gut↔vagina | **the signal** |
| between-person, gut↔vagina | **the null** (unrelated women) |
| within-person, same-site over time | positive control (should share) |

Per species, compute `P(popANI ≥ 0.999)` for within vs between. **Real biology → within ≫ between.** If within ≈ between, the "sharing" is background/technical. This reproduces (and modernizes) Goltsman's within>between result — Figure 1.

## Step 4 — Contamination filter on survivors

For every within-person gut–vaginal pair that clears popANI ≥ 0.999, decide translocation vs cross-swab contamination:

- **Whole-community dissimilarity:** compute Bray–Curtis (MetaPhlAn profiles) between the two samples over *shared species*. **True translocation = shared strain + DISSIMILAR community** (one strain moved). **Contamination = shared strain + SIMILAR community** (whole soup moved).
- **Abundance sanity check:** contamination shows the donor's dominant species appearing at *trace* abundance in the recipient (the Goltsman "very low abundance in gut" pattern). Flag these.
- If the original plate layout were available you'd add same-plate/CroCoDeEL flags — not available here, so rely on the community-dissimilarity rule. → Figure 2.

## Step 5 — Temporal order (what our own cohort can't do)

For surviving shared strains, use the weekly timepoints: does the strain appear in **gut before vagina** or **vagina before gut**? Report per event. Even a handful of directional calls is a genuine advance over 2018. → Figure 3.

---

## Deliverables / success criteria

1. **Fig 1** — within vs between-person popANI distributions per species (reproduce + sharpen Goltsman).
2. **Fig 2** — shared-strain candidates on a popANI × community-similarity plane; translocation vs contamination quadrants.
3. **Fig 3** — directionality timeline for surviving events.
4. **Table** — species ranked by within−between shared-strain rate, with n events, median popANI, % surviving contamination filter.

**Pilot passes if:** (a) we reproduce within>between relatedness, and (b) the pipeline behaves sensibly on positive controls (same-site-over-time shares; unrelated-person pairs don't). Whether *any* gut–vaginal pair clears 99.9% + contamination filter is the actual scientific result — a rigorous negative is still a finding given Takada 2025.

## Known limits (state up front)

- Depth 0.4M reads → only *L. iners / L. crispatus / G. vaginalis* likely reach strain resolution.
- n=10 → underpowered for the formal null; this validates the *method*, not a population estimate.
- Stool and rectal swabs are mixed in this cohort; note it.
