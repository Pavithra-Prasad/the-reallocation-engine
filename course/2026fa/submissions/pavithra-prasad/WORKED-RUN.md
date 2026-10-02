# Worked Run: New-Grad SWE Sponsor Check

## Executive summary

**What this is.** A record of running the new-grad software-engineer sponsor check on real job postings, for a fictional student who graduates in December 2026 and starts OPT in January 2027.

**Why read it.** It shows the program's real output, separates what came from data from what was inferred or assumed, and records what went wrong during testing and what was changed.

**What it found.** On four real postings, the final version recommended applying to Pinterest's university-grad role, checking requirements before applying to a Databricks role that asks for four or more years, and skipping a dead link. The first version got Pinterest wrong: the repository's job-page checker called the open posting "expired," and the program believed it. That error is invisible in normal use (a skipped job is never seen again), and it would hit hardest the student who trusts "posting closed." The fix was to treat a page-reading guess as uncertain and confirm with the job board's own data.

---

## 1. Inputs

| Input | Value | Label |
|---|---|---|
| Persona | `scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/fixtures/persona.json`: "Meera Joshi (fictional)", `meera.joshi@example.com`, MS Information Systems (STEM), program end 2026-12-12, OPT EAD start 2027-01-15, 90-day unemployment ceiling, 20-day buffer, 60-day default hiring lag | your-input (invented) |
| Roles | `course/2026fa/submissions/pavithra-prasad/worked-run/roles-live.json`: 3 real postings found on the Greenhouse job-board API on 2026-10-01, plus the repo's own dead example URL | your-input |
| Fit per role | 0.8 / 0.7 / 0.6 / 0.8, self-rated for the persona | your-input |
| Run date | 2026-10-01 (system date) | your-input |

The three real postings: Pinterest "University Grad Software Engineer 2027 (USA)" (job 7838591), Databricks "Software Engineer, Web Products" Mountain View (job 8635225002), Pinterest "Software Engineer II, Big Data, tvScientific" (job 7782546).

## 2. Commands and real output

### Final live run (frozen code)

```
$ python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --persona scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/fixtures/persona.json --roles course/2026fa/submissions/pavithra-prasad/worked-run/roles-live.json --out-dir course/2026fa/submissions/pavithra-prasad/worked-run/live-run-final
✓ 4 roles → Apply 3 · Consider 0 · Skip 1 · Held 0
  Apply     Pinterest, Inc.              tailor application
  Apply     Databricks, Inc.             check first: the posting asks for more experience than a new grad has; tailor only if you meet it
  Apply     Pinterest, Inc.              tailor application, after reading the posting's experience requirement (the rule could not find one)
  Skip      Chime Financial Inc          skip
  outputs: course/2026fa/submissions/pavithra-prasad/worked-run/live-run-final/{run-log.json, report.md, roles.json, role-scores.json, role-scores.md}
exit 0
```

Decisions table from `worked-run/live-run-final/report.md`, pasted unedited:

