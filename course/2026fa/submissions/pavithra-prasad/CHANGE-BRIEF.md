# Change Brief: New-Grad SWE Sponsor Check

## Executive summary

**What this is.** The plan, written before building, for a job-search check for one kind of student: an international master's student who finishes in December 2026, will work on OPT, and is applying for entry-level Software Engineer, Backend, and Full-Stack jobs in Boston, New York, the San Francisco Bay Area, or Seattle.

**Why read it.** It says what the check will look at, where it stops for a person to decide, and what I expect to go wrong, so the finished work can be compared against these predictions.

**What it decides.** For each job, the check answers two questions from records: has this company sponsored software engineers at entry level, not only senior ones? Is the posting still open? It answers a third from the student's own inputs: can hiring finish before the OPT unemployment clock runs out? It then gives Apply, Consider, or Skip, with every input labeled, and a next step: tailor an application, network into the company first, or skip.

**Early finding behind it.** In the shipped sponsorship dataset, 573 companies with H-1B approvals list a software-type title among their top sponsored titles. 234 of them (about 41%) list only senior titles (Senior, Staff, Principal, Lead, II/III). "This company sponsors software engineers" can hide "there is no record it sponsors new grads." This number comes from a one-off query on 2026-09-30; the prototype has to reproduce it before it is used anywhere else.

---

## 1. Career situation and engine layers

The situation this recipe is designed for. It describes a type of student, not a specific person.

| Item | Value | Label |
|---|---|---|
| Degree | MS, Information Systems, STEM-designated (eligible for the 24-month STEM OPT extension) | your-input |
| Program end | December 2026 | your-input |
| Status after graduation | F-1 post-completion OPT; H-1B sponsorship needed later | your-input |
| Target roles | Software Engineer, Backend Developer, Full-Stack Engineer, new-grad level | your-input |
| SOC codes | 15-1252 Software Developers; 15-1254 Web Developers | record, `data/bls/compact/soc_occupation_compact.csv` |
| Target metros | Boston, NYC, SF / San Jose, Seattle; open to relocation | your-input |

"your-input" means the value comes from the student and no dataset checks it. STEM eligibility is one of these: the repo cannot confirm it. The worked run uses a fictional persona with these parameters and an `@example.com` address.

**Engine layers used:**
- 80 Days to Stay: sponsorship history (a vote) and, thinly, funding.
- Job-Ops: posting liveness (a gate).
- Cognitive Pivot: BLS national wage for 15-1252 and 15-1254, shown in the report as context, not scored.

## 2. What I reuse, and what I propose

**Reused (all exist in the repo today):**

| Path | Use |
|---|---|
| `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` | `Total Approvals`, `Total Denials`, `top_job_titles_sponsored`, `median_salary_offered`, `city`, `state` |
| `data/sec/form-d/processed/sample/companies-sec-*.sample.json` | funding recency; sample only, 50 companies per quarter |
| `data/bls/compact/soc_occupation_compact.csv` | national OEWS median wage for 15-1252 / 15-1254 |
| `scripts/ats/check-liveness.mjs` (`npm run ats:liveness`) | posting liveness |
| `scripts/score/role-scorer.mjs` (`npm run score`) | the composite score; called, not copied |

**Proposed (new, only in my namespace):**

| Path | What | Why the repo needs it |
|---|---|---|
| `scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/` | one Python script that builds `roles.json` from the records above, runs the scorer, and writes a JSON log and a Markdown report; plus an offline test and fixtures | nothing in the repo separates entry-level sponsorship evidence from senior-only evidence |
| `recipes/cases/2026fa/pavithra-prasad-newgrad-swe-sponsor-check.md` and `.card.md` | recipe and card | required by the assignment |

The seniority split is a keyword rule over the sponsored titles. The titles are a record; whether a title is entry-level is an inference the rule makes, so its output is labeled **model-judgment**, not record.

**Known gaps, not built:**
- E-Verify participation, which a STEM OPT extension requires: **[TODO: DATA SOURCE]**. The repo has no such data.
- Full SEC Form D quarters are gitignored, so the run uses the shipped samples only.
- Metro-adjusted wage: `npm run bls:local-wage` fails on a fresh clone (missing `.venv`). Stretch goal only.
- Role quality has weight 0.0 in the scorer, so the wage appears in the report and does not change any decision.

## 3. Gates (hard stops)

| Gate | Testable condition | What a human must see to clear it |
|---|---|---|
| **G0 Input** | persona and roles files parse; required fields present; the OPT unemployment deadline is still in the future | the persona's dates and assumptions printed back, labeled your-input |
| **G1 Liveness** | `check-liveness.mjs` returns `active` for the posting (a saved result in test mode) | any `expired` or `uncertain` URL; the human opens the board and confirms, or drops the role |
| **G2 Timeline** | run date + stated hiring lag ≤ OPT unemployment deadline − buffer | the three dates and the subtraction, all labeled your-input |
| **G3 Decision** | scorer ran, both outputs written, skip rate reported | the Markdown report, row by row; the human accepts or overrides each recommendation, logged in `logs/runs/2026fa-pavithra-prasad-1.md` |

Liveness and timeline are gates (multipliers in the scorer), not votes. Gate records are written to my run folder and `logs/runs/`, because `logs/gate-decisions/` does not exist.

