#!/usr/bin/env python3
"""
T18 gut <-> vagina L. iners strain sharing, with matched controls.

The pre-registered standard needs percent_compared >= 0.5 for a confident call. The
cross-site comparisons here reach only ~0.23, because the gut carriage is ~3x. The
objection that follows -- "0.23 breadth is not enough to trust" -- is answered by the
MATCHED-BREADTH NEGATIVE CONTROL: the same woman's gut against an unrelated woman's
vagina, at essentially identical compared-bases count, is called cleanly different.
Breadth that can separate strains is breadth that can join them.

Writes example/crosssite/t18_comparisons.tsv
"""
import subprocess, os, glob, shutil
import pandas as pd

PROF = "/mnt/d/bioai/results/profiles"
STB = "/mnt/d/bioai/refs/vagref.stb"
OUT = "/mnt/c/Jeanyu/BIOAI/example/crosssite"
TARGET = "L_iners.fna"

os.environ["TMPDIR"] = "/home/allen/bioai_tmp"
os.makedirs(os.environ["TMPDIR"], exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# (label, sampleA, sampleB, role)
COMPARISONS = [
    ("T18 gut t106 x T18 vagina t191", "SRR6748155", "SRR6747944", "cross-site (primary)"),
    ("T18 gut t254 x T18 vagina t254", "SRR6748111", "SRR6748191", "cross-site (independent replicate)"),
    ("T18 gut t106 x T18 gut t254",    "SRR6748155", "SRR6748111", "gut lineage persistence"),
    ("T18 vagina t106 x vagina t254",  "SRR6747940", "SRR6748191", "vaginal positive control"),
    ("T18 gut t106 x T7 vagina",       "SRR6748155", "SRR6748072", "MATCHED-BREADTH negative control"),
]

rows = []
for label, a, b, role in COMPARISONS:
    print(f"{label} ...", flush=True)
    shutil.rmtree("/dev/shm/p", ignore_errors=True); os.makedirs("/dev/shm/p")
    for s in (a, b):
        subprocess.run(["cp", "-r", f"{PROF}/{s}.IS", "/dev/shm/p/"], check=False)
    shutil.rmtree("/dev/shm/c", ignore_errors=True)
    subprocess.run(["inStrain", "compare", "-i", f"/dev/shm/p/{a}.IS", f"/dev/shm/p/{b}.IS",
                    "-o", "/dev/shm/c", "-s", STB, "-p", "2"],
                   capture_output=True, text=True, timeout=1800)
    gw = glob.glob("/dev/shm/c/output/*genomeWide_compare.tsv")
    if not gw:
        print("   no output"); continue
    d = pd.read_csv(gw[0], sep="\t")
    t = d[d.genome == TARGET]
    if t.empty:
        print("   no L_iners row"); continue
    r = t.iloc[0]
    rows.append(dict(label=label, role=role, sampleA=a, sampleB=b,
                     popANI=r.popANI, compared_bases=int(r.compared_bases_count),
                     percent_compared=r.percent_compared,
                     population_SNPs=int(r.population_SNPs)))
    print(f"   popANI={r.popANI:.6f} bases={int(r.compared_bases_count)} "
          f"pc={r.percent_compared:.4f}", flush=True)

df = pd.DataFrame(rows)
df.to_csv(f"{OUT}/t18_comparisons.tsv", sep="\t", index=False)
print(f"\nwrote {OUT}/t18_comparisons.tsv")
print(df.to_string(index=False))