| Role | Decision | Next action | Sponsorship evidence | Live? | Posting level | Timeline | Form D (sample only) | H-1B median salary vs BLS median |
|---|---|---|---|---|---|---|---|---|
| Pinterest, Inc. · University Grad Software Engineer 2027 (USA) | **Apply** (0.555) | tailor application | entry-level-swe: 1364 approvals; entry-level titles ['Software Engineer', 'Software Engineer II', 'Software Engineer I'] [record + model-judgment] | active [record] | entry: posting says 'university grad' [model-judgment] | 1.0 [your-input] | not in sample | $156,853 vs $133,080 [record] |
| Databricks, Inc. · Software Engineer, Web Products (Mountain View) | **Apply** (0.525) | check first: the posting asks for more experience than a new grad has; tailor only if you meet it | entry-level-swe: 1640 approvals; entry-level titles ['Software Engineer'] [record + model-judgment] | active [record] | mid: posting asks 4+ years of experience [model-judgment] | 1.0 [your-input] | filed 31-DEC-2025, sold $4,082,050,250; filed 31-DEC-2025, sold $23,017,200 [record] | $149,422 vs $90,930 [record] |
| Pinterest, Inc. · Software Engineer II, Big Data, tvScientific | **Apply** (0.495) | tailor application, after reading the posting's experience requirement (the rule could not find one) | entry-level-swe: 1364 approvals; entry-level titles ['Software Engineer', 'Software Engineer II', 'Software Engineer I'] [record + model-judgment] | active [record] | unclear: no new-grad phrase and no 'N years experience' found [model-judgment] | 1.0 [your-input] | not in sample | $156,853 vs $133,080 [record] |
| Chime Financial Inc · Deliberately dead URL (the repo's own example 404) | **Skip** (0.000) | skip | senior-only-swe: 580 approvals; entry-level titles none [record + model-judgment] | expired [record] | not checked (no posting text) | 1.0 [your-input] | not in sample | $240,108 vs $133,080 [record] |

### The same postings before the fix (live run 1, `worked-run/live-run-1-before-fix/terminal.txt`)

```
✓ 4 roles → Apply 1 · Consider 0 · Skip 3 · Held 0
  Skip      Pinterest, Inc.              network, don't apply: strong new-grad sponsor but posting closed
  Apply     Databricks, Inc.             tailor application
  Skip      Pinterest, Inc.              network, don't apply: strong new-grad sponsor but posting closed
  Skip      Chime Financial Inc          skip
  outputs: course/2026fa/submissions/pavithra-prasad/worked-run/live-run/{run-log.json, report.md, roles.json, role-scores.json, role-scores.md}
```

Two notes on this record: the run wrote to `worked-run/live-run/`, which was renamed `live-run-1-before-fix/` afterwards (the terminal line above still shows the old name). And `roles-live.json` had no `greenhouse` ids at the time; they were added before live run 3, when the API cross-check existed.

Checking why, with the repo's checker and the job-board API directly:

```
$ node scripts/ats/check-liveness.mjs "https://www.pinterestcareers.com/jobs/?gh_jid=7838591" "https://boards.greenhouse.io/pinterest/jobs/7838591" "https://databricks.com/company/careers/open-positions/job?gh_jid=8635225002"
❌ expired    https://www.pinterestcareers.com/jobs/?gh_jid=7838591
           insufficient content — likely nav/footer only
❌ expired    https://boards.greenhouse.io/pinterest/jobs/7838591
           insufficient content — likely nav/footer only
✅ active     https://databricks.com/company/careers/open-positions/job?gh_jid=8635225002

Results: 1 active  2 expired  0 uncertain
$ curl -s -o /dev/null -w "greenhouse api job: %{http_code}\n" "https://boards-api.greenhouse.io/v1/boards/pinterest/jobs/7838591"
greenhouse api job: 200
```

### Sample run (offline, the version the tests use)

```
$ python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --sample
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
```

### Census and title-rule evaluation

```
$ python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --census
census v0 (data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv): 573 sponsor rows with a SWE title; 234 list only senior SWE titles (40.8%) [record counted by a model-judgment keyword rule]
census v1 (data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv): 573 sponsor rows with a SWE title; 214 list only senior SWE titles (37.3%) [record counted by a model-judgment keyword rule]
```

Held-out titles, labeled by Pavithra-Prasad before seeing the rule's output (first labels):

```
rule v0, heldout titles: 26/28 agree with hand labels; wrong: ['Senior Software Engineer - Backend (Mobile Team)', 'Software Quality Assurance Analyst and Tester']
rule v1, heldout titles: 26/28 agree with hand labels; wrong: ['Senior Software Engineer - Backend (Mobile Team)', 'Software Quality Assurance Analyst and Tester']
```

After the labeler said both disagreements were misreads and corrected them, both rules scored 28/28. That second number is biased toward the rule, because the labels changed after seeing where the rule disagreed. Both originals are kept in `fixtures/title-labels-heldout.csv`.

## 3. Verified vs inferred, line by line (Pinterest university-grad row)

| Value in the output | Label | Where it came from |
|---|---|---|
| Company "Pinterest, Inc.", title, URL | your-input | `roles-live.json` |
| Matched CSV row `PINTEREST INC`, San Francisco, CA | record | sponsorship CSV, exact normalised match |
| 1364 approvals, 16 denials | record | CSV `Total Approvals`, `Total Denials` |
| Top sponsored titles: Software Engineer, Software Engineer II, Software Engineer I, Senior Software Engineer, Senior Data Analyst | record | CSV `top_job_titles_sponsored` |
| Which of those are SWE / entry-level | model-judgment | keyword rules `SWE_RE`, `SENIOR_RE` v1 |
| Evidence class `entry-level-swe` | model-judgment | rule on the above |
| Sponsorship term p = 0.9, tier Proven | model-judgment | `SPONSOR_MAP`, a choice of this recipe |
| Page checker: "expired, insufficient content" | record | `check-liveness.mjs` output |
| Reclassified as uncertain | model-judgment | `classify_liveness`: only HTTP 404/410 counts as expired |
| Greenhouse API HTTP 200 → active | record | `boards-api.greenhouse.io` |
| Posting level "entry" (posting says "university grad") | model-judgment | phrase rule over the posting text |
| Fit 0.8 | your-input | self-rating; no model was called |
| Timeline 1.0 (start ≈ 2027-01-15 ≤ 2027-04-15 − 20 days) | your-input | persona dates and hiring lag |
| Composite 0.555 = (0.9·0.35 + 0.8·0.3) × 1 × 1 | arithmetic by `role-scorer.mjs` | weights 0.35 / 0.30 from the scorer's CONFIG |
| Apply | scorer output | threshold 0.30 |
| H-1B median salary $156,853 | record | CSV `median_salary_offered` |
| BLS national median $133,080 (15-1252, OEWS 2024) | record | BLS compact CSV; report only, weight 0 |
| Form D: not in sample | record (absence in a 50-row sample) | says nothing about real funding |

## 4. Verification

1. **Hand cross-check against the source CSV.** Run by Pavithra-Prasad; compared columns in §4a.
2. **Cross-check against the job board.** The Greenhouse API returned 200 for Pinterest job 7838591 while the page checker said expired (pasted above).
3. **Tests.** 25 offline tests pass (`test_sponsor_check.py`; output in `TEST-REPORT.md`).
4. **Deliberate break attempts.** Five, below and in `worked-run/break-tests/break-tests-terminal.txt`.
5. **Scorer arithmetic checked by hand:** (0.9 × 0.35) + (0.8 × 0.30) = 0.315 + 0.240 = 0.555, matching the output.

### 4a. Hand cross-check (run by Pavithra-Prasad)

Run by Pavithra-Prasad on 2026-10-02, on the author's own machine:

```bash
grep "^PINTEREST INC," data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv
```

The raw line is not pasted whole: it contains the company's switchboard phone number and its officers' and directors' names. They are public business data, but `pii-scan.mjs` flags any non-555 phone number outside `data/`, so a verbatim paste here would fail CI. The compared columns, copied from that output:

| CSV column | Value in the grep output | Value in the report | Match |
|---|---|---|---|
| `company_name`, `city`, `state` | PINTEREST INC, SAN FRANCISCO, CA | (matched row) | yes |
| `Total Approvals` | 1364.0 | 1364 approvals | yes |
| `Total Denials` | 16.0 | 16 (in `run-log.json`) | yes |
| `Approval_Rate` | 98.84057971014492 | not used | — |
| `median_salary_offered` | 156853.0 | $156,853 | yes |
| `top_job_titles_sponsored` | ['Software Engineer', 'Software Engineer II', 'Software Engineer I', 'Senior Software Engineer', 'Senior Data Analyst'] | same five; three classed entry-level SWE | yes |
| `latest_funding_date` | 2017-06-02 | not used (Form D samples used instead) | — |

Pavithra-Prasad: "Yes, I confirmed the grep myself in my terminal"; the approvals, salary, and titles match the report.

## 5. Reflection

**What worked.** Holding a role instead of guessing. Four sample roles and, before the fix, two live roles were held rather than scored. Each case (no row, a blank row, two rows, a checker/API conflict) would otherwise have produced a confident wrong answer. Separating the title rule's judgment from the CSV's record also made the 41% → 37% revision easy to explain: the record didn't change, the judgment did.

**What it got wrong or missed.**
- It trusted the repo's page checker. "Expired" from a content guess zeroed an open new-grad posting at a company with 1,364 approvals. I predicted 404s; I did not predict false 404s.
- The first title rule was inconsistent ("II" senior, "2" entry), as the brief predicted.
- The output message once listed files it hadn't written (break attempt B4).
- In the report, "not checked" was labeled model-judgment until the student asked what "n/a" meant.
- The sample's description check covered only four roles until the student asked why the rest showed n/a.
- The live skip rate is 25%, below the ~50% a healthy run skips, because the live postings were hand-picked.
- The revised title rule did no better than the original on unseen titles (26/28 each). Its gains are on the edge cases it was written for.

**Next improvement.** Extend the API cross-check to Lever and Ashby boards (`[TODO: DEV]` 3 in the recipe), with saved fixtures per provider, because the false-"expired" failure is the one a student can't see.

## Attestation
- Recipe: newgrad-swe-sponsor-check v0.1.0
- By: Pavithra-Prasad · 2026-10-01

### Tested
| Ran | Saw | Expected |
|---|---|---|
| `sponsor_check.py --sample` | Apply 3 · Consider 1 · Skip 2 · Held 4; both outputs written | four held roles, none scored by guess |
| `test_sponsor_check.py` | 25 tests OK on Python 3.9.6 (AI's runs) and 3.13 (my run, 2026-10-02) | all pass offline |
| live run on 4 real postings, final code | Apply 3 · Skip 1; Pinterest university grad Apply; Databricks "check first, 4+ years" | dead URL Skips; no open posting zeroed |
| live run 1 on the same postings, first code | both open Pinterest postings Skipped as expired | (this is the defect found) |
| `--census` | v0 234/573, v1 214/573 | reproduces the brief's 234/573 under v0 |
| `--title-eval` on 28 held-out titles labeled before seeing the rule | 26/28 for both rules | an honest accuracy, not 100% |
| **Break B1:** persona whose OPT deadline passed | `STOP: G0 input: OPT unemployment deadline 2026-04-05 is before run date 2026-10-01; nothing to score`, exit 2, no outputs | stop, invent nothing |
| **Break B2:** `--out-dir data/examples` | `STOP: refusing to write outside the author's namespace: data/examples`, exit 2 | tracked file untouched |
| **Break B3:** role with no `fit` | `STOP: G0 input: role no-fit is missing fit`, exit 2 | stop, no default fit invented |
| **Break B4:** misspelled "Pintrest Inc" | held: no row in the CSV; scorer not run | no fuzzy match to Pinterest |
| **Break B5:** date `15/01/2027` | `STOP: G0 input: opt_ead_start is missing or not YYYY-MM-DD (got '15/01/2027')`, exit 2 | stop, no date guessed |

### Did not test
- Lever, Ashby, SmartRecruiters, or company-site postings with the API cross-check (not built).
- Any persona other than the two fictional ones; the 60-day hiring lag is an assumption, not measured.
- Whether `SPONSOR_MAP`'s 0.9 / 0.6 / 0.5 / 0.3 or the 10-approval cut are good choices; they reproduce sensible orderings on 14 roles, which is not evidence they are right.
- Posting-level rule on more than the 3 real and 6 invented posting texts.
- The full SEC Form D quarters (not shipped); E-Verify (no data).
- A clean checkout on a second machine.

### Broke during testing, fixed
- **False "expired" from the page checker** (live run 1): `classify_liveness` in `sponsor_check.py` now counts only HTTP 404/410 as expired; others are held. Then `greenhouse_lookup` + `combine_liveness` added the API cross-check. Regression test `test_content_heuristic_expired_is_not_trusted`.
- **Title rule inconsistency ("II" vs "2", "Technical Staff")**: `SENIOR_RE` v1; v0 kept as `SENIOR_RE_V0` for `--census` / `--title-eval`. Tests `test_v1_treats_level_2_consistently`, `test_census_v0_reproduces_brief`.
- **Liveness reason captured the wrong line** (live run 3, active URLs picked up "Results: …"): regex in `liveness_results` now requires an indented reason line.
- **Output message listed files never written** (break B4): `main()` now lists only files that exist and says when the scorer was not run.
- **"n/a" labeled model-judgment in the report**: now "not checked (no posting text)", unlabeled.
- **Sample description check covered 4 of 10 roles**: Greenhouse fixtures added for Chime, Smartsheet, Databricks.
- **Name normaliser stripped "co" from any name** ("Cisco" → "cis"), caught before the first run: suffixes are now removed only as whole words. Test `test_norm_strips_suffix_words_only`.
