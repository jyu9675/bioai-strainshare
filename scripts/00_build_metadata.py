#!/usr/bin/env python3
"""
Build data/metadata.tsv  (sample  subject  timepoint  bodysite)  from the SRA Run Selector
metadata (SraRunTable.csv) and/or the ENA run table produced by 01_download_wgs.sh.

The exact column names in PRJNA288562's SraRunTable aren't known until you download it,
so this auto-detects common column aliases, normalises body sites to {vagina, gut, oral},
and REPORTS anything it can't classify instead of silently guessing.

Usage:
  python 00_build_metadata.py --srarun ../data/SraRunTable.csv --out ../data/metadata.tsv
  # optionally restrict to the WGS runs you actually downloaded:
  python 00_build_metadata.py --srarun ../data/SraRunTable.csv --wgs ../data/wgs_runs.tsv --out ../data/metadata.tsv

If auto-detection misses a field, rerun with explicit overrides, e.g.
  --col-subject host_subject_id --col-site host_body_site --col-time collection_week
"""
import argparse, re, sys
import pandas as pd

# candidate column names (lowercased, non-alnum stripped) for each target field
ALIASES = {
    "sample":  ["run", "runaccession", "accession"],
    "subject": ["hostsubjectid", "subjectid", "subject", "hostid", "individual", "patientid",
                "isolationsource"],  # last-resort; alias often encodes subject
    "site":    ["hostbodysite", "bodysite", "isolationsource", "source", "hostbodyproduct",
                "tissue", "env_medium", "sampletype"],
    "time":    ["collectionweek", "gestationalage", "gestationweek", "week", "timepoint",
                "collectiondate", "day", "trimester", "age"],
}

# body-site string -> normalised label
SITE_RULES = [
    (r"vagin", "vagina"),
    (r"cervic", "vagina"),
    (r"stool|feces|faece|gut|rectal|rectum|intestin", "gut"),
    (r"saliva|oral|tooth|gum|plaque|buccal|mouth", "oral"),
]


def norm(s):  # normalise a column name for matching
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def find_col(cols, aliases, override=None):
    if override:
        if override in cols:
            return override
        sys.exit(f"[error] --override column '{override}' not in table. Columns: {list(cols)}")
    normmap = {norm(c): c for c in cols}
    for a in aliases:
        if a in normmap:
            return normmap[a]
    # loose contains-match
    for a in aliases:
        for nc, orig in normmap.items():
            if a in nc:
                return orig
    return None


def norm_site(val):
    v = str(val).lower()
    for pat, label in SITE_RULES:
        if re.search(pat, v):
            return label
    return None  # unclassified -> reported


def parse_time(val):
    """Pull a numeric gestational week if present; else leave raw string for manual fix."""
    m = re.search(r"(\d+(\.\d+)?)", str(val))
    return float(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--srarun", required=True, help="SraRunTable.csv from SRA Run Selector")
    ap.add_argument("--wgs", help="wgs_runs.tsv (restrict to these run accessions)")
    ap.add_argument("--out", default="../data/metadata.tsv")
    ap.add_argument("--col-subject"); ap.add_argument("--col-site"); ap.add_argument("--col-time")
    a = ap.parse_args()

    sep = "\t" if a.srarun.endswith((".tsv", ".txt")) else ","
    df = pd.read_csv(a.srarun, sep=sep, dtype=str)
    cols = df.columns

    c_run  = find_col(cols, ALIASES["sample"])
    c_subj = find_col(cols, ALIASES["subject"], a.col_subject)
    c_site = find_col(cols, ALIASES["site"], a.col_site)
    c_time = find_col(cols, ALIASES["time"], a.col_time)

    missing = [n for n, c in [("run", c_run), ("subject", c_subj), ("site", c_site)] if c is None]
    if missing:
        print(f"[error] could not auto-detect: {missing}\nAvailable columns:\n  " +
              "\n  ".join(cols), file=sys.stderr)
        print("Rerun with --col-subject / --col-site / --col-time overrides.", file=sys.stderr)
        sys.exit(1)
    print(f"[cols] run={c_run}  subject={c_subj}  site={c_site}  time={c_time}")

    out = pd.DataFrame({
        "sample":   df[c_run],
        "subject":  df[c_subj],
        "timepoint": df[c_time].map(parse_time) if c_time else pd.NA,
        "bodysite": df[c_site].map(norm_site),
    })

    if a.wgs:  # keep only downloaded WGS runs
        keep = set(pd.read_csv(a.wgs, sep="\t")["run_accession"])
        out = out[out["sample"].isin(keep)]

    unclassified = out[out["bodysite"].isna()]
    if len(unclassified):
        print(f"[warn] {len(unclassified)} rows have unrecognised body site "
              f"(values: {sorted(df.loc[unclassified.index, c_site].dropna().unique())[:8]}). "
              "Add a rule to SITE_RULES or fix by hand.", file=sys.stderr)
    if c_time is None:
        print("[warn] no timepoint column detected -> Fig 3 (directionality) needs it; "
              "set --col-time.", file=sys.stderr)

    out.to_csv(a.out, sep="\t", index=False)
    print(f"[done] wrote {len(out)} rows -> {a.out}")
    print(out["bodysite"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
