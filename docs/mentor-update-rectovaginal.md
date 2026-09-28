# Rectovaginal-transmission investigation — summary & questions for discussion

*A short, honest update on the strain-level rectal/gut↔vaginal work, and the specific points where I'd
value your advice. Tool: [strainshare](../README.md) (validated on 26 women of public data — see
[example/cervix_vagina_n26](../example/cervix_vagina_n26)). Full proposal:
[study-rectovaginal-pregnancy.md](study-rectovaginal-pregnancy.md).*

## TL;DR
The tool works (validated). On the small **public** cohorts I could access, I found **no within-woman
gut↔vaginal shared strain** — but this is an *underpowered / not-evaluable* result, **not** evidence
against transmission: the vaginal commensals simply aren't gut-resident, and the pathogens weren't
vaginally colonized in those particular women. The literature strongly supports transmission for the
*pathogens*. The natural next step is to run the tool on a **colonized, deep, ideally longitudinal**
cohort — which points at the lab's 382-set. My questions below are mostly about how best to do that.

## What I tested
Within-woman rectal/gut ↔ vaginal **strain-level** sharing (inStrain popANI ≥ 0.999, breadth ≥ 0.5),
contamination-controlled (within- vs between-person null + a translocation-vs-contamination discriminator).

## What I did (data + method)
| Cohort | Sites, n | Reference | Result |
|---|---|---|---|
| Fijian (PRJNA826539) | rectal+vaginal, 3 deep | broad 33-genome | No within-woman cross-site shared strain |
| HMP (phs000228) | stool+vaginal, ~7 of 34 complete | broad 33-genome | Clean baseline null, 0 co-detections |
| Goltsman (PRJNA288562) | gut+vaginal, longitudinal | per-sample | **T18: gut *L. iners* = same strain as vagina across 10 timepoints** |

## Findings (honest)
- **Commensals are not a gut reservoir.** In all 3 Fijian women the dominant vaginal *Lactobacillus* /
  *Gardnerella* were deeply covered vaginally (up to 185×) but **0× in the rectum**. Clean, and
  reference-controlled (the reference *contains* these species).
- **Pathogens weren't testable in these women.** *E. coli* was rectum-only where present; **GBS undetected**;
  BV-*Prevotella* were co-detected at both sites in one woman but at breadth too low to strain-type
  (**not-evaluable**, logged as such — never counted as "not shared").
- **One genuine positive (a commensal):** Goltsman **T18** carries gut *L. iners* as the *same strain* as
  her vagina across 10 timepoints — a real within-woman cross-site signal.
- **HMP** (healthy, non-pregnant US women): *Lactobacillus*-dominant vaginas, gut pathogens absent from the
  vagina → the expected healthy baseline.

## Interpretation
These are **honest negatives on underpowered/uncolonized data**, consistent with (not contradicting) the
literature: rectovaginal same-strain transfer is documented for the pathogens (identical GBS genotype in
18/19 colonized women; ~85% *E. coli* concordance; rectal carriage predicts vaginal; the gut re-seeds after
antibiotics). The commensals shown here are simply the *wrong target*. To observe transmission we need a
cohort where the pathogens are actually present at both sites — i.e. **colonized women, deep sequencing,
a broad reference, and (for direction) longitudinal sampling.**

## Open questions / items to explore — where I'd value your advice

**Data**
1. **The 382 paired vaginal–rectal set** — could I run strainshare on it, targeting the pathogens
   (GBS / *E. coli* / BV-*Prevotella*) and their clones (CC17, ST131)? It's the one in-hand dataset that
   could actually test *pathogen* transmission in colonized women. This is my main ask.
2. Is the 382-set **longitudinal** (≥2 timepoints/woman)? If cross-sectional, direction is unresolvable and
   I'd frame Aim 2 accordingly.
3. Are there **negative/plate controls** for it, so the contamination discriminator (and CroCoDeEL) can run?

**Method / reference**
4. **Reference strategy:** build GTDB + a vaginal collection (VMGC) + per-sample MAGs? Should I fold in
   Scarlet's assemblies? Reference breadth has been the dominant sensitivity limit in my pilots.
5. **Depth / the ~10× floor:** is the 382-set (~38M reads/sample) deep enough to strain-type *low-abundance*
   pathogens at both sites, or should we plan **culture/target enrichment** for GBS/*E. coli*?
6. **strainshare vs the lab pipeline:** does the standardized interpretation layer (within/between null +
   contamination discriminator + direction) complement inStrain + CroCoDeEL + StrainFacts, or overlap? Where
   is it most useful?

**Direction & scope**
7. Is the **Goltsman T18** commensal signal worth following up, or a distraction from the pathogen focus?
8. For the pregnancy / low-resource arm: which path do you favor — **MOMS-PI dbGaP**, an **author request**
   for the Fijian rectal set (paired data exists but is unreleased), or a **prospective cohort**?

**Publishing**
9. Is the **strain-sharing methods/tool paper** (backed by the n=26 validation) worth pursuing on its own,
   and if so, what venue/scope — and how would you like authorship handled?

---
*Everything is committed at github.com/jyu9675/bioai-strainshare (tool, validation, full proposal package).
Happy to walk through any piece.*
