"""strainshare command-line interface.

    strainshare analyze     --compare --meta --metaphlan --outdir [--config]
    strainshare benchmark   [--mode model | --selftest | --from-reads F | --precision-edge F]
    strainshare diagnostic  --pairs --out [--title]
    strainshare version
"""
import argparse
import os
import sys

import pandas as pd

from . import __version__
from .config import SPEC_VERSION, load_config, site_classes
from . import analysis, generalist, direction, plots, benchmark


def _cmd_analyze(a):
    cfg = load_config(a.config)
    if a.site_pair:
        cfg = dict(cfg)
        cfg["site_pair"] = [s.strip() for s in a.site_pair.split(",")]
    _, _, within_cls, _ = site_classes(cfg)
    out = analysis.analyze_files(a.compare, a.meta, a.metaphlan, a.outdir, cfg)
    generalist.run_files(f"{a.outdir}/pairs_tagged.tsv", a.outdir, cfg,
                         candidates_path=f"{a.outdir}/translocation_candidates.tsv")
    direction.run_files(f"{a.outdir}/translocation_candidates.tsv",
                        f"{a.outdir}/pairs_tagged.tsv", a.meta, a.outdir, cfg)
    meta = pd.read_csv(a.meta, sep="\t")
    plots.all_figures(out["pairs_tagged"], out["translocation_candidates"], meta, f"{a.outdir}/figures", cfg=cfg)
    p = out["pairs_tagged"]
    cand = out["translocation_candidates"]
    n_shared = int(p[p.pair_class == within_cls].shared_strain.sum()) if len(p) else 0
    n_transloc = int((cand.verdict == "translocation_candidate").sum()) if "verdict" in cand.columns else 0
    n_contam = int((cand.verdict == "contamination_suspect").sum()) if "verdict" in cand.columns else 0
    print(f"[analyze] {len(p)} pairs | within-person cross-site shared: {n_shared} | "
          f"translocation candidates: {n_transloc} | contamination suspects: {n_contam}")
    print(f"[analyze] wrote tables + figures/ to {a.outdir}")


def _cmd_benchmark(a):
    cfg = load_config(a.config)
    if a.selftest:
        benchmark.selftest(cfg)
        print("[benchmark] selftest PASSED")
        return
    if a.from_reads:
        benchmark.summarize_reads(a.from_reads, cfg, a.outdir)
        print(f"[benchmark] reads validation -> {a.outdir}")
        return
    if a.precision_edge:
        benchmark.precision_edge(a.precision_edge, cfg, a.outdir)
        print(f"[benchmark] precision edge -> {a.outdir}")
        return
    coverages = [float(x) for x in a.coverages.split(",")] if a.coverages else None
    benchmark.run_model(a.outdir, cfg, coverages=coverages, n_pairs=a.n_pairs, seed=a.seed)
    print(f"[benchmark] model sweep -> {a.outdir}")


def _cmd_diagnostic(a):
    pairs = pd.read_csv(a.pairs, sep="\t")
    conf = plots.popani_breadth(pairs, a.out, title=a.title)
    print(f"[diagnostic] {len(conf)} comparison(s) in the confident-call box -> {a.out}")


def _cmd_fetch(a):
    from . import fetch
    site_map = fetch.parse_site_map(a.site_map)
    sheet, path = fetch.fetch_to_sheet(
        a.bioproject, a.outdir, site_map,
        paired_only=not a.all_samples, max_subjects=a.max_subjects, do_download=a.download)
    n_sub = sheet.subject.nunique() if len(sheet) else 0
    by_site = sheet.bodysite.value_counts().to_dict() if len(sheet) else {}
    print(f"[fetch] {a.bioproject}: {len(sheet)} samples, {n_sub} subjects, sites={by_site}")
    print(f"[fetch] wrote {path}" + ("" if a.download else "  (fq1/fq2 are ENA URLs; add --download to pull fastqs)"))


def _cmd_version(a):
    print(f"strainshare {__version__} (standard spec {SPEC_VERSION})")


def build_parser():
    p = argparse.ArgumentParser(prog="strainshare",
                                description="Standardized cross-body-site bacterial strain-sharing analysis.")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="shared-strain call + null + contamination + generalist + direction + figures")
    a.add_argument("--compare", required=True, help="inStrain genomeWide_compare.tsv")
    a.add_argument("--meta", required=True, help="metadata: sample subject timepoint bodysite")
    a.add_argument("--metaphlan", required=True, help="community table (rows=features, cols=samples)")
    a.add_argument("--outdir", default="results")
    a.add_argument("--config", default=None)
    a.add_argument("--site-pair", dest="site_pair", default=None,
                   help="override the two body sites, e.g. 'oral,gut' or 'donor,recipient'")
    a.set_defaults(func=_cmd_analyze)

    b = sub.add_parser("benchmark", help="coverage-sweep / precision-edge benchmarks")
    b.add_argument("--mode", choices=["model"], default="model")
    b.add_argument("--selftest", action="store_true")
    b.add_argument("--from-reads", dest="from_reads", default=None)
    b.add_argument("--precision-edge", dest="precision_edge", default=None)
    b.add_argument("--coverages", default=None)
    b.add_argument("--n-pairs", dest="n_pairs", type=int, default=4000)
    b.add_argument("--seed", type=int, default=0)
    b.add_argument("--outdir", default="results/benchmark")
    b.add_argument("--config", default=None)
    b.set_defaults(func=_cmd_benchmark)

    d = sub.add_parser("diagnostic", help="popANI x breadth confident-call-box plot")
    d.add_argument("--pairs", required=True)
    d.add_argument("--out", required=True)
    d.add_argument("--title", default="")
    d.set_defaults(func=_cmd_diagnostic)

    f = sub.add_parser("fetch", help="build a sample sheet from an ENA BioProject (public data)")
    f.add_argument("--bioproject", required=True, help="ENA/SRA BioProject, e.g. PRJNA982400")
    f.add_argument("--outdir", default="data")
    f.add_argument("--site-map", dest="site_map", default="V=vagina,C=cervix,R=rectum,G=gut,O=oral",
                   help="alias site-code -> bodysite, e.g. 'V=vagina,C=cervix,R=rectum'")
    f.add_argument("--max-subjects", dest="max_subjects", type=int, default=None,
                   help="cap to the first N subjects (for a quick test)")
    f.add_argument("--all", dest="all_samples", action="store_true",
                   help="keep all samples (default keeps only subjects with >=2 sites)")
    f.add_argument("--download", action="store_true", help="download fastqs (large!)")
    f.set_defaults(func=_cmd_fetch)

    v = sub.add_parser("version", help="print version")
    v.set_defaults(func=_cmd_version)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
