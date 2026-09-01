#!/usr/bin/env python3
"""
Pairwise inStrain compare — robust workaround for a constrained box where all-N compare
OOM/hangs. Each pair stages only its 2 profiles in RAM (/dev/shm), compares, aggregates.
Pairs built for the pilot's question:
  - within-subject SAME-site over time  -> positive control (strain should persist)
  - within-subject CROSS-site (vagina x gut) -> the reservoir/sharing question
Output: /mnt/d/bioai/results/pairwise_popani.tsv  and a printed summary.
"""
import subprocess, os, glob, itertools, shutil, sys
import pandas as pd

META="/mnt/d/bioai/data/metadata_subset.tsv"
REFS="/mnt/d/bioai/refs"
PROF="/mnt/d/bioai/results/profiles"
RAM="/dev/shm/pair"
os.environ["TMPDIR"]="/home/allen/bioai_tmp"; os.makedirs(os.environ["TMPDIR"], exist_ok=True)

# completed profiles that have covT
good={}
for d in glob.glob(f"{PROF}/*.IS"):
    if os.path.exists(f"{d}/raw_data/covT.hd5"):
        good[os.path.basename(d)[:-3]]=d   # sample -> path
meta=pd.read_csv(META,sep="\t")
meta=meta[meta["sample"].isin(good)].copy()
print(f"usable profiles: {len(meta)}  (vagina={sum(meta.bodysite=='vagina')}, gut={sum(meta.bodysite=='gut')})")

def run_pair(a,b,tag):
    shutil.rmtree(RAM,ignore_errors=True); os.makedirs(RAM)
    for s in (a,b): subprocess.run(["cp","-r",good[s],RAM],check=False)
    out=f"/dev/shm/cmp_{tag}"; shutil.rmtree(out,ignore_errors=True)
    try:
        subprocess.run(["inStrain","compare","-i",f"{RAM}/{a}.IS",f"{RAM}/{b}.IS",
                        "-o",out,"-s",f"{REFS}/vagref.stb","-p","2"],
                       capture_output=True,text=True,timeout=240)
    except subprocess.TimeoutExpired:
        shutil.rmtree(RAM,ignore_errors=True); return None
    gw=glob.glob(f"{out}/output/*_genomeWide_compare.tsv")
    d=None
    if gw:
        try: d=pd.read_csv(gw[0],sep="\t")
        except Exception: d=None
    shutil.rmtree(RAM,ignore_errors=True); shutil.rmtree(out,ignore_errors=True)
    return d

pairs=[]
# same-site within-subject (positive control): up to 2 consecutive-timepoint pairs each
for (subj,site),g in meta.sort_values("timepoint").groupby(["subject","bodysite"]):
    s=g["sample"].tolist()
    for a,b in list(zip(s,s[1:]))[:2]:
        pairs.append((a,b,"within_same_site",subj,site))
# cross-site within-subject (the question): up to 3 vagina x gut pairs each
for subj,g in meta.groupby("subject"):
    v=g[g.bodysite=="vagina"]["sample"].tolist(); gut=g[g.bodysite=="gut"]["sample"].tolist()
    for a,b in list(itertools.product(v,gut))[:3]:
        pairs.append((a,b,"within_cross_site",subj,"V-G"))

print(f"running {len(pairs)} pairwise comparisons...")
rows=[]
for i,(a,b,cls,subj,site) in enumerate(pairs):
    d=run_pair(a,b,f"{i}")
    n=0
    if d is not None and len(d):
        for _,r in d.iterrows():
            rows.append(dict(subject=subj,site=site,pair_class=cls,sampleA=a,sampleB=b,
                             genome=r.get("genome"),popANI=r.get("popANI"),
                             breadth=r.get("percent_compared"),          # inStrain 1.10 column name
                             bases=r.get("compared_bases_count")))
        n=len(d)
    print(f"[{i+1}/{len(pairs)}] {cls} {subj} {a} vs {b}: {n} genome(s) compared",flush=True)

res=pd.DataFrame(rows)
res.to_csv("/mnt/d/bioai/results/pairwise_popani.tsv",sep="\t",index=False)
print("\n=== SUMMARY: shared strain = popANI>=0.99999 & breadth(percent_compared)>=0.5 ===")
if len(res):
    res["shared"]=(res["popANI"]>=0.99999)&(res["breadth"]>=0.5)
    for cls in ["within_same_site","within_cross_site"]:
        sub=res[res.pair_class==cls]
        print(f"\n{cls}: {len(sub)} genome-comparisons")
        if len(sub):
            print(sub.groupby("genome").agg(
                  n=("popANI","size"), med_popANI=("popANI","median"),
                  med_breadth=("breadth","median"), med_bases=("bases","median"),
                  shared=("shared","sum")).round(4).to_string())
else:
    print("no genome-level comparisons produced.")
print(f"\nwrote /mnt/d/bioai/results/pairwise_popani.tsv ({len(res)} rows)")
