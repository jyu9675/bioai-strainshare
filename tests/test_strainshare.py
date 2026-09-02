"""Unit tests for the strainshare package — planted-truth synthetic data with known answers."""
import numpy as np
import pandas as pd
import pytest

from strainshare import STANDARD, load_config, __version__
from strainshare import analysis, generalist, direction, benchmark, plots


# ---------- fixtures ----------
@pytest.fixture
def synthetic():
    """3 subjects x {vagina,gut} x {wk12,wk30}, with planted truths:
    - L_crispatus: within-person gut<->vagina shared (S1,S2), dissimilar community -> translocation;
      S1 also present in gut at wk12 -> direction gut_to_vagina; S2 only wk30 -> unresolved
    - G_vaginalis: S3 within gut<->vagina shared but S3 gut made vagina-like -> contamination
    - E_coli: shared between UNRELATED people (S1 gut <-> S2 vagina) -> generalist
    """
    rows = []
    for subj in ["S1", "S2", "S3"]:
        for site in ["vagina", "gut"]:
            for wk in [12, 30]:
                rows.append(dict(sample=f"{subj}_{site}_{wk}", subject=subj, timepoint=wk, bodysite=site))
    meta = pd.DataFrame(rows)

    species = ["L_crispatus", "L_iners", "G_vaginalis", "P_bivia", "B_fragilis", "F_prausnitzii", "E_coli"]
    mpa = pd.DataFrame(0.0, index=species, columns=meta["sample"])
    for c in meta["sample"]:
        if "vagina" in c:
            mpa.loc["L_crispatus", c] = 70; mpa.loc["L_iners", c] = 10; mpa.loc["G_vaginalis", c] = 4
        else:
            mpa.loc["B_fragilis", c] = 30; mpa.loc["F_prausnitzii", c] = 30
            mpa.loc["P_bivia", c] = 10; mpa.loc["G_vaginalis", c] = 3
    for wk in [12, 30]:  # S3 gut looks vagina-like -> contamination
        c = f"S3_gut_{wk}"
        mpa[c] = 0.0
        mpa.loc["L_crispatus", c] = 70; mpa.loc["G_vaginalis", c] = 8; mpa.loc["L_iners", c] = 10

    def row(g, a, b, pop, br=0.8):
        return dict(genome=g, name1=a, name2=b, popANI=pop, percent_genome_compared=br)

    C = []
    for subj in ["S1", "S2"]:
        C.append(row("L_crispatus", f"{subj}_vagina_30", f"{subj}_gut_30", 0.99995))
    C.append(row("L_crispatus", "S1_vagina_30", "S2_gut_30", 0.9970))       # between, not shared
    C.append(row("L_crispatus", "S1_gut_12", "S1_gut_30", 0.99999))         # same-site -> direction
    C.append(row("G_vaginalis", "S3_vagina_30", "S3_gut_30", 0.99996))      # contamination
    C.append(row("L_iners", "S1_vagina_12", "S1_vagina_30", 0.99999))       # same-site control
    C.append(row("P_bivia", "S1_gut_30", "S2_gut_30", 0.9950))              # between, negative
    C.append(row("E_coli", "S1_gut_30", "S2_vagina_30", 0.99999))           # between gut-vagina -> generalist
    compare = pd.DataFrame(C)
    return compare, meta, mpa


# ---------- config ----------
def test_standard_shape():
    assert STANDARD["shared_strain"]["popani_primary"] == 0.999
    assert STANDARD["shared_strain"]["breadth_min"] == 0.5
    assert STANDARD["direction"]["min_timepoints"] == 2


def test_load_config_fallback(tmp_path):
    cfg = load_config(str(tmp_path / "does_not_exist.yaml"))
    assert cfg["shared_strain"]["popani_primary"] == 0.999  # falls back to defaults


def test_version():
    assert __version__ == "0.1.0"


# ---------- analysis (M1/M2) ----------
def test_analyze_classes_and_verdicts(synthetic):
    compare, meta, mpa = synthetic
    out = analysis.analyze(compare, meta, mpa)
    cand = out["translocation_candidates"].set_index("genome")
    assert (cand.loc["L_crispatus", "verdict"] == "translocation_candidate").all()
    assert "contamination_suspect" in cand.loc["G_vaginalis", "verdict"]
    # E_coli is a between-person shared pair, not a within candidate
    assert "E_coli" not in cand.index


def test_within_between_null(synthetic):
    compare, meta, mpa = synthetic
    swb = analysis.analyze(compare, meta, mpa)["species_within_between"]
    # L_crispatus shared within-person, not between -> positive within_minus_between
    assert swb.loc["L_crispatus", "within_shared_rate"] > swb.loc["L_crispatus", "between_shared_rate"]


# ---------- generalist (M5) ----------
def test_generalist_flag(synthetic):
    compare, meta, mpa = synthetic
    out = analysis.analyze(compare, meta, mpa)
    flags, scored = generalist.run(out["pairs_tagged"], candidates=out["translocation_candidates"])
    assert bool(flags.loc["E_coli", "is_generalist"]) is True
    assert bool(flags.loc["L_crispatus", "is_generalist"]) is False


