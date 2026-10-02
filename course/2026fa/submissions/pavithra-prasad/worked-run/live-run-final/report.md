# New-grad SWE sponsor check — 2026-10-01

## Executive summary

This report checks 4 software job postings for a new graduate on OPT who will need visa sponsorship. It asks whether each company has a record of sponsoring entry-level software engineers, whether the posting is still open, and whether hiring can finish before the OPT unemployment deadline (2027-04-15, from the student's own dates).

**Result:** Apply 3 · Consider 0 · Skip 1 · Held for a human 0. 1 of 4 were skipped or held.

Labels: **record** = read from a repo data file; **model-judgment** = inferred by a rule in this script; **your-input** = supplied by the student, unchecked.

## Decisions

| Role | Decision | Next action | Sponsorship evidence | Live? | Posting level | Timeline | Form D (sample only) | H-1B median salary vs BLS median |
|---|---|---|---|---|---|---|---|---|
| Pinterest, Inc. · University Grad Software Engineer 2027 (USA) | **Apply** (0.555) | tailor application | entry-level-swe: 1364 approvals; entry-level titles ['Software Engineer', 'Software Engineer II', 'Software Engineer I'] [record + model-judgment] | active [record] | entry: posting says 'university grad' [model-judgment] | 1.0 [your-input] | not in sample | $156,853 vs $133,080 [record] |
| Databricks, Inc. · Software Engineer, Web Products (Mountain View) | **Apply** (0.525) | check first: the posting asks for more experience than a new grad has; tailor only if you meet it | entry-level-swe: 1640 approvals; entry-level titles ['Software Engineer'] [record + model-judgment] | active [record] | mid: posting asks 4+ years of experience [model-judgment] | 1.0 [your-input] | filed 31-DEC-2025, sold $4,082,050,250; filed 31-DEC-2025, sold $23,017,200 [record] | $149,422 vs $90,930 [record] |
| Pinterest, Inc. · Software Engineer II, Big Data, tvScientific | **Apply** (0.495) | tailor application, after reading the posting's experience requirement (the rule could not find one) | entry-level-swe: 1364 approvals; entry-level titles ['Software Engineer', 'Software Engineer II', 'Software Engineer I'] [record + model-judgment] | active [record] | unclear: no new-grad phrase and no 'N years experience' found [model-judgment] | 1.0 [your-input] | not in sample | $156,853 vs $133,080 [record] |
| Chime Financial Inc · Deliberately dead URL (the repo's own example 404) | **Skip** (0.000) | skip | senior-only-swe: 580 approvals; entry-level titles none [record + model-judgment] | expired [record] | not checked (no posting text) | 1.0 [your-input] | not in sample | $240,108 vs $133,080 [record] |

## Held: a human must look these up

None.

## What this run did not verify

- Whether a company sponsors *new grads today*: the CSV gives the top five sponsored titles with no year and no count per title.
- Whether a title is entry-level: a keyword rule decides, and it is labeled model-judgment.
- Posting level: a phrase and years-of-experience rule over the posting text (Greenhouse postings only); it can miss phrasing it does not know and it does not change the score.
- E-Verify participation (needed for a STEM OPT extension): no data in the repo.
- Funding: only the shipped Form D samples were searched; "not in sample" says nothing about real funding.
- Salary: the BLS figure is a national median for the occupation, not an offer; role quality has weight 0 in the scorer, so it changed no decision.
- OPT dates and hiring lag are the student's own inputs.

## Run record

- Liveness: `live:scripts/ats/check-liveness.mjs`
- Data: `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv`, `data/sec/form-d/processed/sample/companies-sec-*.sample.json`, `data/bls/compact/soc_occupation_compact.csv`
- Scorer: `scripts/score/role-scorer.mjs` (called, not copied); its own audit is `role-scores.md` in this folder
- Agent log: `run-log.json` in this folder
