# Test Report: New-Grad SWE Sponsor Check

## Executive summary

**What this is.** The record of testing the new-grad software-engineer sponsor check: the repository's health before and after the work, a run from a fresh copy of the submitted branch, each predicted failure case, and the parts only a person can judge.

**Why read it.** It shows the program runs from scratch with one command, passes the repository's checks, and fails safely on the cases it was designed to catch.

**What it found.** Everything passes from a clean checkout. The repository's own checks were healthy before and after, except for one setup gap (a missing Python package) that existed before any change. The only privacy-scanner finding is in a file that came with the repository and is not part of this branch.

---

## 1. Toolchain baseline

Full outputs are kept outside the repo in `Prompt eng/reallocation-notes/` (the scanner output contains an email address from `package-lock.json`, which would be flagged again if saved here).

| Check | Before (fresh fork, 2026-09-30, commit `015843d`) | After (branch, 2026-10-01) |
|---|---|---|
| `npm run doctor` | `environment: ✓ runnable`, exit 0 | `environment: ✓ runnable`, exit 0 |
| `npm run verify` | **exit 1**: `ModuleNotFoundError: No module named 'yaml'` → `✗ manifest check FAILED (1 error)`. Conformance itself passed (158 files). | exit 0: `conformance: 174 files … ✓ all conform`, `✓ manifest check passed (3 warnings)` |
| `node scripts/pii-scan.mjs` | 1 finding: `[email] package-lock.json` | 1 finding: `[email] package-lock.json` (same) |

- The `verify` failure was the machine's Python missing PyYAML, not a repo defect introduced here. After `python3 -m pip install --user pyyaml` (2026-09-30), `verify` passed **before any change was made**.
- The three manifest warnings exist on the unmodified fork. W2 ("private/, data/ats/ not gitignored") was checked: `git check-ignore -v` shows both ignored by `/private/*` and `/data/ats/*` in `.gitignore`; the checker does not recognise the `/*` form.
- The `package-lock.json` email is in the upstream file; this branch does not touch `package-lock.json`. CI's `pii-scan --diff` scans only the branch's changes.
- `npm run doctor` reports "33 recipes"; it does not appear to count `recipes/cases/2026fa/`.

## 2. Clean checkout of the branch

Fresh `git clone --branch contrib/2026fa-pavithra-prasad-newgrad-swe-sponsor-check` of commit `9ec71e7` into an empty temporary folder, then:

```
== clean clone of 9ec71e7 on branch contrib/2026fa-pavithra-prasad-newgrad-swe-sponsor-check at Fri Oct  2 16:26:13 EDT 2026
== npm install

added 55 packages in 2s
== npm run doctor
SUMMARY
  environment: ✓ runnable
  recipes: 33/33 carry lifecycle frontmatter — all tracked
  next: continue
== npm run verify
conformance: 174 files (88 md · 38 py · 30 js · 14 json · 4 sh)
✓ all conform (machine half of P4). Adequacy is still the human gate.
✓ manifest check passed (3 warnings)
== node scripts/pii-scan.mjs
pii-scan: 1 finding(s) — see DATA_CONTRACT.md §Zero-Conditions

  [email] package-lock.json — <email-redacted>

If a finding is a false positive (fictional data outside the sanctioned dirs),
move it under search/examples/ or resumes/ rather than allowlisting it here.
== conformance on my paths
conformance: 63 files (21 md · 40 json · 2 py)
✓ all conform (machine half of P4). Adequacy is still the human gate.
== sample
✓ 10 roles → Apply 3 · Consider 1 · Skip 2 · Held 4
  Apply     Pinterest, Inc.              tailor application
  Consider  Chime Financial Inc          network first: ask whether they sponsor new grads before tailoring
  Skip      Databricks, Inc.             network, don't apply: strong new-grad sponsor but posting closed
  Skip      Smartsheet Inc               skip
  Apply     Airbnb, Inc.                 check first: the posting asks for more experience than a new grad has; tailor only if you meet it
  Apply     Uber Technologies Inc        tailor application
  HELD      Alphabet Inc                 G-sponsorship: row exists but Total Approvals is blank or 0; this can mean the sponsoring entity has a different legal name
  HELD      Google LLC                   G-sponsorship: no row in the sponsorship CSV after name normalisation; absence of a row is not evidence of non-sponsorship
  HELD      Peloton Interactive          G-sponsorship: 2 rows match: PELOTON INTERACTIVE INC, PELOTON INTERACTIVE LLC; the script will not pick one
  HELD      Twilio Inc                   G1 liveness: uncertain (page checker said active but Greenhouse API HTTP 404); a human must open the posting
  outputs: course/2026fa/submissions/pavithra-prasad/runs/sample/{run-log.json, report.md, roles.json, role-scores.json, role-scores.md}
exit 0
== tests
----------------------------------------------------------------------
Ran 25 tests in 0.620s

OK
== git status after
 M course/2026fa/submissions/pavithra-prasad/runs/sample/role-scores.json
 M course/2026fa/submissions/pavithra-prasad/runs/sample/role-scores.md
 M package-lock.json
```