## 4. Predicted failure cases and how I'll check each

| # | Case | Expected behaviour | How I'll check |
|---|---|---|---|
| F1 | **Company has no row in the CSV.** Checked 2026-09-30: no row starts with "Google", "Amazon", or "Meta Platforms". | sponsorship marked missing; the role is flagged for manual lookup; no value is invented | fixture role for a company with no row |
| F2 | **Company has a row but blank approvals.** Checked 2026-09-30: `ALPHABET INC` is present with empty `Total Approvals` and empty `top_job_titles_sponsored`, though Google is widely reported to sponsor, probably under another legal entity. | treated the same as F1: missing, not "does not sponsor" | fixture role for `ALPHABET INC` |
| F3 | **Company sponsors only senior SWE titles** | soft sponsorship tier, so the scorer cannot return a clean Apply | fixture with a senior-only company from the CSV |
| F4 | **Posting returns 404** | liveness gate closes, composite is 0, Skip | saved `expired` result in the test; one live run against the repo's dead example URL |
| F5 | **OPT deadline already passed, or hiring lag too long** | G0 or G2 stops with a message; no score produced | fixture persona with a past deadline |
| F6 | **SOC code with no BLS row** | wage shows "missing: no row", never a fallback number | fixture role with an invalid SOC code |

## 5. What I expect the prototype to get wrong

**The seniority rule will misclassify titles.** A keyword rule ("Senior", "Sr.", "Staff", "II", "III", "Lead") will miss conventions like "SDE I", "Engineer 2", or "Member of Technical Staff", and cannot tell when a plain "Software Engineer" was a senior hire. The CSV lists only the top five titles, with no count per title and no year, so the rule cannot say how many approvals were entry-level. On the first pass, "has an entry-level title" will be trusted more than it should be.

**The funding join will add almost nothing.** Each sample quarter has 50 companies, and only 2 to 6 of them match any company name in the full CSV (mostly funds and holding companies; Databricks is one exception). The CSV's own latest funding date is September 2025. I expect most roles to show funding as "not in sample."

---

## Revisions

*Original predictions stay as written above; later corrections are added here with a date.*

- **2026-09-30, before building (review of the first draft).** The first draft used "Meta vs Meta Platforms Inc" as a name-mismatch example without checking it. Checking showed something different: there is no Meta Platforms, Google, or Amazon row at all, and `ALPHABET INC` has a row with blank sponsorship fields. F1 now uses checked examples and F2 is new. The first draft also said "the rule is mine" about the seniority rule; the AI assistant drafted that rule, so the line was removed (see `FRICTIONAL.md`).

- **2026-10-01, first prototype run.** The prototype reproduced 573 and 234 exactly (`--census`). Correction to the wording above: these are **rows** of the CSV, not companies. One company can have more than one row (Peloton Interactive has an INC row and an LLC row), so "573 companies" overstates by an unknown small number.
- **2026-10-01, prediction 5 (seniority rule) came true.** The first-pass rule (v0) called "Software Engineer II" senior but "Software Engineer 2" entry-level, called "Member of Technical Staff" senior, and missed "Software Engineer 3" and "(L5)". A revised rule (v1) treats level II/2 as mid-level and reachable. Under v1 the senior-only count is **214 of 573 rows (37.3%)**, not 234 (40.8%). The 41% in the executive summary above is the v0 figure and is kept as originally written.
- **2026-10-01, a failure case I did not predict.** The repository's page-liveness checker reported two open Pinterest postings as "expired" because the page showed too little text. My F4 assumed "expired" meant a real 404. Now only HTTP 404/410 counts as expired; other "expired" results are held and cross-checked with the Greenhouse job-board API.
- **2026-10-01, second prediction partly wrong.** I predicted the Form D join would add almost nothing. On the sample it matched one target company (Databricks, two filings in 2025Q4). Still thin, but not nothing.
- **2026-10-01, scope added after the brief.** At the student's request, three items first planned as proposed additions were built: title rule v1, the Greenhouse API cross-check, and a posting-level check from the job description. Each is labeled (record or model-judgment) in the outputs. E-Verify was moved out of scope as a stated limit.
- **2026-10-02, E-Verify clarified.** "Out of scope" above means out of scope for v0.1.0: there is no E-Verify data in the repo, so nothing is built and the report says it is unchecked. The recipe still lists it as a proposed addition (`[TODO: DATA SOURCE]` #1), which is one of the four open TODOs that keep the recipe at DRAFT. The two statements describe the same decision.
- **2026-10-02, F5 and G2 were modelled wrongly.** The brief (and the first code) treated "EAD start + 90 days" as a calendar deadline. The 90 days count accumulated unemployment, so the deadline is a date only under an assumption. The program now takes `unemployment_days_used` and computes `max(EAD start, run date) + (90 − days used)`, stating that it assumes no work in between. F5's test case is now "all 90 days used" instead of "deadline already past". Found by an outside review, not predicted here.
- **2026-10-03, two features added at the student's request.** "Try these instead" (same-city companies whose sponsorship record looks entry-level, labeled model-judgment) and `network-targets.md` (roles to network into, with template questions). Neither was predicted here. Both are new outputs only: they do not change any score or decision.
