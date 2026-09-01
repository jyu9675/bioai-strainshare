#!/usr/bin/env python3
# Visualize the pairwise popANI result: popANI vs breadth (percent_compared),
# same-site (positive control) vs cross-site (the sharing question).
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

d=pd.read_csv("/mnt/d/bioai/results/pairwise_popani.tsv",sep="\t")
d["genome"]=d["genome"].str.replace(".fna","",regex=False)
d=d.dropna(subset=["popANI","breadth"])

fig,ax=plt.subplots(figsize=(7.5,5.5))
styles={"within_same_site":("#2a9d3f","o","same-site over time (positive control)"),
        "within_cross_site":("#d1495b","^","vagina × gut (sharing question)")}
for cls,(col,mk,lab) in styles.items():
    s=d[d.pair_class==cls]
    ax.scatter(s["breadth"],s["popANI"],c=col,marker=mk,s=55,alpha=0.75,edgecolor="white",linewidth=0.5,label=lab)
# same-strain quadrant
ax.axhline(0.99999,ls="--",color="grey",lw=1); ax.axvline(0.5,ls=":",color="grey",lw=1)
ax.text(0.52,0.99991,"same-strain zone\n(popANI≥99.999% & ≥50% compared)",fontsize=8,color="#444")
ax.set_xlabel("fraction of genome compared (percent_compared)")
ax.set_ylabel("popANI")
ax.set_title("Strain identity: same-site persistence vs gut↔vagina sharing\n(4 subjects, 38 profiles, shallow pilot)")
ax.set_ylim(0.975,1.0005)
ax.legend(fontsize=8,loc="lower right")
# annotate: cross-site points cluster at far left (tiny breadth)
fig.tight_layout(); fig.savefig("/mnt/d/bioai/results/figures/pairwise_popANI_vs_breadth.png",dpi=150)
import os; os.makedirs("/mnt/d/bioai/results/figures",exist_ok=True)
fig.savefig("/mnt/d/bioai/results/figures/pairwise_popANI_vs_breadth.png",dpi=150)
print("wrote /mnt/d/bioai/results/figures/pairwise_popANI_vs_breadth.png")
print(f"same-site points: {sum(d.pair_class=='within_same_site')}, cross-site: {sum(d.pair_class=='within_cross_site')}")
