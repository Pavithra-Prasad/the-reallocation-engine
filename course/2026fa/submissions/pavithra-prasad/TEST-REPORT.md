# Test Report: New-Grad SWE Sponsor Check

## Executive summary

**What this is.** The record of testing the new-grad software-engineer sponsor check: the repository's health before and after the work, a run from a fresh copy of the final branch, each predicted failure case, and the parts only a person can judge.

**Why read it.** It shows the program runs from scratch with one command, passes the repository's checks, and fails safely on the cases it was designed to catch.

**What it found.** Everything passes from a clean checkout of the final code: 32 tests, conformance, the repository's verify and doctor checks, and the privacy scan of the branch history. The only setup problem (a missing Python package) existed before any change was made.

---

## 1. Toolchain baseline

Full outputs are kept outside the repo in `Prompt eng/reallocation-notes/` (the working-tree scanner output contains an email address from `package-lock.json`, which would be flagged again if saved here).

| Check | Before (fresh fork, 2026-09-30, commit `015843d`) | After (final commit `ed9eacd`, 2026-10-03) |
|---|---|---|
| `npm run doctor` | `environment: ✓ runnable`, exit 0 | `environment: ✓ runnable`, exit 0 |
| `npm run verify` | **exit 1**: `ModuleNotFoundError: No module named 'yaml'` → `✗ manifest check FAILED (1 error)`. Conformance itself passed (158 files). | exit 0: `conformance: 174 files … ✓ all conform`, `✓ manifest check passed (3 warnings)` |
| `node scripts/pii-scan.mjs` (working tree) | 1 finding: `[email] package-lock.json` | same 1 finding, in the upstream file |
| `node scripts/pii-scan.mjs --diff 015843d` (branch history, what CI runs) | — | `pii-scan: clean ✓` |

- The `verify` failure was the machine's Python missing PyYAML. After `python3 -m pip install --user pyyaml` (2026-09-30), `verify` passed **before any change was made**.
- The three manifest warnings exist on the unmodified fork. W2 ("private/, data/ats/ not gitignored") was checked: `git check-ignore -v` shows both ignored by `/private/*` and `/data/ats/*` in `.gitignore`; the checker does not recognise the `/*` form.
- The `package-lock.json` email is in the upstream file; this branch does not change `package-lock.json`.
- `npm run doctor` reports "33 recipes"; it does not appear to count `recipes/cases/2026fa/`.

## 2. Clean checkout of the final branch

Fresh `git clone --branch contrib/2026fa-pavithra-prasad-newgrad-swe-sponsor-check` of commit `ed9eacd` into an empty temporary folder, then:

```
== clean clone of ed9eacd on branch contrib/2026fa-pavithra-prasad-newgrad-swe-sponsor-check at Sat Oct  3 17:02:59 EDT 2026
== python3 --version
Python 3.9.6
== npm install

added 55 packages in 1s
== npm run doctor (last 3 lines)
  environment: ✓ runnable
  recipes: 33/33 carry lifecycle frontmatter — all tracked
  next: continue
== npm run verify
conformance: 174 files (88 md · 38 py · 30 js · 14 json · 4 sh)
✓ all conform (machine half of P4). Adequacy is still the human gate.
✓ manifest check passed (3 warnings)
== node scripts/pii-scan.mjs --diff 015843d
pii-scan: clean ✓
== conformance on my paths
conformance: 67 files (25 md · 40 json · 2 py)
✓ all conform (machine half of P4). Adequacy is still the human gate.
== sample
$ python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --sample
✓ 10 roles → Apply 3 · Consider 1 · Skip 2 · Held 4
  Apply     Pinterest, Inc.              tailor application
  Consider  Chime Financial Inc          network first: ask whether they sponsor new grads before tailoring
                                         try instead: DOCUSIGN INC, MAPLEBEAR INC, DROPBOX INC
  Skip      Databricks, Inc.             network, don't apply: strong new-grad sponsor but posting closed
                                         try instead: DOCUSIGN INC, MAPLEBEAR INC, DROPBOX INC
  Skip      Smartsheet Inc               skip
                                         try instead: ZIPSTORM INC, PETABYTE TECHNOLOGY INC
  Apply     Airbnb, Inc.                 check first: the posting asks for more experience than a new grad has; tailor only if you meet it
  Apply     Uber Technologies Inc        tailor application
  HELD      Alphabet Inc                 G-sponsorship: row exists but Total Approvals is blank or 0; this can mean the sponsoring entity has a different legal name
  HELD      Google LLC                   G-sponsorship: no row in the sponsorship CSV after name normalisation; absence of a row is not evidence of non-sponsorship
  HELD      Peloton Interactive          G-sponsorship: 2 rows match: PELOTON INTERACTIVE INC, PELOTON INTERACTIVE LLC; the script will not pick one
  HELD      Twilio Inc                   G1 liveness: uncertain (page checker said active but Greenhouse API HTTP 404); a human must open the posting
                                         try instead: DOCUSIGN INC, MAPLEBEAR INC, DROPBOX INC
  network targets: Chime Financial Inc, Databricks, Inc.
  outputs: scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/out/sample/{run-log.json, report.md, network-targets.md, roles.json, role-scores.json, role-scores.md}
exit 0
== tests
$ python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/test_sponsor_check.py
----------------------------------------------------------------------
Ran 32 tests in 0.880s

OK
== git status after
 M package-lock.json
```

