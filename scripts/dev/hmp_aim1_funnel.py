#!/usr/bin/env python3
"""
Aim-1 funnel for stool/rectum <-> vagina strain sharing (HMP n=34 & any paired cohort).

Implements the integrity-first pipeline:
    99 samples -> QC/coverage -> EVALUABLE stool-vagina comparisons -> shared species
    -> shared strains -> individual-specific (within vs between) -> longitudinal candidates

CORE RULE: an organism that is below the coverage/breadth floor at EITHER site of a woman is
labelled NOT_EVALUABLE for that woman and is NEVER counted as "not shared". Only comparisons that
are actually powered (both sites >= floor, and inStrain compared >= breadth_min of the genome) can
be called shared / not-shared.

Inputs (all produced by _hmp_run.sh / _cx_test.sh):
  --profiles DIR   directory of <sample>.IS inStrain profiles (uses output/*genome_info.tsv)
  --compare FILE   inStrain genomeWide_compare.tsv (popANI, percent_compared, SNP counts)
  --meta FILE      sample<TAB>subject<TAB>timepoint<TAB>bodysite
  --out DIR        output directory

Thresholds default to the strainshare STANDARD; the ~10x confident-popANI floor (from the
reads benchmark) is applied as a confidence tier, not a hard cutoff.
"""
import argparse, glob, os, sys
import pandas as pd
import numpy as np

SITE_A = {"gut", "stool", "rectum", "rectal", "feces", "faeces"}          # the gut/rectal reservoir
SITE_B = {"vagina", "vaginal", "posterior_fornix", "mid_vagina",
          "vaginal_introitus", "cervix"}                                   # the vaginal target

def clean(name):
    name = str(name)
    for s in (".sorted.bam", ".bam", ".IS", ".fastq", ".fq"):
        if name.endswith(s):
            name = name[: -len(s)]
    return name

def site_class(bs):
    b = str(bs).strip().lower().replace(" ", "_").replace("g_dna_", "")
    if b in SITE_A: return "A"
    if b in SITE_B: return "B"
    # substring fallback
    if any(k in b for k in SITE_A): return "A"
    if any(k in b for k in SITE_B): return "B"
    return "?"