The email in the pii-scan line was redacted when saving this log. `git status after` explained:
- `role-scores.json` / `.md`: only the date line changed (`"generated": "2026-10-01"` → `"2026-10-02"`). `role-scores.mjs` stamps the wall-clock date even though `--sample` fixes the run date at 2026-10-01. Decisions and numbers are identical.
- `package-lock.json`: rewritten by `npm install` on this npm version (10.8.2). The same happened on the first install; that change was reverted and is not in the branch.

The clean checkout above used Python 3.9.6. The author also ran the 25 tests on their own machine with Python 3.13 on 2026-10-02: `Ran 25 tests in 0.657s` / `OK`. (An earlier 17-test version had passed there on 2026-10-01.)

## 3. Failure cases exercised

| Brief case | Input | Observed | Where |
|---|---|---|---|
| F1 company has no CSV row | "Google LLC" | held: `missing-no-row`, not scored | sample; `test_missing_row_is_held_not_zero` |
| F2 row with blank approvals | "Alphabet Inc" | held: `missing-blank-approvals` | sample; `test_blank_approvals_is_held` |
| (found) two matching rows | "Peloton Interactive" | held: `ambiguous-multiple-rows` | sample; `test_ambiguous_name_is_held` |
| F3 senior-only sponsor | "Chime Financial Inc" | Consider, "network first" | sample; `test_senior_only_cannot_cleanly_apply` |
| F4 posting 404 | Databricks fixture (HTTP 404) and the repo's dead example URL (live) | composite 0, Skip | sample; live-run-final; `test_dead_posting_is_gated_and_becomes_network_target` |
| (found) false "expired" | real Pinterest posting, live | run 1: wrongly Skipped. Final: Greenhouse API 200 → Apply | `WORKED-RUN.md`; `test_content_heuristic_expired_is_not_trusted` |
| (found) checker vs API conflict | Twilio fixture (page active, API 404) | held | sample; `test_checker_api_conflict_is_held` |
| F5 OPT deadline passed | `persona-deadline-passed.json` | `STOP: G0 input: OPT unemployment deadline 2026-04-05 is before run date 2026-10-01; nothing to score`, exit 2, no outputs | break B1; `test_deadline_passed_stops_run` |
| F5 hiring lag too long | Smartsheet, 210-day lag | timeline 0, Skip | sample; `test_timeline_past_deadline_zeroes` |
| F6 SOC with no BLS row | Airbnb, SOC 15-9999 | wage "missing (no BLS row)", no fallback | sample; `test_missing_soc_row_reports_missing` |
| write over a tracked file | `--out-dir data/examples` | `STOP: refusing to write outside the author's namespace`, exit 2 | break B2; `test_refuses_to_write_outside_namespace` |
| missing input field | role without `fit` | `STOP: G0 input: role no-fit is missing fit` | break B3 |
| misspelled company | "Pintrest Inc" | held: no row (no fuzzy match) | break B4 |
| bad date format | `15/01/2027` | `STOP: … not YYYY-MM-DD` | break B5 |
| network in tests | offline run without Greenhouse fixtures | API never called | `test_offline_run_never_calls_api_without_fixtures` |

Break-attempt output, verbatim: `worked-run/break-tests/break-tests-terminal.txt`.

## 4. Diff scope

```
$ git diff --stat 015843d..9ec71e7 | tail -1
 70 files changed, 7292 insertions(+)
$ git diff --name-only 015843d..9ec71e7 | cut -d/ -f1-4 | sort | uniq -c
  51 course/2026fa/submissions/pavithra-prasad
   1 logs/runs/2026fa-pavithra-prasad-1.md
   1 recipes/cases/2026fa/pavithra-prasad-newgrad-swe-sponsor-check.card.md
   1 recipes/cases/2026fa/pavithra-prasad-newgrad-swe-sponsor-check.md
  16 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check
```

Only the assigned namespaces. No maintained file, `logs/RUN_LOG.md`, `package-lock.json`, or another student's folder is touched. Insertions only, no deletions. (This report and `SUBMISSION.md` are added in a later commit, also under `course/2026fa/submissions/pavithra-prasad/`.)

## 5. What the gates require a human to judge

| Gate | The program decides | A person must judge |
|---|---|---|
| G0 Input | that fields exist and dates parse | whether the OPT dates and the hiring-lag assumption are true for them |
| G-sponsor | that a record is missing, blank, or duplicated | who the sponsoring entity really is (e.g. Google LLC under Alphabet), by looking up DOL LCA records |
| G1 Liveness | HTTP 404/410, or an API 200/404 | an uncertain or contradicted posting, by opening it |
| G2 Timeline | the date arithmetic | whether a given employer's process really takes that long |
| G3 Decision | Apply / Consider / Skip from the scorer | whether to act. On the sample, Pavithra-Prasad accepted six decisions, overrode Airbnb (asks 5+ years), and accepted the four held roles as needing lookup (`logs/runs/2026fa-pavithra-prasad-1.md`) |

The program also can't judge whether its own rules are right: the title rule's 26/28 agreement and the `SPONSOR_MAP` numbers are reported for a person to accept or argue with.
