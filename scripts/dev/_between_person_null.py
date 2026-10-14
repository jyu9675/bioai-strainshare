#!/usr/bin/env python3
"""
Between-person, SAME-SITE null for the Goltsman cohort (PRJNA288562).

Why this exists: the original 04b between-person null compared gut<->vagina pairs only.
That leaves the question the rectovaginal study actually needs answered -- do unrelated
people share strains *at the same site*? -- untested, and it was the gap that let a
between-woman P. vulgatus call in the Fijian pilot be misread as a generalist taxon
(see docs/fijian-pilot-findings.md).

Builds a proper null: N representative profiles per subject per body site, all
between-subject same-site pairs, every comparable genome retained.

Resumable: each pair's result is cached under $OUT/pairs/ and skipped on re-run.
"""
import subprocess, os, glob, itertools, shutil, sys
import pandas as pd

META = "/mnt/d/bioai/data/metadata.tsv"
REFS = "/mnt/d/bioai/refs"
PROF = "/mnt/d/bioai/results/profiles"
OUT  = "/mnt/d/bioai/results/between_person_null"
RAM  = "/dev/shm/bpn"
SITES = ("gut", "vagina")
N_PER_SUBJECT = int(os.environ.get("N_PER_SUBJECT", "2"))

os.environ["TMPDIR"] = "/home/allen/bioai_tmp"
os.makedirs(os.environ["TMPDIR"], exist_ok=True)
os.makedirs(f"{OUT}/pairs", exist_ok=True)

stb = next((p for p in (f"{REFS}/vagref.stb",) if os.path.exists(p)), None) \
      or (glob.glob(f"{REFS}/**/*.stb", recursive=True) or [None])[0]
print(f"stb: {stb}", flush=True)

good = {os.path.basename(d)[:-3]: d for d in glob.glob(f"{PROF}/*.IS")
        if os.path.exists(f"{d}/raw_data/covT.hd5")}
meta = pd.read_csv(META, sep="\t")
meta = meta[meta["sample"].isin(good)]
print(f"usable profiles: {len(meta)}", flush=True)


def richness(sample):
    """Rank profiles for comparability.

    DEPTH FIRST, then breadth of the catalogue. inStrain compare needs both members of a
    pair to cover the SAME positions deeply; a profile that touches many genomes shallowly
    produces rows that all fall under the percent_compared floor and so contribute nothing
    to the null. Ranking by genome count instead of depth was tried first and gave a pair
    with 8 comparable genomes and 0 evaluable rows.
    """
    gi = f"{PROF}/{sample}.IS/output/{sample}.IS_genome_info.tsv"
    if not os.path.exists(gi):
        return 0.0, 0
    try:
        df = pd.read_csv(gi, sep="\t")
    except Exception:
        return 0.0, 0
    ok = df[df.breadth > 0.5]
    if not len(ok):
        return 0.0, 0
    # median coverage across well-covered genomes: robust to one dominant organism
    return float(ok.coverage.median()), len(ok)


reps = {}   # (site, subject) -> [samples]
for site in SITES:
    sub = meta[meta.bodysite == site]
    for subj, grp in sub.groupby("subject"):
        scored = sorted(((richness(s), s) for s in grp["sample"]), reverse=True)
        picked = [s for (sc, s) in scored[:N_PER_SUBJECT] if sc[0] > 0]
        if picked:
            reps[(site, subj)] = picked

print("\nrepresentative profiles:", flush=True)
for (site, subj), ss in sorted(reps.items()):
    print(f"  {site:7s} {subj:5s} {' '.join(ss)}", flush=True)

pairs = []
for site in SITES:
    subjects = sorted({su for (si, su) in reps if si == site})
    for a, b in itertools.combinations(subjects, 2):
        for sa in reps[(site, a)]:
            for sb in reps[(site, b)]:
                pairs.append((site, a, b, sa, sb))
print(f"\n{len(pairs)} between-subject same-site pairs "
      f"({sum(1 for p in pairs if p[0]=='gut')} gut, "
      f"{sum(1 for p in pairs if p[0]=='vagina')} vagina)\n", flush=True)

for i, (site, suba, subb, a, b) in enumerate(pairs, 1):
    cache = f"{OUT}/pairs/{site}__{suba}_{a}__{subb}_{b}.tsv"
    if os.path.exists(cache):
        print(f"[{i}/{len(pairs)}] {site} {suba}x{subb} cached", flush=True)
        continue
    print(f"[{i}/{len(pairs)}] {site} {suba} ({a}) x {subb} ({b}) ...", flush=True)
    shutil.rmtree(RAM, ignore_errors=True); os.makedirs(RAM)
    for s in (a, b):
        subprocess.run(["cp", "-r", good[s], RAM], check=False)
    tmp = f"/dev/shm/cmp_bpn"; shutil.rmtree(tmp, ignore_errors=True)
    try:
        cp = subprocess.run(["inStrain", "compare", "-i", f"{RAM}/{a}.IS", f"{RAM}/{b}.IS",
                             "-o", tmp, "-s", stb, "-p", "2"],
                            capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        print("    TIMEOUT", flush=True); shutil.rmtree(RAM, ignore_errors=True); continue
    gw = glob.glob(f"{tmp}/output/*genomeWide_compare.tsv")
    if gw:
        d = pd.read_csv(gw[0], sep="\t")
        d["site"], d["subject1"], d["subject2"] = site, suba, subb
        d["sample1"], d["sample2"] = a, b
        d.to_csv(cache, sep="\t", index=False)
        pc = "percent_compared" if "percent_compared" in d.columns else "percent_genome_compared"
        ev = d[d[pc] >= 0.5]
        sh = ev[ev.popANI >= 0.999]
        print(f"    {len(d)} rows, {len(ev)} evaluable (pc>=0.5), {len(sh)} shared", flush=True)
    else:
        print(f"    no output (rc={cp.returncode})", flush=True)
    shutil.rmtree(RAM, ignore_errors=True); shutil.rmtree(tmp, ignore_errors=True)

files = glob.glob(f"{OUT}/pairs/*.tsv")
if files:
    allr = pd.concat([pd.read_csv(f, sep="\t") for f in files], ignore_index=True)
    allr.to_csv(f"{OUT}/between_person_null.tsv", sep="\t", index=False)
    pc = "percent_compared" if "percent_compared" in allr.columns else "percent_genome_compared"
    ev = allr[allr[pc] >= 0.5]
    print(f"\n=== {len(allr)} rows from {len(files)} pairs ===", flush=True)
    print(f"evaluable (pc>=0.5): {len(ev)}", flush=True)
    print(f"shared strains (popANI>=0.999 AND pc>=0.5): {len(ev[ev.popANI>=0.999])}", flush=True)
    naive = allr[allr.popANI >= 0.999]
    print(f"WITHOUT the breadth floor, popANI>=0.999 alone would call "
          f"{len(naive)}/{len(allr)} ({100*len(naive)/len(allr):.1f}%) shared", flush=True)
    print(f"  of those, {len(naive[naive[pc]<0.5])} are breadth artifacts", flush=True)
    print(f"\nwrote {OUT}/between_person_null.tsv", flush=True)