# ---------- direction (M4) ----------
def test_direction(synthetic):
    compare, meta, mpa = synthetic
    out = analysis.analyze(compare, meta, mpa)
    d = direction.run(out["translocation_candidates"], out["pairs_tagged"], meta).set_index("subject")
    assert d.loc["S1", "direction"] == "gut_to_vagina"
    assert d.loc["S2", "direction"] == "direction_unresolved"


# ---------- benchmark ----------
def test_benchmark_selftest():
    df = benchmark.selftest()
    # sensitivity rises with coverage; specificity stays high
    s_lo = df[(df.method == "inStrain") & (df.coverage == 0.5)].sensitivity.iloc[0]
    s_hi = df[(df.method == "inStrain") & (df.coverage == 30)].sensitivity.iloc[0]
    assert s_hi > s_lo


def test_direction_call_helper():
    # gut wk12 + vagina wk30 -> gut_to_vagina
    st = [("gut", 12), ("gut", 30), ("vagina", 30)]
    assert direction.call_direction(st, 2)[0] == "gut_to_vagina"
    # single timepoint -> unresolved
    assert direction.call_direction([("gut", 30), ("vagina", 30)], 2)[0] == "direction_unresolved"


def test_plots_smoke(synthetic, tmp_path):
    compare, meta, mpa = synthetic
    out = analysis.analyze(compare, meta, mpa)
    p = str(tmp_path / "diag.png")
    conf = plots.popani_breadth(out["pairs_tagged"], p)
    import os
    assert os.path.exists(p)
    assert len(conf) >= 0


# ---------- Item 4: arbitrary site pairs ----------
@pytest.fixture
def oral_gut():
    """Same planted structure but sites are oral<->gut, to prove site-pair generalization."""
    rows = []
    for subj in ["P1", "P2"]:
        for site in ["oral", "gut"]:
            for wk in [1, 8]:
                rows.append(dict(sample=f"{subj}_{site}_{wk}", subject=subj, timepoint=wk, bodysite=site))
    meta = pd.DataFrame(rows)
    species = ["Strep_mutans", "B_fragilis"]
    mpa = pd.DataFrame(0.0, index=species, columns=meta["sample"])
    for c in meta["sample"]:
        if "oral" in c:
            mpa.loc["Strep_mutans", c] = 60
        else:
            mpa.loc["B_fragilis", c] = 60

    def row(g, a, b, pop, br=0.8):
        return dict(genome=g, name1=a, name2=b, popANI=pop, percent_genome_compared=br)

    C = [
        row("Strep_mutans", "P1_oral_8", "P1_gut_8", 0.99996),   # within-person oral<->gut shared
        row("Strep_mutans", "P1_oral_1", "P1_oral_8", 0.99999),  # oral over time -> direction
        row("Strep_mutans", "P1_oral_8", "P2_gut_8", 0.9960),    # between, not shared
    ]
    return pd.DataFrame(C), meta, mpa


def test_fetch_parse_and_sheet():
    from strainshare import fetch
    smap = fetch.parse_site_map("V=vagina,C=cervix,R=rectum")
    assert fetch.parse_alias("95V", smap) == ("95", "vagina")
    assert fetch.parse_alias("90C", smap) == ("90", "cervix")
    assert fetch.parse_alias("weird_id", smap) == (None, None)

    runs = pd.DataFrame([
        dict(sample_alias="1V", library_strategy="WGS", fastq_ftp="host/1V_1.fq.gz;host/1V_2.fq.gz"),
        dict(sample_alias="1C", library_strategy="WGS", fastq_ftp="host/1C_1.fq.gz;host/1C_2.fq.gz"),
        dict(sample_alias="2V", library_strategy="WGS", fastq_ftp="host/2V_1.fq.gz;host/2V_2.fq.gz"),  # unpaired subject
        dict(sample_alias="3V", library_strategy="16S", fastq_ftp="host/3V_1.fq.gz;host/3V_2.fq.gz"),  # not WGS
    ])
    sheet = fetch.build_sheet(runs, smap, paired_only=True)
    # only subject 1 has two sites -> kept; subject 2 (single site) and 3 (16S) dropped
    assert set(sheet.subject) == {"1"}
    assert set(sheet.bodysite) == {"vagina", "cervix"}
    assert sheet.fq1.str.startswith("https://").all()


def test_site_pair_generalization(oral_gut):
    compare, meta, mpa = oral_gut
    cfg = dict(STANDARD)
    cfg["site_pair"] = ["oral", "gut"]
    out = analysis.analyze(compare, meta, mpa, cfg)
    # class label follows the configured sites
    assert "within_oral_gut" in set(out["pairs_tagged"].pair_class)
    # oral<->gut shared strain detected and oriented oral_to_gut (oral wk1 precedes gut wk8)
    d = direction.run(out["translocation_candidates"], out["pairs_tagged"], meta, cfg)
    assert (d.direction == "oral_to_gut").any()
