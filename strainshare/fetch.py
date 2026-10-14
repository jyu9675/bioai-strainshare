"""Fetch public paired-site metagenome datasets from ENA and build a strainshare sample sheet.

Turns an ENA BioProject into a ready `samples.tsv` (sample, subject, timepoint, bodysite,
fq1, fq2) by parsing the sample alias into a subject id + a site code. Many cohorts encode
this in the alias (e.g. `95V` = subject 95, vaginal; `90C` = subject 90, cervical), so a
regex + a site-code map recovers the cross-site pairing needed for strain-sharing analysis.
"""
import io
import os
import re
import urllib.parse
import urllib.request

import pandas as pd

ENA_API = "https://www.ebi.ac.uk/ena/portal/api/filereport"
DEFAULT_ALIAS_RE = r"^(?P<subject>\d+)(?P<site>[A-Za-z]+)$"
DEFAULT_FIELDS = ("run_accession", "sample_alias", "library_strategy", "fastq_ftp", "read_count")


def query_ena(bioproject, fields=DEFAULT_FIELDS, timeout=90):
    q = urllib.parse.urlencode({"accession": bioproject, "result": "read_run",
                                "fields": ",".join(fields), "format": "tsv"})
    with urllib.request.urlopen(f"{ENA_API}?{q}", timeout=timeout) as r:
        text = r.read().decode()
    return pd.read_csv(io.StringIO(text), sep="\t")


def parse_alias(alias, site_map, alias_re=DEFAULT_ALIAS_RE):
    """(subject, bodysite) from an alias; bodysite is None if the site code isn't mapped."""
    m = re.match(alias_re, str(alias))
    if not m:
        return None, None
    return m.group("subject"), site_map.get(m.group("site").upper())


def build_sheet(runs, site_map, alias_re=DEFAULT_ALIAS_RE, paired_only=True,
                max_subjects=None, wgs_only=True):
    """Build the strainshare sample sheet from an ENA read_run table."""
    df = runs.copy()
    if wgs_only and "library_strategy" in df.columns:
        df = df[df.library_strategy.astype(str).str.upper() == "WGS"]
    df = df[df.fastq_ftp.notna() & df.fastq_ftp.astype(str).str.contains(";")]  # paired reads only
    rows = []
    for _, r in df.iterrows():
        subject, bodysite = parse_alias(r.sample_alias, site_map, alias_re)
        if bodysite is None:
            continue
        f1, f2 = str(r.fastq_ftp).split(";")[:2]
        rows.append(dict(sample=str(r.sample_alias), subject=subject, timepoint=1,
                         bodysite=bodysite, fq1="https://" + f1, fq2="https://" + f2))
    sheet = pd.DataFrame(rows, columns=["sample", "subject", "timepoint", "bodysite", "fq1", "fq2"])
    if paired_only and len(sheet):
        n_sites = sheet.groupby("subject").bodysite.nunique()
        sheet = sheet[sheet.subject.isin(n_sites[n_sites >= 2].index)]
    if max_subjects and len(sheet):
        keep = sorted(sheet.subject.unique(), key=lambda s: (len(s), s))[:max_subjects]
        sheet = sheet[sheet.subject.isin(keep)]
    return sheet.sort_values(["subject", "bodysite"]).reset_index(drop=True)


def parse_site_map(s):
    """'V=vagina,C=cervix,R=rectum' -> {'V':'vagina', ...} (keys upper-cased)."""
    out = {}
    for part in s.split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip().upper()] = v.strip()
    return out


def download(sheet, outdir):
    """Download the fastqs to outdir/fastq and rewrite fq1/fq2 to local paths."""
    fq_dir = os.path.join(outdir, "fastq")
    os.makedirs(fq_dir, exist_ok=True)
    sheet = sheet.copy()
    for i, r in sheet.iterrows():
        for col, tag in [("fq1", "1"), ("fq2", "2")]:
            dest = os.path.join(fq_dir, f"{r['sample']}_{tag}.fq.gz")
            if not os.path.exists(dest):
                print(f"[fetch] downloading {r['sample']} R{tag} ...")
                urllib.request.urlretrieve(r[col], dest)
            sheet.at[i, col] = dest
    return sheet


def fetch_to_sheet(bioproject, outdir, site_map, alias_re=DEFAULT_ALIAS_RE,
                   paired_only=True, max_subjects=None, do_download=False):
    os.makedirs(outdir, exist_ok=True)
    runs = query_ena(bioproject)
    sheet = build_sheet(runs, site_map, alias_re, paired_only, max_subjects)
    if do_download and len(sheet):
        sheet = download(sheet, outdir)
    path = os.path.join(outdir, "samples.tsv")
    # force LF endings — the sheet is consumed by bash/Snakemake, where a CRLF trailing \r
    # corrupts the last field (e.g. the fastq URL).
    sheet.to_csv(path, sep="\t", index=False, lineterminator="\n")
    return sheet, path