def load_coverage(profiles_dir):
    """sample -> {genome -> (coverage, breadth)} from inStrain genome_info.tsv."""
    cov = {}
    for d in sorted(glob.glob(os.path.join(profiles_dir, "*.IS"))):
        s = clean(os.path.basename(d))
        fs = glob.glob(os.path.join(d, "output", "*genome_info.tsv"))
        if not fs:
            continue
        gi = pd.read_csv(fs[0], sep="\t")
        ccol = "coverage" if "coverage" in gi.columns else gi.columns[1]
        bcol = "breadth" if "breadth" in gi.columns else ("breadth_minCov" if "breadth_minCov" in gi.columns else None)
        cov[s] = {}
        for _, r in gi.iterrows():
            b = float(r[bcol]) if bcol else np.nan
            cov[s][str(r["genome"])] = (float(r[ccol]), b)
    return cov

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", required=True)
    ap.add_argument("--compare", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--out", default="aim1_funnel")
    ap.add_argument("--cov-floor", type=float, default=5.0, help="min coverage to be evaluable at a site")
    ap.add_argument("--cov-confident", type=float, default=10.0, help="coverage for a confident popANI (benchmark)")
    ap.add_argument("--breadth-min", type=float, default=0.5, help="min genome breadth compared")
    ap.add_argument("--popani-shared", type=float, default=0.999, help="shared-strain popANI threshold")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    meta = pd.read_csv(a.meta, sep="\t")
    meta["sample"] = meta["sample"].map(clean)
    meta["cls"] = meta["bodysite"].map(site_class)
    smeta = meta.set_index("sample")
    subj = smeta["subject"].astype(str).to_dict()
    cls  = smeta["cls"].to_dict()
    tp   = smeta["timepoint"].to_dict() if "timepoint" in smeta else {}

    cov = load_coverage(a.profiles)

    cmp = pd.read_csv(a.compare, sep="\t")
    cmp["s1"] = cmp["name1"].map(clean); cmp["s2"] = cmp["name2"].map(clean)
    brcol = "percent_compared" if "percent_compared" in cmp.columns else "percent_genome_compared"

    def cov_of(sample, genome):
        return cov.get(sample, {}).get(genome, (0.0, 0.0))

    # ---- iterate every compare row, classify as within/between x A-B/A-A/B-B --------------
    rows = []
    for _, r in cmp.iterrows():
        s1, s2, g = r["s1"], r["s2"], str(r["genome"])
        if s1 not in cls or s2 not in cls:
            continue
        c1, c2 = cls[s1], cls[s2]
        if "?" in (c1, c2):
            continue
        pair_sites = "".join(sorted([c1, c2]))            # 'AB','AA','BB'
        within = subj.get(s1) == subj.get(s2)
        cov1, br1 = cov_of(s1, g); cov2, br2 = cov_of(s2, g)
        pc = float(r[brcol]); pop = float(r["popANI"])
        # evaluability of THIS comparison
        both_cov = min(cov1, cov2) >= a.cov_floor
        breadth_ok = pc >= a.breadth_min
        evaluable = both_cov and breadth_ok
        conf = "confident" if min(cov1, cov2) >= a.cov_confident else ("low_cov" if both_cov else "below_floor")
        if not evaluable:
            verdict = "NOT_EVALUABLE"
        elif pop >= a.popani_shared:
            verdict = "SHARED_STRAIN"
        else:
            verdict = "not_shared"
        rows.append(dict(genome=g, s1=s1, s2=s2, subj1=subj.get(s1), subj2=subj.get(s2),
                         pair_sites=pair_sites, within=within,
                         cov1=round(cov1, 1), cov2=round(cov2, 1),
                         min_cov=round(min(cov1, cov2), 1), breadth_compared=round(pc, 3),
                         popANI=round(pop, 6), confidence=conf, verdict=verdict))
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(a.out, "all_comparisons.tsv"), sep="\t", index=False)

    # ---- the funnel: focus on cross-site A<->B --------------------------------------------
    ab = R[R.pair_sites == "AB"].copy()
    within_ab  = ab[ab.within]
    between_ab = ab[~ab.within]
    eval_within = within_ab[within_ab.verdict != "NOT_EVALUABLE"]
    shared      = within_ab[within_ab.verdict == "SHARED_STRAIN"]
    not_eval    = within_ab[within_ab.verdict == "NOT_EVALUABLE"]

    women = sorted(set(subj.values()))
    n_samples = len(smeta)
    # DETECTION (co-occurrence) = coverage >= floor at a site. Breadth is about COMPARABILITY,
    # not presence, so it is deliberately NOT required here — a species present at both sites but
    # too sparse to strain-type is an UNRESOLVED candidate, never a negative.
    best = {}   # (subject, class, genome) -> (max_cov, breadth_at_that_cov)
    for s, gd in cov.items():
        if s not in subj: continue
        k0 = (subj[s], cls.get(s, "?"))
        for g, (c, b) in gd.items():
            key = (k0[0], k0[1], g)
            if c > best.get(key, (-1, 0))[0]:
                best[key] = (c, b)
    detected = {}   # (subject, genome) -> set of classes with cov>=floor
    for (sj, cl, g), (c, b) in best.items():
        if c >= a.cov_floor:
            detected.setdefault((sj, g), set()).add(cl)
    shared_species_women = {k for k, v in detected.items() if {"A", "B"} <= v}   # co-detected A & B
    shared_species = sorted({g for (_, g) in shared_species_women})

    # For every co-detected (woman, genome): coverage/breadth at each site + the within-woman
    # compare row if inStrain formed one -> classify SHARED / not_shared / NOT_EVALUABLE.
    codet_rows = []
    for (sj, g) in sorted(shared_species_women):
        cA, bA = best.get((sj, "A", g), (0, 0)); cB, bB = best.get((sj, "B", g), (0, 0))
        row = within_ab[(within_ab.genome == g) &
                        ((within_ab.subj1 == sj) | (within_ab.subj2 == sj))]
        if not row.empty:
            rr = row.iloc[0]; pc = rr["breadth_compared"]; pop = rr["popANI"]; verdict = rr["verdict"]
        else:
            pc = np.nan; pop = np.nan
            verdict = "NOT_EVALUABLE"   # co-detected but inStrain could not form a >=breadth comparison
        codet_rows.append(dict(subject=sj, genome=g,
                               covA=round(cA, 1), breadthA=round(bA, 2),
                               covB=round(cB, 1), breadthB=round(bB, 2),
                               compare_breadth=(round(pc, 3) if pc == pc else "-"),
                               popANI=(round(pop, 6) if pop == pop else "-"),
                               status=verdict))
    codet = pd.DataFrame(codet_rows)
    if not codet.empty:
        codet.to_csv(os.path.join(a.out, "co_detected_species_detail.tsv"), sep="\t", index=False)
        codet[codet.status == "NOT_EVALUABLE"].to_csv(
            os.path.join(a.out, "unresolved_candidates.tsv"), sep="\t", index=False)

    # individual-specific: species that are within-shared but NOT between-shared
    def species_within_shared(g): return not shared[shared.genome == g].empty
    def species_between_shared(g):
        b = between_ab[(between_ab.genome == g) & (between_ab.verdict == "SHARED_STRAIN")]
        return not b.empty
    indiv_specific = [g for g in shared.genome.unique() if not species_between_shared(g)]

    # longitudinal candidates: shared strains in a woman who has >1 timepoint at a site
    tp_counts = meta.groupby(["subject", "cls"]).size()
    def is_longitudinal(sj):
        try:  return (tp_counts.get((sj, "A"), 0) > 1) or (tp_counts.get((sj, "B"), 0) > 1)
        except Exception: return False
    longit = shared[shared.subj1.map(is_longitudinal) | shared.subj2.map(is_longitudinal)]

    # ---- write outputs --------------------------------------------------------------------
    within_ab.to_csv(os.path.join(a.out, "within_woman_AB.tsv"), sep="\t", index=False)
    not_eval.to_csv(os.path.join(a.out, "NOT_EVALUABLE_within_AB.tsv"), sep="\t", index=False)
    shared.to_csv(os.path.join(a.out, "shared_strain_candidates.tsv"), sep="\t", index=False)

    # within vs between popANI distribution per species (only evaluable)
    wb = []
    for g in sorted(ab.genome.unique()):
        w = eval_within[eval_within.genome == g]["popANI"]
        b = between_ab[(between_ab.genome == g) & (between_ab.verdict != "NOT_EVALUABLE")]["popANI"]
        wb.append(dict(genome=g, n_within_eval=len(w), within_max=round(w.max(), 6) if len(w) else np.nan,
                       n_between_eval=len(b), between_max=round(b.max(), 6) if len(b) else np.nan))
    pd.DataFrame(wb).to_csv(os.path.join(a.out, "within_vs_between_by_species.tsv"), sep="\t", index=False)

    # ---- funnel report --------------------------------------------------------------------
    L = []
    L.append("="*70)
    L.append("AIM-1 FUNNEL  —  stool/rectum <-> vagina strain sharing")
    L.append("="*70)
    L.append(f"{len(women):>5}  women")
    L.append(f"{n_samples:>5}  samples  (site A gut/rectum, site B vaginal)")
    L.append(f"{len(ab):>5}  cross-site A<->B comparisons inStrain could form")
    L.append(f"{len(within_ab):>5}     of which WITHIN-woman")
    n_codet_women = len(shared_species_women)
    n_unresolved = int((codet.status == "NOT_EVALUABLE").sum()) if not codet.empty else 0
    n_codet_eval = n_codet_women - n_unresolved
    L.append(f"{len(shared_species):>5}  SHARED SPECIES (same species >= {a.cov_floor}x at BOTH sites of a woman)")
    L.append(f"{n_codet_women:>5}     co-detected (woman x species) instances")
    L.append(f"{n_codet_eval:>5}        of which EVALUABLE for strain comparison (compare breadth >= {a.breadth_min})")
    L.append(f"{n_unresolved:>5}        of which NOT EVALUABLE (present both sites, too sparse to strain-type) <-- unresolved, NOT negative")
    L.append(f"{len(shared):>5}  SHARED-STRAIN calls (evaluable within-woman, popANI >= {a.popani_shared})")
    L.append(f"{len(indiv_specific):>5}  individual-specific species (within-shared, NOT between-shared)")
    L.append(f"{len(longit):>5}  longitudinal candidates (shared strain in a multi-timepoint woman -> Aim 2 only w/ real dates)")
    L.append("")
    if not codet.empty and n_unresolved:
        L.append("UNRESOLVED CO-DETECTIONS (present at both sites, depth-limited — top targets for deeper seq):")
        for _, r in codet[codet.status == "NOT_EVALUABLE"].iterrows():
            L.append(f"    woman {r['subject']}  {r['genome']:<26} "
                     f"A {r['covA']}x/br{r['breadthA']}  B {r['covB']}x/br{r['breadthB']}")
        L.append("")
    if len(shared):
        L.append("RESULT: shared-strain candidate(s) found — see shared_strain_candidates.tsv.")
        L.append("        Verify against between-woman null before any transmission claim.")
    elif n_codet_eval > 0:
        L.append(f"RESULT: {n_codet_eval} evaluable within-woman comparison(s), ZERO shared strains.")
        L.append(f"        Honest negative on the powered comparisons; {n_unresolved} co-detection(s) remain unresolved.")
    elif n_codet_women > 0:
        L.append(f"RESULT: {n_codet_women} species co-detected across sites within a woman, but NONE evaluable")
        L.append("        at these depths -> unresolved candidates, NOT evidence of no sharing.")
    else:
        L.append("RESULT: no species reached the coverage floor at both sites in any woman.")
        L.append("        -> 'no evidence of sharing (depth-limited)', NOT 'evidence of no sharing'.")
    report = "\n".join(L)
    print(report)
    open(os.path.join(a.out, "FUNNEL.txt"), "w").write(report + "\n")
    print(f"\n[out] {a.out}/  (FUNNEL.txt, within_woman_AB.tsv, NOT_EVALUABLE_within_AB.tsv, "
          f"shared_strain_candidates.tsv, within_vs_between_by_species.tsv, all_comparisons.tsv)")

if __name__ == "__main__":
    main()
