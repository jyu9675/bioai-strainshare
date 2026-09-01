#!/usr/bin/env python3
# Summarize genome detection across completed profiles, split by body site.
import pandas as pd
R="/mnt/d/bioai/results"; D="/mnt/d/bioai/data"
c=pd.read_csv(f"{R}/composition.tsv",sep="\t")
m=pd.read_csv(f"{D}/metadata_subset.tsv",sep="\t").set_index("sample")
c["genome"]=c["genome"].str.replace(".fna","",regex=False)
c=c.join(m,on="sample")
c["detected"]=(c["breadth"]>=0.5)&(c["coverage"]>=5)

print(f"samples profiled: {c['sample'].nunique()}  (by site: "
      + ", ".join(f"{k}={v}" for k,v in c.drop_duplicates('sample')['bodysite'].value_counts().items())+")")
print("\n=== genome detection (breadth>=0.5 & cov>=5x), samples by site ===")
det=c[c["detected"]]
tab=det.pivot_table(index="genome",columns="bodysite",values="sample",aggfunc="nunique",fill_value=0)
tab["total_samples"]=tab.sum(axis=1)
tab["median_cov"]=det.groupby("genome")["coverage"].median().round(1)
print(tab.sort_values("total_samples",ascending=False).to_string())

print("\n=== subjects with same genome detected in BOTH their vagina AND gut (sharing candidates) ===")
d2=det.groupby(["subject","genome"])["bodysite"].agg(lambda x:set(x))
both=d2[d2.apply(lambda s:{"vagina","gut"}<=s)]
if len(both):
    for (subj,gen) in both.index: print(f"  {subj:4s}  {gen}")
else:
    print("  (none yet among completed profiles)")
