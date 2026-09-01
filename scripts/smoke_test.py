#!/usr/bin/env python3
"""
Generate a tiny synthetic dataset (fake inStrain compare table + metadata + MetaPhlAn table)
and run 05 + 06 on it, so the analysis/plotting half can be validated on Windows TODAY,
before any real sequencing data exists.

It plants three known truths so you can eyeball that the pipeline calls them correctly:
  - L. crispatus  : a REAL within-person gut↔vagina shared strain with DISSIMILAR community
                    -> should surface as a 'translocation_candidate'
  - G. vaginalis  : a within-person shared strain but with SIMILAR community
                    -> should surface as a 'contamination_suspect'
  - L. iners      : shared within same person over time (positive control), NOT gut↔vagina

Usage:
  python scripts/smoke_test.py            # writes to results/smoke/ and makes figures
"""
import os, subprocess, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "results", "smoke")
os.makedirs(OUT, exist_ok=True)
np.random.seed(1)

# --- samples: 3 subjects, gut+vagina, two timepoints ---
rows = []
for subj in ["S1", "S2", "S3"]:
    for site in ["vagina", "gut"]:
        for wk in [12, 30]:
            rows.append(dict(sample=f"{subj}_{site}_{wk}", subject=subj,
                             timepoint=wk, bodysite=site))
meta = pd.DataFrame(rows)
meta.to_csv(f"{OUT}/metadata.tsv", sep="\t", index=False)
S = meta["sample"].tolist()

# --- MetaPhlAn-like species table (rows=species, cols=samples, rel-abundance %) ---
species = ["s__Lactobacillus_crispatus", "s__Lactobacillus_iners",
           "s__Gardnerella_vaginalis", "s__Prevotella_bivia",
           "s__Bacteroides_fragilis", "s__Faecalibacterium_prausnitzii"]
mpa = pd.DataFrame(0.0, index=species, columns=S)
for c in S:
    if "vagina" in c:      # vaginal: Lactobacillus-dominated
        mpa.loc["s__Lactobacillus_crispatus", c] = np.random.uniform(60, 85)
        mpa.loc["s__Lactobacillus_iners", c] = np.random.uniform(5, 20)
        mpa.loc["s__Gardnerella_vaginalis", c] = np.random.uniform(1, 8)
    else:                  # gut: Bacteroides/Faecalibacterium-dominated (DISSIMILAR to vagina)
        mpa.loc["s__Bacteroides_fragilis", c] = np.random.uniform(20, 40)
        mpa.loc["s__Faecalibacterium_prausnitzii", c] = np.random.uniform(20, 40)
        mpa.loc["s__Prevotella_bivia", c] = np.random.uniform(5, 15)
        mpa.loc["s__Gardnerella_vaginalis", c] = np.random.uniform(1, 5)
# Make S3's gut look vagina-like (simulate whole-community contamination) so its shared
# G. vaginalis reads as a contamination_suspect (SIMILAR community).
for wk in [12, 30]:
    c = f"S3_gut_{wk}"
    mpa[c] = 0.0
    mpa.loc["s__Lactobacillus_crispatus", c] = np.random.uniform(60, 85)
    mpa.loc["s__Gardnerella_vaginalis", c] = np.random.uniform(5, 12)
    mpa.loc["s__Lactobacillus_iners", c] = np.random.uniform(5, 15)
mpa.to_csv(f"{OUT}/merged_metaphlan.tsv", sep="\t")

# --- fake inStrain genomeWide_compare.tsv ---
def row(g, a, b, popani, breadth=0.8):
    return dict(genome=g, name1=a, name2=b, popANI=popani, conANI=popani,
                percent_genome_compared=breadth)

C = []
# L. crispatus: identical within-person gut↔vagina (real translocation), non-identical between-person
for subj in ["S1", "S2"]:
    C.append(row("Lactobacillus_crispatus", f"{subj}_vagina_30", f"{subj}_gut_30", 0.99995))
C.append(row("Lactobacillus_crispatus", "S1_vagina_30", "S2_gut_30", 0.9970))   # between: not shared
# G. vaginalis: identical within-person gut↔vagina for S3, but S3 gut community ~ vagina (contamination)
C.append(row("Gardnerella_vaginalis", "S3_vagina_30", "S3_gut_30", 0.99996))
# L. iners: shared within same site over time (positive control)
C.append(row("Lactobacillus_iners", "S1_vagina_12", "S1_vagina_30", 0.99999))
# Prevotella bivia: between-person, low popANI (clear negative)
C.append(row("Prevotella_bivia", "S1_gut_30", "S2_gut_30", 0.9950))
pd.DataFrame(C).to_csv(f"{OUT}/genomeWide_compare.tsv", sep="\t", index=False)

print(f"[smoke] wrote synthetic inputs to {OUT}")

# --- run 05 then 06 ---
def run(cmd):
    print("> " + " ".join(cmd)); subprocess.run(cmd, check=True)

py = sys.executable
run([py, f"{HERE}/05_shared_strain_analysis.py",
     "--compare", f"{OUT}/genomeWide_compare.tsv",
     "--meta", f"{OUT}/metadata.tsv",
     "--metaphlan", f"{OUT}/merged_metaphlan.tsv",
     "--outdir", OUT])
run([py, f"{HERE}/06_plots.py",
     "--pairs", f"{OUT}/pairs_tagged.tsv",
     "--candidates", f"{OUT}/translocation_candidates.tsv",
     "--meta", f"{OUT}/metadata.tsv",
     "--outdir", f"{OUT}/figures"])

print("\n[smoke] EXPECTED:")
print("  translocation_candidates.tsv -> L. crispatus (S1,S2) = translocation_candidate,")
print("                                  G. vaginalis (S3)    = contamination_suspect")
print(f"  figures in {OUT}/figures/fig1..3.png")