- `git status after`: only `package-lock.json`, rewritten by `npm install` on this npm version (10.8.2). No tracked file of this branch changed: `--sample` writes to the gitignored `out/` folder.
- **Python versions for the final 32-test version:** 3.9.6 (above, run by the AI assistant) and 3.13 (run by the author on their own machine on 2026-10-03: `Ran 32 tests in 0.944s` / `OK`).

## 3. Failure cases exercised

| Brief case | Input | Observed | Where |
|---|---|---|---|
| F1 company has no CSV row | "Google LLC" | held: `missing-no-row`, not scored | sample; `test_missing_row_is_held_not_zero` |
| F2 row with blank approvals | "Alphabet Inc" | held: `missing-blank-approvals` | sample; `test_blank_approvals_is_held` |
| (found) two matching rows | "Peloton Interactive" | held: `ambiguous-multiple-rows` | sample; `test_ambiguous_name_is_held` |
| F3 senior-only sponsor | "Chime Financial Inc" | Consider, "network first"; listed in `network-targets.md` | sample; `test_senior_only_cannot_cleanly_apply`, `test_network_targets` |
| F4 posting 404 | Databricks fixture (HTTP 404) and the repo's dead example URL (live) | composite 0, Skip | sample; live-run-final; `test_dead_posting_is_gated_and_becomes_network_target` |
| (found) false "expired" | real Pinterest posting, live | run 1: wrongly Skipped. Final: Greenhouse API 200 → Apply | `WORKED-RUN.md`; `test_content_heuristic_expired_is_not_trusted` |
| (found) checker vs API conflict | Twilio fixture (page active, API 404) | held | sample; `test_checker_api_conflict_is_held` |
| F5 OPT unemployment days used up | `persona-deadline-passed.json` (90 of 90 days used) | `STOP: G0 input: unemployment days used (90) have reached the ceiling (90); nothing to score`, exit 2, no outputs | break B1; `test_deadline_passed_stops_run`, `test_opt_clock_counts_used_days` |
| F5 hiring lag too long | Smartsheet, 210-day lag | timeline 0, Skip | sample; `test_timeline_past_deadline_zeroes` |
| F6 SOC with no BLS row | Airbnb, SOC 15-9999 | wage "missing (no BLS row)", no fallback | sample; `test_missing_soc_row_reports_missing` |
| invented fixture data | sample run | liveness and Greenhouse answers labeled your-input, never record | `test_fixture_answers_are_never_records` |
| write over a tracked file | `--out-dir data/examples` | `STOP: refusing to write outside the author's namespace`, exit 2 | break B2; `test_refuses_to_write_outside_namespace` |
| missing input field | role without `fit` | `STOP: G0 input: role no-fit is missing fit` | break B3 |
| misspelled company | "Pintrest Inc" | held: no row (no fuzzy match); scorer not run | break B4 |
| bad date format | `15/01/2027` | `STOP: … not YYYY-MM-DD` | break B5 |
| "try these instead" | Chime (San Francisco) | same-city entry-level sponsors not already in the run; none for an Apply or a role with no row | `test_try_instead_same_city_entry_level_not_in_run`, `test_try_instead_only_when_not_apply_and_never_guessed` |
| network in tests | offline run without Greenhouse fixtures | API never called | `test_offline_run_never_calls_api_without_fixtures` |

Break-attempt output, verbatim: `worked-run/break-tests/break-tests-terminal.txt` (re-run on the final code, 2026-10-03).

## 4. Diff scope

```
$ git diff --stat 015843d..ed9eacd | tail -1
 76 files changed, 8027 insertions(+)
$ git diff --name-only 015843d..ed9eacd | cut -d/ -f1-4 | sort | uniq -c
  56 course/2026fa/submissions/pavithra-prasad
   1 logs/runs/2026fa-pavithra-prasad-1.md
   1 recipes/cases/2026fa/pavithra-prasad-newgrad-swe-sponsor-check.card.md
   1 recipes/cases/2026fa/pavithra-prasad-newgrad-swe-sponsor-check.md
  17 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check
```

Only the assigned namespaces. No maintained file, `logs/RUN_LOG.md`, `package-lock.json`, or another student's folder is touched. Insertions only, no deletions. This report is updated in one more commit, also under `course/2026fa/submissions/pavithra-prasad/`.

## 5. What the gates require a human to judge

| Gate | The program decides | A person must judge |
|---|---|---|
| G0 Input | that fields exist, dates parse, and unemployment days remain | whether the OPT dates, days used, and hiring-lag assumption are true for them |
| G-sponsor | that a record is missing, blank, or duplicated | who the sponsoring entity really is (e.g. Google LLC under Alphabet), by looking up DOL LCA records |
| G1 Liveness | HTTP 404/410, or an API 200/404 | an uncertain or contradicted posting, by opening it |
| G2 Timeline | the date arithmetic, under a stated continuous-unemployment assumption | whether a given employer's process really takes that long |
| G3 Decision | Apply / Consider / Skip from the scorer, plus "try these instead" and network targets | whether to act. On the sample, Pavithra-Prasad accepted six decisions, overrode Airbnb (asks 5+ years), and accepted the four held roles as needing lookup (`logs/runs/2026fa-pavithra-prasad-1.md`) |

The program also can't judge whether its own rules are right: the title rule's 26/28 agreement and the `SPONSOR_MAP` numbers are reported for a person to accept or argue with.
