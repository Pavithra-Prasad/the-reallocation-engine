---
owner: Pavithra-Prasad
term: 2026fa
component: newgrad-swe-sponsor-check
status: DRAFT
promoted_to: null
---

# New-grad SWE sponsor check

## Executive summary

**What this is.** A small program for an international student finishing a master's degree, about to start OPT, and applying for entry-level software engineering jobs. For each job it checks, from the repository's own data, whether the company has a record of sponsoring *entry-level* software engineers (not only senior ones), whether the posting is still open (cross-checked with the job board's own API where possible), whether the posting itself asks for more experience than a new grad has, and whether hiring can finish before the student's OPT unemployment deadline. It then asks the repository's existing scorer for Apply / Consider / Skip and suggests a next step.

**Why read it.** It tells you the one command to run, what the output means, and what the program cannot check.

**What it found.** On the ten-role sample: three Apply, one Consider, two Skip, and four held for a person, because the sponsorship record was missing, blank, or matched two companies, or because the page check and the job-board API disagreed. On live postings it caught the repo's page checker calling an open new-grad posting "expired." Across the whole sponsorship dataset, 214 of 573 rows with software-type sponsored titles (37%) list only senior titles.

---

## Run it

From the **repo root** (running from a subfolder fails with "No such file"):

```bash
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --sample
```

Writes to `course/2026fa/submissions/pavithra-prasad/runs/sample/`:

| File | Reader | What |
|---|---|---|
| `report.md` | the person | decisions, next actions, held roles, what was not verified |
| `run-log.json` | the agent | every input and value with its label, gate results, held roles |
| `roles.json` | the scorer | the input this program built for `scripts/score/role-scorer.mjs` |
| `role-scores.json`, `role-scores.md` | both | the scorer's own output and per-term audit trace |

Other modes:

```bash
# reproduce the senior-only share across the whole CSV (old and new title rule)
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --census

# score both title rules against the hand-labeled titles in fixtures/
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --title-eval

# your own inputs, live: contacts the posting URLs in the roles file and boards-api.greenhouse.io
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py \
  --persona <persona.json> --roles <roles.json> \
  --out-dir course/2026fa/submissions/pavithra-prasad/runs/<name>
```

`--out-dir` must be inside `scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/` or `course/2026fa/submissions/pavithra-prasad/`; anything else stops the run.

## Test (offline)

```bash
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/test_sponsor_check.py
```

25 tests. No network: liveness is read from `fixtures/liveness.json` and Greenhouse answers from `fixtures/greenhouse/` (both invented). The scorer is the repo's own `role-scorer.mjs`, run locally with `node`. Tested on Python 3.9.6 and 3.13.

## How it decides

| Step | Source | Label |
|---|---|---|
| Find the company in `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` (exact match after dropping punctuation and trailing Inc/LLC/Corp…; no fuzzy matching) | CSV | record |
| No row, blank approvals, or more than one matching row → **held**, not scored | rule | — |
| Split the top sponsored titles into SWE / senior (`SWE_RE`, `SENIOR_RE` v1; v0 kept for comparison) | keyword rule | model-judgment |
| Evidence class → sponsorship term (`SPONSOR_MAP`): entry-level 0.9 Proven; entry-level with < 10 approvals 0.6 Likely; senior-only 0.5 Possible; no SWE title 0.3 Possible | design choice | model-judgment |
| Posting liveness: `scripts/ats/check-liveness.mjs`, or a saved fixture. Only HTTP 404/410 counts as expired; "expired" from a content heuristic → uncertain | ATS check | record |
| Greenhouse API (`boards-api.greenhouse.io`) when the role has `greenhouse: {board, job_id}`: 200/404 resolves an uncertain page check; a conflict → held | job-board API | record |
| Posting level from the posting text: new-grad phrases, "N+ years experience" → entry / mid / senior / unclear. Changes the next action, not the score | phrase rule | model-judgment |
| Timeline: start ≈ max(run date + hiring lag, OPT EAD start); 0 if after EAD start + 90 days, 0.5 inside the buffer, else 1 | persona file | your-input |
| Fit | self-rated in the roles file; no model is called | your-input |
| Form D funding: `data/sec/form-d/processed/sample/*.sample.json` | sample files | record (report only) |
| National wage, `data/bls/compact/soc_occupation_compact.csv`, vs the CSV's H-1B median salary | BLS / CSV | record (report only; role quality has weight 0 in the scorer) |

The composite score and the Apply / Consider / Skip decision come from `scripts/score/role-scorer.mjs`. This program does not re-implement them.

## Known limits

- The CSV lists the top five sponsored titles per company, with no year and no per-title count.
- The title rule is a keyword match. It was revised after seeing labeled titles; on 28 held-out titles labeled by a person it agreed on 26 before that person corrected two misreads. It does not know abbreviations like "Prin".
- The Greenhouse cross-check covers Greenhouse boards only; Lever and Ashby are not cross-checked.
- No E-Verify data, so the STEM OPT extension requirement is not checked.
- Form D data is the shipped 50-company-per-quarter sample only.
- The fixture persona is fictional; its dates are invented.
