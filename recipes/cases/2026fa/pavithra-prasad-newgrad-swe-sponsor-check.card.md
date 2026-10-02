# New-grad SWE sponsor check — human card

**Audience:** an international master's student on (or about to start) OPT, applying for entry-level Software Engineer, Backend, or Full-Stack roles, who has to decide which applications deserve tailoring time.
**Agent twin:** `recipes/cases/2026fa/pavithra-prasad-newgrad-swe-sponsor-check.md`
**Status:** DRAFT v0.1.0. Runs on sample data and live postings; four additions unbuilt.

## Purpose

Answer three questions per job before you spend an hour tailoring for it: has this company sponsored *entry-level* software engineers, or only senior ones? Is the posting really open? Can hiring finish before your OPT unemployment deadline? If the records can't answer, it says so and holds the job for you instead of guessing.

## What it can verify

- The company's row in the sponsorship dataset: approvals, denials, top five sponsored titles, H-1B median salary. Or that the row is missing, blank, or duplicated.
- That a posting URL returns 404, and for Greenhouse boards, whether the job-board API says the job exists.
- Whether the company is in the shipped Form D funding samples.
- The national BLS median wage for the occupation.
- Every step of the score's arithmetic.

## What it cannot verify

- Whether the company sponsors new grads **today**. The data has the top five titles, with no year and no counts.
- Whether a title is really entry-level. A keyword rule decides; it agreed with a human on 26 of 28 unseen titles.
- Which legal entity actually sponsors. Alphabet is blank and Google LLC is missing, so those jobs are held.
- E-Verify (needed for STEM OPT), real funding beyond the samples, your fit, or your OPT dates.

## Dependencies

- Node 20+ and Python 3.9+ (tested on 3.9.6 and 3.13). No extra Python packages.
- `npm install` (for Playwright, used by the liveness checker).
- Data shipped in the repo: `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv`, `data/sec/form-d/processed/sample/`, `data/bls/compact/soc_occupation_compact.csv`.
- Live mode only: network access to the posting URLs and `boards-api.greenhouse.io`.

## Annotated commands

Run from the repo root, not from a subfolder (the first attempt from `course/…/` fails with "No such file").

Offline sample, ten fictional-persona roles (expected: Apply 3 · Consider 1 · Skip 2 · Held 4):

```bash
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --sample
```

Offline tests (expected: 25 OK):

```bash
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/test_sponsor_check.py
```

Senior-only share in the whole dataset (expected: v0 234/573, v1 214/573):

```bash
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --census
```

A posting that is really gone (expected: Skip, liveness `expired`, HTTP 404):

```bash
npm run ats:liveness -- https://boards.greenhouse.io/acmecorp/jobs/12345
```

## What it produces

- `report.md`: your decisions, next actions, the jobs held for you and why, and what was not checked.
- `run-log.json`: the same run for an agent, every value labeled record, model-judgment, or your-input.
- The scorer's own `role-scores.md` with its per-term audit.

## Named failure modes

1. **Senior-only sponsor read as "sponsors SWEs."** A company whose sponsored software titles are all Senior/Staff/Principal looks like a sponsor. The student who sees "sponsors software engineers" on a list is the one least likely to check the titles. The recipe demotes these to Consider and says "network first."
2. **Open posting reported closed.** On 2026-10-01 the repo's page checker reported Pinterest's open "University Grad Software Engineer 2027" posting as expired ("insufficient content"). The liveness gate then zeroed it. Nobody sees a skipped job, so this error is invisible unless something cross-checks. The recipe now holds such results and asks the job-board API.
3. **Missing record read as non-sponsor.** Google is absent from the CSV, and Alphabet's row is blank. Treating either as "doesn't sponsor" would skip one of the largest sponsors. The recipe holds them.
4. **"Entry-level" posting that isn't.** Databricks "Software Engineer, Web Products" scores Apply on sponsorship but asks for 4+ years. The recipe changes the next action to "check first."
