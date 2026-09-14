# Within-woman gut↔vaginal strain sharing in T18 — the first positive

*Goltsman/DiGiulio cohort (PRJNA288562), subject T18. Evidence in
[`../example/crosssite/t18_comparisons.tsv`](../example/crosssite/t18_comparisons.tsv);
reproduce with [`_t18_crosssite.py`](../scripts/dev/_t18_crosssite.py).*

**This overturns the standing conclusion of the pilot.** Every prior run reported no
gut↔vaginal strain sharing in this cohort. That negative was partly an artifact of *which
gut profile was compared* — selecting T18's deepest gut sample instead of an arbitrary one
turns ~974 bp of comparison into 307,794 bp, and the answer changes.

## The finding

T18 carries *L. iners* in her gut continuously across pregnancy, and it is the **same strain**
as the population dominating her vagina.

| comparison | role | popANI | bases compared | population SNPs |
|---|---|--:|--:|--:|
| gut t106 × vagina t191 | **cross-site (primary)** | **0.999935** | 307,794 | **20** |
| gut t254 × vagina t254 | cross-site (independent replicate) | 0.999843 | 89,359 | 14 |
| gut t106 × gut t254 | gut lineage persistence (148 days) | 0.999719 | 35,640 | 10 |
| vagina t106 × vagina t254 | vaginal positive control | 1.000000 | 976,132 | 0 |
| gut t106 × **T7** vagina | **matched-breadth negative control** | 0.992127 | 302,916 | **2,385** |

## Why the low breadth does not sink it

All cross-site rows fall below the standard's `percent_compared ≥ 0.5` floor — 0.23 for the
primary comparison — because T18's gut carriage is only ~3×. The obvious objection is that
0.23 breadth cannot be trusted. **The matched-breadth negative control answers it directly:**

> At **302,916** compared bases, T18's gut *L. iners* against an **unrelated** woman's vaginal
> *L. iners* gives popANI 0.992127 and **2,385** population SNPs.
> At **307,794** compared bases — essentially the same breadth — T18's gut against **her own**
> vagina gives popANI 0.999935 and **20** SNPs.

Same organism, same reference, same breadth, **119× fewer SNPs**. Breadth sufficient to
separate strains is breadth sufficient to join them. The floor exists to exclude calls made on
a few hundred bases (see [`between-person-null.md`](./between-person-null.md), where 27
artifacts reach popANI 1.0 on 0.016–4% of the genome); 300 kb with a matched negative control
is a categorically different situation.

## Why it is not contamination

*L. iners* appears in **all 10** of T18's gut samples, spanning t66 → t254 (~6 months):

| timepoint | t66 | t85 | t106 | t126 | t149 | t169 | t191 | t212 | t232 | t254 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| gut coverage | 0.10 | 0.40 | **3.18** | 0.95 | 0.39 | 0.42 | 0.16 | 0.75 | 0.05 | **2.07** |
| gut breadth | 0.05 | 0.29 | **0.89** | 0.58 | 0.28 | 0.32 | 0.08 | 0.50 | 0.02 | 0.82 |

Sporadic cross-contamination hits one or two samples. It does not hit ten consecutive
collections over six months. The gut lineage is also internally consistent (t106 × t254,
popANI 0.999719), which is what persistent carriage looks like and what independent
contamination events would not produce.

The community check points the same way: T18's gut carries *P. vulgatus* (6.6×) and *P. bivia*
(17.0×) that are absent or near-absent from her vagina, and *P. bivia* runs the **opposite**
direction across sites (gut 17.0× vs vagina 0.79×). The two sites are not copies of each other.

## How it was found

The funnel in [`_crosssite_funnel.py`](../scripts/dev/_crosssite_funnel.py) separates two
things the earlier analyses merged:

```
detected in gut  →  co-detected at BOTH sites  →  jointly deep enough to compare  →  shared
```

Across the 4 profiled Goltsman women, exactly **one** co-detection reaches the comparable
stage: T18's *L. iners*. The other three women have **no** cross-site co-detection at all —
their negatives are genuine absence, not depth. Reporting "0/4 shared" would hide that the
denominators are different in kind.

Sample selection is what surfaced it. Ranking T18's gut profiles by depth picks SRR6748155
(3.18×, breadth 0.89); an arbitrary pick lands on samples at 0.05–0.4× where *L. iners* is a
trace and the comparison is uninformative. **A cohort-level "no sharing" result is only as
good as the per-subject profile selection behind it.**

## What this changes

1. **"*Lactobacillus* is not a gut reservoir" is refuted as a universal claim.** It holds in
   3/3 Fijian women and 3/4 Goltsman women — but not in T18. The exclusion of *Lactobacillus*
   from the rectovaginal study's target list was justified on the Fijian result alone
   ([`fijian-pilot-findings.md`](./fijian-pilot-findings.md)); on this evidence the honest
   position is that gut *Lactobacillus* carriage is **uncommon but real**, and excluding it
   outright discards the only positive sharing signal found so far.
2. **Low-abundance carriage is the norm for the interesting case.** T18's gut *L. iners* sits
   at 0.05–3.18×. Any study powered only for dominant taxa will miss exactly this.
3. **The breadth floor needs a companion, not a relaxation.** A matched-breadth control turns
   a sub-floor comparison into an interpretable one. That belongs in the standard as a
   reporting requirement rather than as a lower threshold.

## Limitations

- **n = 1 woman**, 1 of 4 profiled. This is a case, not a rate.
- All cross-site rows are **below the pre-registered floor**; under the standard as written
  these are candidates, not confident calls. The claim rests on the matched control, which is
  an argument about the evidence, not a threshold pass.
- Goltsman "gut" is **stool**, not a rectal swab. Collection-route contamination is less likely
  than sporadic contamination but is not formally excluded.
- **Direction is unknown.** Gut and vaginal samples are same-day, so nothing here says whether
  the gut seeded the vagina or the reverse.
- The reference is the narrow 8-genome `vagref`; a broader catalogue could reveal co-detections
  this analysis cannot see.
