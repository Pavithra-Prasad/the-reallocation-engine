## 2026-10-01 — newgrad-swe-sponsor-check sample and live runs

### Executive summary

On 1 October 2026 the new-grad software-engineer sponsor check was run once on its ten-role sample and four times on real job postings. The sample run gave three Apply, one Consider, two Skip, and held four roles for a person because a record was missing, duplicated, or contradicted. The live runs found that the repository's job-page checker called an open new-grad posting "expired." The program was changed to hold such results and confirm them with the job board's own data, and the last live run scored that posting correctly. A named person reviewed the sample decisions, accepted six, overrode one, and accepted the four held roles as needing manual lookup.

### Run record

- **Date:** 2026-10-01
- **Recipe:** newgrad-swe-sponsor-check v0.1.0 (`recipes/cases/2026fa/pavithra-prasad-newgrad-swe-sponsor-check.md`)
- **Persona:** `scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/fixtures/persona.json` (fictional)
- **Data:** `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv`, `data/sec/form-d/processed/sample/*.sample.json`, `data/bls/compact/soc_occupation_compact.csv`
- **Scorer:** `scripts/score/role-scorer.mjs`, called with `--profile` and `--out-dir`

#### Sample run (offline)

- **Command:** `python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --sample`
- **Inputs:** `fixtures/roles.json` (10 roles), liveness `fixtures/liveness.json`, Greenhouse `fixtures/greenhouse/` (all invented)
- **Outputs:** (committed copy, written with `--out-dir course/2026fa/submissions/pavithra-prasad/runs/sample`) `course/2026fa/submissions/pavithra-prasad/runs/sample/{run-log.json, report.md, network-targets.md, roles.json, role-scores.json, role-scores.md}`
- **Result:** Apply 3 · Consider 1 · Skip 2 · Held 4
- **Gates:** G0 pass · G-sponsor held 3 (Alphabet blank, Google LLC no row, Peloton two rows) · G1 held 1 (Twilio: page active, API 404) · G2 zeroed 1 (Smartsheet) · G3 cleared by Pavithra-Prasad, 2026-10-01 (below)

#### Live runs (real postings, `course/2026fa/submissions/pavithra-prasad/worked-run/roles-live.json`)

| Run | Code state | Result | What it showed |
|---|---|---|---|
| live-run-1-before-fix | page checker trusted | Apply 1 · Skip 3 | both Pinterest postings Skipped as "expired"; the Greenhouse API listed them open |
| live-run-2 | content-heuristic "expired" → held | Apply 1 · Skip 1 · Held 2 | safe, unresolved |
| live-run-3 | + Greenhouse API cross-check, posting level | Apply 3 · Skip 1 | Pinterest resolved; Databricks flagged "asks 4+ years" |
| live-run-final | frozen code | Apply 3 · Skip 1 | same decisions as run 3; pasted in the worked run |

Skip rate on the live set is 25%, below the ~50% a healthy run skips. The four live postings were hand-picked (three chosen because they looked promising, one deliberately dead), so the low skip rate reflects the selection, not the recipe.

#### G3 decision gate

Reviewer: **Pavithra-Prasad**, 2026-10-01, on `runs/sample/report.md`.

| Role | Program | Reviewer decision | Reason |
|---|---|---|---|
| Pinterest · Software Engineer I, Backend | Apply | accept | |
| Uber · Backend Engineer, New Grad | Apply | accept | |
| Airbnb · Full-Stack Software Engineer | Apply, "check first" | **override → do not apply** | posting asks 5+ years; reviewer is a new grad |
| Chime · Software Engineer, Backend (New Grad) | Consider, network first | accept | |
| Databricks · Software Engineer, New Grad | Skip, network don't apply | accept | |
| Smartsheet · Software Engineer | Skip | accept | |
| Alphabet, Google LLC, Peloton, Twilio | Held | accept | manual lookup needed |

The override is recorded here, not in the roles file, so the program's own output stays as it ran.

#### Other runs the same day

- `--census`: v0 rule 234/573 senior-only, v1 rule 214/573.
- `--title-eval`: v1 agreed with 26/28 held-out labels before the labeler corrected two misreads, 28/28 after (biased toward the rule; see worked run).
- Five break attempts: `course/2026fa/submissions/pavithra-prasad/worked-run/break-tests/break-tests-terminal.txt`.
- Tests: 25 passing on 2026-10-01; 29 after the 2026-10-02 review fixes; 32 after "try these instead" and network targets were added on 2026-10-03, `python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/test_sponsor_check.py`.

#### Open issues

- **Rule conflict, logged here as SNICKERDOODLE asks:** the assignment requires typed TODOs for proposed additions; SNICKERDOODLE forbids any open TODO above DRAFT. The recipe keeps both rules and stays DRAFT with 4 TODOs. (Logged here and not in `logs/RUN_LOG.md`, which contributors may not edit.)
- `scripts/ats/check-liveness.mjs` reports "expired" from a content heuristic on JavaScript-rendered boards. Worked around in this recipe; the maintained script is unchanged.
- `npm run doctor` counts 33 recipes and does not appear to include `recipes/cases/2026fa/`.
- Lever and Ashby postings get no API cross-check. E-Verify and parent/subsidiary data are absent.
