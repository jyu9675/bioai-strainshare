#!/usr/bin/env python3
"""
Between-subject gut<->gut compare for P. vulgatus (and every other comparable genome),
on the Goltsman cohort. Tests whether the Fijian generalist call (P_vulgatus 107R<->57R,
popANI 0.99971 @ pc 0.768) reproduces in an unrelated US cohort with no shared environment.

Reuses the 05b RAM-staging workaround: only 2 profiles in /dev/shm per pair.
"""
import subprocess, os, glob, itertools, shutil, sys
import pandas as pd

META = "/mnt/d/bioai/data/metadata.tsv"
REFS = "/mnt/d/bioai/refs"
PROF = "/mnt/d/bioai/results/profiles"
RAM  = "/dev/shm/pvpair"
OUT  = "/mnt/d/bioai/results/pvulg_between.tsv"
TARGET = "P_vulgatus.fna"

os.environ["TMPDIR"] = "/home/allen/bioai_tmp"
os.makedirs(os.environ["TMPDIR"], exist_ok=True)

stb = None
for cand in ("vagref.stb", "broadref/broadref.stb", "broadref.stb"):
    p = os.path.join(REFS, cand)
    if os.path.exists(p):
        stb = p
        break
if stb is None:
    hits = glob.glob(f"{REFS}/**/*.stb", recursive=True)
    stb = hits[0] if hits else None
print(f"stb: {stb}", flush=True)

good = {}
for d in glob.glob(f"{PROF}/*.IS"):
    if os.path.exists(f"{d}/raw_data/covT.hd5"):
        good[os.path.basename(d)[:-3]] = d
meta = pd.read_csv(META, sep="\t")
gut = meta[(meta.bodysite == "gut") & (meta["sample"].isin(good))].copy()
print(f"usable gut profiles: {len(gut)} across {gut.subject.nunique()} subjects", flush=True)

# best P_vulgatus profile per subject (max coverage among breadth>0.5)
best = {}
for _, r in gut.iterrows():
    s = r["sample"]
    gi = f"{PROF}/{s}.IS/output/{s}.IS_genome_info.tsv"
    if not os.path.exists(gi):
        continue
    try:
        df = pd.read_csv(gi, sep="\t")
    except Exception:
        continue
    row = df[(df.genome == TARGET) & (df.breadth > 0.5)]
    if row.empty:
        continue
    cov = float(row.iloc[0]["coverage"]); br = float(row.iloc[0]["breadth"])
    if r.subject not in best or cov > best[r.subject][1]:
        best[r.subject] = (s, cov, br)

print("\nrepresentative gut profile per subject:", flush=True)
for su, (s, cov, br) in sorted(best.items()):
    print(f"  {su:5s} {s}  cov={cov:.1f}  breadth={br:.3f}", flush=True)

pairs = list(itertools.combinations(sorted(best), 2))
print(f"\n{len(pairs)} between-subject gut<->gut pairs\n", flush=True)

rows = []
for i, (sa, sb) in enumerate(pairs, 1):
    a, b = best[sa][0], best[sb][0]
    tag = f"{sa}_{sb}"
    print(f"[{i}/{len(pairs)}] {sa} ({a}) x {sb} ({b}) ...", flush=True)
    shutil.rmtree(RAM, ignore_errors=True); os.makedirs(RAM)
    for s in (a, b):
        subprocess.run(["cp", "-r", good[s], RAM], check=False)
    out = f"/dev/shm/cmp_{tag}"; shutil.rmtree(out, ignore_errors=True)
    try:
        cp = subprocess.run(
            ["inStrain", "compare", "-i", f"{RAM}/{a}.IS", f"{RAM}/{b}.IS",
             "-o", out, "-s", stb, "-p", "2"],
            capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        print("    TIMEOUT", flush=True)
        shutil.rmtree(RAM, ignore_errors=True); continue
    gw = glob.glob(f"{out}/output/*genomeWide_compare.tsv")
    if not gw:
        print(f"    no output (rc={cp.returncode}) {cp.stderr[-300:] if cp.stderr else ''}", flush=True)
    else:
        d = pd.read_csv(gw[0], sep="\t")
        pc_col = "percent_compared" if "percent_compared" in d.columns else "percent_genome_compared"
        d["subject1"], d["subject2"] = sa, sb
        d["sample1"], d["sample2"] = a, b
        rows.append(d)
        t = d[d.genome == TARGET]
        if t.empty:
            print("    P_vulgatus: no comparable row", flush=True)
        else:
            r0 = t.iloc[0]
            call = "SHARED" if (r0.popANI >= 0.999 and r0[pc_col] >= 0.5) else "different"
            print(f"    P_vulgatus popANI={r0.popANI:.5f} pc={r0[pc_col]:.3f}  -> {call}", flush=True)
    shutil.rmtree(RAM, ignore_errors=True); shutil.rmtree(out, ignore_errors=True)

if rows:
    allr = pd.concat(rows, ignore_index=True)
    allr.to_csv(OUT, sep="\t", index=False)
    print(f"\nwrote {OUT}  ({len(allr)} rows)", flush=True)
    pc_col = "percent_compared" if "percent_compared" in allr.columns else "percent_genome_compared"
    print("\n=== P_vulgatus across all between-subject gut pairs ===", flush=True)
    t = allr[allr.genome == TARGET]
    if t.empty:
        print("none comparable", flush=True)
    else:
        for _, r in t.iterrows():
            call = "SHARED" if (r.popANI >= 0.999 and r[pc_col] >= 0.5) else "different"
            print(f"  {r.subject1:5s} x {r.subject2:5s}  popANI={r.popANI:.5f}  pc={r[pc_col]:.3f}  {call}", flush=True)
else:
    print("\nno comparisons produced output", flush=True)
