# New-grad SWE sponsor check — 2026-10-01

## Executive summary

This report checks 1 software job postings for a new graduate on OPT who will need visa sponsorship. It asks whether the company's top five recorded sponsored titles include a software title that the keyword rule classifies as non-senior, whether the posting is still open, and whether hiring can finish before the student runs out of OPT unemployment days (2027-04-15, from the student's own dates, assuming no work in between; any work moves this date later).

**Result:** Apply 0 · Consider 0 · Skip 0 · Held for a human 1. 1 of 1 were skipped or held.

Labels: **record** = read from a named repository data file or returned by a named live checker/API; **model-judgment** = inferred by a rule in this script; **your-input** = supplied by the student, unchecked.

## Decisions

| Role | Decision | Next action | Sponsorship evidence | Live? | Posting level | Timeline | Form D (sample only) | H-1B median salary vs BLS median |
|---|---|---|---|---|---|---|---|---|

## Held: a human must look these up

- **Pintrest Inc · Software Engineer**: G-sponsorship: no row in the sponsorship CSV after name normalisation; absence of a row is not evidence of non-sponsorship

## Try these instead

For each role that is not a clean Apply: other companies in the same city, not already in this run, whose sponsorship record shows a software title the keyword rule classifies as non-senior, ranked by approvals. Names and counts are records; the entry-level class is model-judgment; none of this says a role is open now.

None this run.

Network targets with a suggested first question: `network-targets.md` (0 this run).

## What this run did not verify

- Whether a company sponsors *new grads today*: the CSV gives the top five sponsored titles with no year and no count per title.
- Whether a title is entry-level: a keyword rule decides, and it is labeled model-judgment.
- Posting level: a phrase and years-of-experience rule over the posting text (Greenhouse postings only); it can miss phrasing it does not know and it does not change the score.
- E-Verify participation (needed for a STEM OPT extension): no data in the repo.
- Funding: only the shipped Form D samples were searched; "not in sample" says nothing about real funding.
- Salary: the BLS figure is a national median for the occupation, not an offer; role quality has weight 0 in the scorer, so it changed no decision.
- OPT dates and hiring lag are the student's own inputs.

## Run record

- Liveness: `fixture:course/2026fa/submissions/pavithra-prasad/worked-run/break-tests/liveness-typo.json`
- Data: `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv`, `data/sec/form-d/processed/sample/companies-sec-*.sample.json`, `data/bls/compact/soc_occupation_compact.csv`
- Scorer: `scripts/score/role-scorer.mjs` (called, not copied); its own audit is `role-scores.md` in this folder
- Agent log: `run-log.json` in this folder
