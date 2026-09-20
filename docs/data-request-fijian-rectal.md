# Data request — Fijian paired rectal shotgun (PRJNA1153641)

*A concrete, near-term path to real paired rectal + vaginal shotgun metagenomes. Companion to the
[proposal](study-rectovaginal-pregnancy.md) and the [MOMS-PI scoping](momspi-dbgap-scoping.md).*

## The opportunity

The study **"Azithromycin alters the microbiome composition, function and resistome in women with
*Chlamydia trachomatis* infections"** (*npj Biofilms and Microbiomes*, 2025;
[s41522-025-00858-9](https://www.nature.com/articles/s41522-025-00858-9)) generated **paired vaginal,
cervical, and rectal shotgun metagenomes** from the same women (a Fiji-based, high-STI-risk cohort).

- **Vaginal + cervical (PRJNA982400): public** — verified **350 WGS runs** on ENA (258 vaginal, 92
  cervical), subject-numbered aliases (e.g., `95V`, `86C`).
- **Rectal (PRJNA1153641): not released** — verified **0 runs** on ENA/SRA. The rectal half exists (the
  paper analyzed it) but is held by the authors.

If the rectal set can be obtained and it pairs by subject number with the vaginal set, this is a **ready
open-ish paired rectal↔vaginal shotgun cohort** — directly runnable through strainshare, targeting the
pathogens (GBS, *E. coli*, BV taxa).

**Honest caveats:** this is a *Chlamydia*-treatment cohort, **not confirmed pregnant** — so it tests the
baseline rectum↔vagina mechanism in a high-risk Pacific population, not the pregnancy/WASH arm. It is a
strong *mechanism/validation* cohort, complementary to (not a substitute for) the prospective study.

## Ask, precisely
Access to the **rectal shotgun reads (PRJNA1153641)**, with the **subject-level linkage** to the public
vaginal/cervical samples (so pairs can be formed), plus any body-site and clinical metadata the authors
can share under their terms.

## Draft email

> **Subject:** Request: paired rectal shotgun metagenomes (PRJNA1153641) for a rectovaginal
> strain-transmission analysis
>
> Dear Dr. [corresponding author — from the paper],
>
> I greatly enjoyed your 2025 *npj Biofilms and Microbiomes* paper on azithromycin and the microbiome in
> women with *C. trachomatis* infection. I am conducting a strain-resolved study of rectum→vagina
> bacterial transfer (GBS, *E. coli*, BV-associated taxa) using an open, contamination-aware pipeline
> (inStrain + our published tool, **strainshare**), and your cohort is uniquely suited to it because it
> has **paired rectal and vaginal shotgun metagenomes from the same women**.
>
> The **vaginal/cervical** data (PRJNA982400) are available on SRA, but the **rectal** metagenomes
> (PRJNA1153641) do not yet have released runs. Would you be willing to share the rectal shotgun reads —
> together with the subject-level identifiers needed to pair them with the vaginal samples, and any
> body-site/clinical metadata you can provide — for a within-woman cross-site strain-sharing analysis? I
> would of course follow your data-use terms, acknowledge or co-author per your preference, and share
> results back.
>
> Thank you for considering this, and for making the vaginal data public.
>
> Sincerely,
> [Name, degrees] · [institution] · [email] · (with [PI], [lab])

## If they agree
Run identically to the prospective cohort: broad reference + MAGs → `inStrain profile` →
`strainshare analyze --site-pair rectum,vagina`, focused on the pathogens/clones (CC17, ST131). If they
decline, the [MOMS-PI dbGaP route](momspi-dbgap-scoping.md) and the prospective cohort remain.
