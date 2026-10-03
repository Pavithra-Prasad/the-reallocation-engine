---
owner: Pavithra-Prasad
term: 2026fa
component: newgrad-swe-sponsor-check
status: DRAFT
promoted_to: null
---

# New-grad SWE sponsor check

## Executive summary

**What this is.** A small program for an international student finishing a master's degree, about to start OPT, and applying for entry-level software engineering jobs. For each job it checks, from the repository's own data, whether the company's top five recorded sponsored titles include a software title that a keyword rule classifies as non-senior (evidence about new-grad sponsorship, not proof of it), whether the posting is still open (cross-checked with the job board's own API where possible), whether the posting itself asks for more experience than a new grad has, and whether hiring can finish before the student would use up their OPT unemployment days (assuming no work in between). It then asks the repository's existing scorer for Apply / Consider / Skip and suggests a next step. For jobs that aren't a clean Apply it suggests up to three same-city companies with entry-level sponsorship records ("try these instead"), and it writes a list of companies to network into, with a suggested first question.

**Why read it.** It tells you the one command to run, what the output means, and what the program cannot check.

**What it found.** On the ten-role sample: three Apply, one Consider, two Skip, and four held for a person, because the sponsorship record was missing, blank, or matched two companies, or because the page check and the job-board API disagreed. On live postings it caught the repo's page checker calling an open new-grad posting "expired." Across the whole sponsorship dataset, 214 of 573 rows with software-type sponsored titles (37%) list only senior titles.

---

## Run it

From the **repo root** (running from a subfolder fails with "No such file"):

```bash
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --sample
```

Writes to `out/sample/` in this folder (gitignored, because the scorer stamps today's date and every run would otherwise change a tracked file). The committed record of the sample run is `course/2026fa/submissions/pavithra-prasad/runs/sample/`, made with `--sample --out-dir course/2026fa/submissions/pavithra-prasad/runs/sample`. Files:

| File | Reader | What |
|---|---|---|
| `report.md` | the person | decisions, next actions, held roles, what was not verified |
| `run-log.json` | the agent | every input and value with its label, gate results, held roles |
| `network-targets.md` | the person | companies to network into instead of applying, each with a suggested first question |
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

32 tests. No network: liveness is read from `fixtures/liveness.json` and Greenhouse answers from `fixtures/greenhouse/` (both invented, so both are labeled your-input in the output, never record). The scorer is the repo's own `role-scorer.mjs`, run locally with `node`. Python versions tested: see `course/2026fa/submissions/pavithra-prasad/TEST-REPORT.md`.

## How it decides

| Step | Source | Label |
|---|---|---|
| Find the company in `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` (exact match after dropping punctuation and trailing Inc/LLC/Corp…; no fuzzy matching) | CSV | record |
| No row, blank approvals, or more than one matching row → **held**, not scored | rule | — |
| Split the top sponsored titles into SWE / senior (`SWE_RE`, `SENIOR_RE` v1; v0 kept for comparison) | keyword rule | model-judgment |
| Evidence class → sponsorship term (`SPONSOR_MAP`): entry-level 0.9 Proven; entry-level with < 10 approvals 0.6 Likely; senior-only 0.5 Possible; no SWE title 0.3 Possible | design choice | model-judgment |
| Posting liveness: `scripts/ats/check-liveness.mjs`, or a saved fixture. Only HTTP 404/410 counts as expired; "expired" from a content heuristic → uncertain | ATS check | record live; model-judgment when this script reclassifies; your-input from a fixture |
| Greenhouse API (`boards-api.greenhouse.io`) when the role has `greenhouse: {board, job_id}`: 200/404 resolves an uncertain page check; a conflict → held | job-board API | record live; your-input from a fixture |
| Posting level from the posting text: new-grad phrases, "N+ years experience" → entry / mid / senior / unclear. Changes the next action, not the score | phrase rule | model-judgment |
| Timeline: start ≈ max(run date + hiring lag, OPT EAD start); deadline = max(EAD start, run date) + (90 − days already used), **assuming continuous unemployment** from then (the 90 days are accumulated, not a calendar date); 0 if start is after the deadline, 0.5 inside the buffer, else 1 | persona file | your-input |
| Fit | self-rated in the roles file; no model is called | your-input |
| "Try these instead": same-city (CSV `city`/`state`) companies, not already in the run, in the `entry-level-swe` class, ranked by approvals, up to 3, for every non-Apply role with a matched row | CSV + keyword rule | model-judgment (names and counts are records) |
| Network targets: scored roles whose next action starts with "network", with a fixed template question | rule | not evidence; `network-targets.md` |
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
