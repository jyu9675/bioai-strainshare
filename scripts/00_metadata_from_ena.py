#!/usr/bin/env python3
"""
Build metadata.tsv AND per-site download lists for PRJNA288562 directly from ENA,
by parsing the free-text `sample_title` (this dataset encodes everything there, e.g.
"Subject M4 distal gut specimen collected on gestational day 147").

Outputs (in data/):
  metadata.tsv        sample  subject  timepoint  bodysite   (all WGS runs)
  download_all.txt    fastq URLs, all WGS
  download_vg.txt     fastq URLs, vagina+gut only (what the gut<->vagina pilot needs)

Usage: python 00_metadata_from_ena.py
"""
import re, sys, urllib.request, os

ACC = "PRJNA288562"
FIELDS = "run_accession,library_strategy,sample_title,fastq_ftp,fastq_bytes"
URL = f"https://www.ebi.ac.uk/ena/portal/api/filereport?accession={ACC}&result=read_run&fields={FIELDS}&format=tsv"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
os.makedirs(DATA, exist_ok=True)

SITE_RULES = [(r"vagin|posterior fornix|cervic", "vagina"),
              (r"distal gut|stool|feces|faece|rectal|gut specimen", "gut"),
              (r"saliva|oral|tooth|gum|buccal", "oral")]

def site_of(title):
    t = title.lower()
    for pat, lab in SITE_RULES:
        if re.search(pat, t):
            return lab
    return None

raw = urllib.request.urlopen(URL, timeout=120).read().decode()
lines = raw.strip().split("\n")
hdr = lines[0].split("\t")
ix = {c: i for i, c in enumerate(hdr)}

meta_rows, all_urls, vg_urls = [], [], []
site_ct, site_gb = {}, {}
for ln in lines[1:]:
    f = ln.split("\t")
    if f[ix["library_strategy"]] != "WGS":
        continue
    title = f[ix["sample_title"]]
    run = f[ix["run_accession"]]
    subj_m = re.search(r"Subject\s+(\S+)", title)
    day_m = re.search(r"gestational day\s+(\d+)", title, re.I)
    site = site_of(title)
    subject = subj_m.group(1) if subj_m else "NA"
    timepoint = int(day_m.group(1)) if day_m else ""
    meta_rows.append(f"{run}\t{subject}\t{timepoint}\t{site or 'NA'}")

    ftp = f[ix["fastq_ftp"]] if ix["fastq_ftp"] < len(f) else ""
    urls = ["https://" + u for u in ftp.split(";") if u]
    byts = sum(int(b) for b in f[ix["fastq_bytes"]].split(";") if b) if ix["fastq_bytes"] < len(f) and f[ix["fastq_bytes"]] else 0
    all_urls += urls
    site_ct[site] = site_ct.get(site, 0) + 1
    site_gb[site] = site_gb.get(site, 0) + byts / 1e9
    if site in ("vagina", "gut"):
        vg_urls += urls

with open(f"{DATA}/metadata.tsv", "w") as fh:
    fh.write("sample\tsubject\ttimepoint\tbodysite\n" + "\n".join(meta_rows) + "\n")
with open(f"{DATA}/download_all.txt", "w") as fh:
    fh.write("\n".join(all_urls) + "\n")
with open(f"{DATA}/download_vg.txt", "w") as fh:
    fh.write("\n".join(vg_urls) + "\n")

print("WGS runs by body site (count, GB):")
for s in sorted(site_ct, key=lambda x: (x is None, x)):
    print(f"  {str(s):8s}  n={site_ct[s]:3d}  {site_gb[s]:6.1f} GB")
vg_gb = site_gb.get("vagina", 0) + site_gb.get("gut", 0)
print(f"\nvagina+gut: n={site_ct.get('vagina',0)+site_ct.get('gut',0)}  {vg_gb:.1f} GB  "
      f"-> {len(vg_urls)} fastq files in data/download_vg.txt")
print(f"wrote data/metadata.tsv ({len(meta_rows)} rows), download_all.txt, download_vg.txt")
