#!/usr/bin/env python3
"""Print NEW within-woman gut<->vagina co-detections (species >=5x at BOTH sites) as profiles
complete. Deduplicates via a state file so each co-detection is announced once. Silent when there
is nothing new -> pairs cleanly with Monitor (one notification per genuine co-detection)."""
import glob, os
import pandas as pd
from collections import defaultdict

# Paths come from the environment so this works both on the laptop and on EC2. The driver exports
# HMP_OUT (the run dir) and HMP_META (the manifest) before calling it.
F     = os.environ.get("HMP_OUT",  "/mnt/d/bioai/results/hmp_full")
META  = os.environ.get("HMP_META", "/mnt/c/Jeanyu/BIOAI/scripts/dev/hmp_metadata.tsv")
STATE = F + "/.codetect_seen"
FLOOR = float(os.environ.get("HMP_FLOOR", "5.0"))

def cls(bs):
    b = str(bs).lower()
    if b in ("gut", "stool", "rectum", "rectal"): return "A"
    if "vag" in b or b in ("cervix", "posterior_fornix", "mid_vagina", "vaginal_introitus"): return "B"
    return "?"

meta = pd.read_csv(META, sep="\t")
m = {r["sample"]: (str(r["subject"]), str(r["bodysite"])) for _, r in meta.iterrows()}

cov = {}
for d in glob.glob(F + "/profiles/*.IS"):
    if not os.path.exists(os.path.join(d, ".done")):      # only finished profiles
        continue
    s = os.path.basename(d)[:-3]
    fs = glob.glob(os.path.join(d, "output", "*genome_info.tsv"))
    if not fs:
        continue
    try:
        gi = pd.read_csv(fs[0], sep="\t")
    except Exception:
        continue
    cov[s] = {str(r["genome"]): (float(r["coverage"]), float(r["breadth"])) for _, r in gi.iterrows()}

best = defaultdict(dict)   # subject -> {(class, genome): (cov, breadth)}
for s, gd in cov.items():
    if s not in m:
        continue
    subj, bs = m[s]; c = cls(bs)
    if c == "?":
        continue
    for g, (cv, br) in gd.items():
        k = (c, g)
        if cv > best[subj].get(k, (-1, 0))[0]:
            best[subj][k] = (cv, br)

seen = set()
if os.path.exists(STATE):
    seen = {ln.strip() for ln in open(STATE)}

new = []
for subj, d in best.items():
    for g in {g for (_, g) in d}:
        a = d.get(("A", g)); b = d.get(("B", g))
        if a and b and a[0] >= FLOOR and b[0] >= FLOOR:
            key = f"{subj}|{g}"
            if key not in seen:
                new.append((subj, g, a, b)); seen.add(key)

if new:
    with open(STATE, "a") as f:
        for subj, g, a, b in sorted(new):
            flag = "EVALUABLE" if (a[1] >= 0.5 and b[1] >= 0.5) else "low-breadth/UNRESOLVED"
            print(f"CO-DETECTION  woman {subj}  {g.replace('.fna','')}  "
                  f"gut {a[0]:.0f}x/br{a[1]:.2f}  vagina {b[0]:.0f}x/br{b[1]:.2f}  [{flag}]",
                  flush=True)
            f.write(key + "\n")
