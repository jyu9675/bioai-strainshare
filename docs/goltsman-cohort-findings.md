# Goltsman/DiGiulio pilot — real-cohort run through the strainshare stack

*Study D's real-data figures (F1/F2/F4/F5). Public cohort PRJNA288562, 4 subjects (M4, T7, T18, P2),
88 inStrain profiles, run through 05 → 09 → 08 → 06 plus the between-person null (04b). Artifacts in
[`../example/goltsman/`](../example/goltsman).*

## What was run

- **Within-person** comparisons (108 same-site + 66 gut↔vagina) from the pairwise workaround
  (`inStrain compare` all-N OOMs on this cohort; pairwise does not).
- **Between-person null** — 40 representative unrelated-subject gut↔vagina pairs via
  [`04b_between_person_compare.sh`](../scripts/04b_between_person_compare.sh).
- Thresholds from the versioned standard; F2 contamination axis used an 8-genome coverage proxy
  (full MetaPhlAn merge still pending).

## Result

| Figure | Outcome |
|---|---|
| **Positive controls** | **11 confident within-same-site persistence calls** (popANI ≥ 0.999 **and** breadth 0.8–0.94): *L. iners* in vagina over time (T7, T18), *P. vulgatus* in gut (P2, M4), *P. bivia* (T7). **The pipeline correctly detects true persistence on real data.** |
| **F1 — within vs between (gut↔vagina)** | within_shared_rate = **0** and between_shared_rate = **0** for every genome. No sharing either way. |
| **F2 — translocation vs contamination** | **0 translocation candidates** (nothing clears the breadth filter to enter the plane). |
| **F4 — direction** | **0 events** (no shared strains → nothing to orient). |
| **F5 — generalist filter** | **0 genomes flagged** (the one comparable between-person pair, *P. bivia*, popANI 0.9946 = different strain). |

The headline figure is [`fig_cohort_popani_breadth.png`](../example/goltsman/fig_cohort_popani_breadth.png):
positive controls land in the confident-call box (top-right); **no gut↔vagina pair, within or between,
comes close**.

## Why the negative is *driven by breadth*, not by "different strains"

The important nuance: within-person gut↔vagina comparisons that show popANI ≈ 1.0 do so on **tens to a
few hundred bases** (breadth 10⁻⁵–10⁻⁴) — the "popANI = 1.0 on a handful of positions = artifact" failure
the coverage benchmark predicted. Where breadth is even modestly higher, popANI falls to ~0.98–0.996
(different strains). And between unrelated people, **39 of 40 cross-site pairs share no genome at
comparable coverage at all** — an unrelated vagina (*Lactobacillus*-dominated) and gut
(*Bacteroides*-dominated) simply have nothing to compare.

So this is a **rigorous negative caused by cross-site coverage starvation**: the shared taxa across sites
sit *below the ~10× confidence floor* established in the reads benchmark ([`fig3_reads_validation`](../example/benchmark)).
It is "no evidence of sharing," and specifically **not** "evidence of distinct strains" — the data cannot
confidently call either way at this depth.

## Implications

1. **For the 191-sample cohort:** to detect gut↔FGT strain sharing you must get the *cross-site shared taxa*
   above ~10× breadth — i.e., much deeper sequencing on those samples, or targeted enrichment. Power the
   study for the cross-site taxon depth, not just total depth.
2. **For Study D:** the pilot is a clean **method-validation + rigorous-negative** result (positive controls
   fire; the breadth filter correctly rejects low-coverage artifacts). It is honest to report the negative
   as depth-limited rather than biological.

## Caveats

- 4 subjects — validates the *method*, not a population estimate.
- F2 used an 8-genome coverage proxy for community similarity; the full MetaPhlAn merge would sharpen it.
- The between-person null is capped at 40 representative pairs; near-empty by biology (cross-site cross-person
  overlap is essentially nil), so more pairs would not change the conclusion.
