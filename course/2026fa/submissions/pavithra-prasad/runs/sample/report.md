# New-grad SWE sponsor check — 2026-10-01

## Executive summary

This report checks 10 software job postings for a new graduate on OPT who will need visa sponsorship. It asks whether the company's top five recorded sponsored titles include a software title that the keyword rule classifies as non-senior, whether the posting is still open, and whether hiring can finish before the student runs out of OPT unemployment days (2027-04-15, from the student's own dates, assuming no work in between; any work moves this date later).

**Result:** Apply 3 · Consider 1 · Skip 2 · Held for a human 4. 6 of 10 were skipped or held.

Labels: **record** = read from a named repository data file or returned by a named live checker/API; **model-judgment** = inferred by a rule in this script; **your-input** = supplied by the student, unchecked.

## Decisions

| Role | Decision | Next action | Sponsorship evidence | Live? | Posting level | Timeline | Form D (sample only) | H-1B median salary vs BLS median |
|---|---|---|---|---|---|---|---|---|
| Pinterest, Inc. · Software Engineer I, Backend | **Apply** (0.540) | tailor application | entry-level-swe: 1364 approvals; entry-level titles ['Software Engineer', 'Software Engineer II', 'Software Engineer I'] [record + model-judgment] | active [your-input] | entry: posting says 'new grad' [model-judgment] | 1.0 [your-input] | not in sample | $156,853 vs $133,080 [record] |
| Uber Technologies Inc · Backend Engineer, New Grad | **Apply** (0.525) | tailor application | entry-level-swe: 3984 approvals; entry-level titles ['Software Engineer II', 'Software Engineer', 'SOFTWARE ENGINEER'] [record + model-judgment] | active [your-input] | entry: posting says 'new grad' [model-judgment] | 1.0 [your-input] | not in sample | $165,000 vs $133,080 [record] |
| Airbnb, Inc. · Full-Stack Software Engineer | **Apply** (0.495) | check first: the posting asks for more experience than a new grad has; tailor only if you meet it | entry-level-swe: 1000 approvals; entry-level titles ['Software Engineer'] [record + model-judgment] | active [your-input] | senior: posting asks 5+ years of experience [model-judgment] | 1.0 [your-input] | not in sample | $158,080 vs missing (no BLS row) [record] |
| Chime Financial Inc · Software Engineer, Backend (New Grad) | **Consider** (0.415) | network first: ask whether they sponsor new grads before tailoring | senior-only-swe: 580 approvals; entry-level titles none [record + model-judgment] | active [your-input] | entry: posting says 'recent grad' [model-judgment] | 1.0 [your-input] | not in sample | $240,108 vs $133,080 [record] |
| Databricks, Inc. · Software Engineer, New Grad | **Skip** (0.000) | network, don't apply: strong new-grad sponsor but posting closed | entry-level-swe: 1640 approvals; entry-level titles ['Software Engineer'] [record + model-judgment] | expired [your-input] | not checked (no posting text) | 1.0 [your-input] | filed 31-DEC-2025, sold $4,082,050,250; filed 31-DEC-2025, sold $23,017,200 [record] | $149,422 vs $133,080 [record] |
| Smartsheet Inc · Software Engineer (starts after a long process) | **Skip** (0.000) | skip | entry-level-swe: 240 approvals; entry-level titles ['SOFTWARE ENGINEER II'] [record + model-judgment] | active [your-input] | entry: posting asks 2+ years of experience [model-judgment] | 0.0 [your-input] | not in sample | $145,000 vs $133,080 [record] |

## Held: a human must look these up

- **Alphabet Inc · Software Engineer, Early Career**: G-sponsorship: row exists but Total Approvals is blank or 0; this can mean the sponsoring entity has a different legal name
- **Google LLC · Software Engineer, University Grad**: G-sponsorship: no row in the sponsorship CSV after name normalisation; absence of a row is not evidence of non-sponsorship
- **Peloton Interactive · Full-Stack Engineer**: G-sponsorship: 2 rows match: PELOTON INTERACTIVE INC, PELOTON INTERACTIVE LLC; the script will not pick one
- **Twilio Inc · Software Engineer (L2)**: G1 liveness: uncertain (page checker said active but Greenhouse API HTTP 404); a human must open the posting

## Try these instead

For each role that is not a clean Apply: other companies in the same city, not already in this run, whose sponsorship record shows a software title the keyword rule classifies as non-senior, ranked by approvals. Names and counts are records; the entry-level class is model-judgment; none of this says a role is open now.

- **Chime Financial Inc** (Consider): DOCUSIGN INC (1082 approvals); MAPLEBEAR INC (498 approvals); DROPBOX INC (430 approvals)
- **Databricks, Inc.** (Skip): DOCUSIGN INC (1082 approvals); MAPLEBEAR INC (498 approvals); DROPBOX INC (430 approvals)
- **Smartsheet Inc** (Skip): ZIPSTORM INC (18 approvals); PETABYTE TECHNOLOGY INC (12 approvals)
- **Twilio Inc** (Held): DOCUSIGN INC (1082 approvals); MAPLEBEAR INC (498 approvals); DROPBOX INC (430 approvals)

Network targets with a suggested first question: `network-targets.md` (2 this run).

## What this run did not verify

- Whether a company sponsors *new grads today*: the CSV gives the top five sponsored titles with no year and no count per title.
- Whether a title is entry-level: a keyword rule decides, and it is labeled model-judgment.
- Posting level: a phrase and years-of-experience rule over the posting text (Greenhouse postings only); it can miss phrasing it does not know and it does not change the score.
- E-Verify participation (needed for a STEM OPT extension): no data in the repo.
- Funding: only the shipped Form D samples were searched; "not in sample" says nothing about real funding.
- Salary: the BLS figure is a national median for the occupation, not an offer; role quality has weight 0 in the scorer, so it changed no decision.
- OPT dates and hiring lag are the student's own inputs.

## Run record

- Liveness: `fixture:scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/fixtures/liveness.json`
- Data: `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv`, `data/sec/form-d/processed/sample/companies-sec-*.sample.json`, `data/bls/compact/soc_occupation_compact.csv`
- Scorer: `scripts/score/role-scorer.mjs` (called, not copied); its own audit is `role-scores.md` in this folder
- Agent log: `run-log.json` in this folder
