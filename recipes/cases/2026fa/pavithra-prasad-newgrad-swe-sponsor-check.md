---
status: DRAFT
todos_open: 4
last_gate: "sample run + three live runs, 2026-10-01, logs/runs/2026fa-pavithra-prasad-1.md (G3 decision gate on the sample run cleared by Pavithra-Prasad, 2026-10-01)"
attestation: null
recipe_version: 0.1.0
---

# newgrad-swe-sponsor-check — Entry-level SWE sponsorship, liveness, and OPT timing

## Executive summary

**What this is.** A procedure, plus the program that runs it, for one kind of job seeker: an international master's student who graduates in December 2026, will work on OPT, will need H-1B sponsorship later, and is applying for entry-level Software Engineer, Backend, and Full-Stack jobs in Boston, New York, the San Francisco Bay Area, or Seattle.

**Why read it.** "Does this company sponsor software engineers?" is the question most such students ask, and it hides a second one: *does it sponsor new graduates, or only senior hires?* In the shipped sponsorship data, about a third of companies with software-type sponsored titles list only senior titles. The procedure also catches two quieter errors: a job page reported as closed when it is still open, and an "entry-level" posting that actually asks for four or more years of experience.

**What it decides.** For each job: Apply, Consider, or Skip, from the repository's existing scorer; a next step (tailor an application, network into the company first, check the requirements first, or skip); and a list of jobs it refuses to score because a record is missing, ambiguous, or contradicted. A person reviews the result before acting.

**Why it is still a draft.** The program runs end to end on sample data and on live postings. The recipe stays at the first lifecycle stage because the repository's rule allows no open to-do items above that stage, and four proposed additions below are not built.

---

## Lifecycle note

The core path was run on the fixture sample and on three live runs (evidence in `logs/runs/2026fa-pavithra-prasad-1.md` and `course/2026fa/submissions/pavithra-prasad/worked-run/`). Under `SNICKERDOODLE.md`, DRAFT → SPECIFIED requires zero open TODOs. The assignment requires proposed additions marked as typed TODOs. Both rules are kept: the four additions are listed as open TODOs, so the status is DRAFT. The conflict is recorded in the run log, not resolved silently.

## Required reads

1. `SNICKERDOODLE.md`: gates, provenance, TODO closure.
2. `DOMAIN.md`: what runs today, known gaps.
3. `DATA_CONTRACT.md` §Zero-Conditions: fictional personas only.
4. `scripts/score/role-scorer.mjs` header: the composite formula, weights, and threshold.
5. `scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/README.md`: commands.

## Source inventory

| Path | What it provides | Label |
|---|---|---|
| `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` | `company_name`, `city`, `state`, `Total Approvals`, `Total Denials`, `top_job_titles_sponsored` (top five only), `median_salary_offered` | record |
| `data/sec/form-d/processed/sample/companies-sec-*.sample.json` | Form D filings, 50 companies per quarter, 2025Q2–2026Q1 | record (report only) |
| `data/bls/compact/soc_occupation_compact.csv` | national OEWS median wage by SOC | record (report only) |
| `scripts/ats/check-liveness.mjs` (`npm run ats:liveness`) | page-level liveness: active / expired / uncertain + reason | record |
| `https://boards-api.greenhouse.io/v1/boards/<board>/jobs/<id>?content=true` | posting status (HTTP 200/404) and posting text, for Greenhouse boards only | record |
| `scripts/score/role-scorer.mjs` (`npm run score`) | composite, Apply/Consider/Skip, per-term audit trace | called, not copied |
| `scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py` | this recipe's program | — |

Network hosts contacted: the posting URLs in the roles file (through `check-liveness.mjs`) and `boards-api.greenhouse.io`. Nothing else. With `--liveness-fixture`, nothing.

## Commands

From the repo root:

```bash
# offline sample run (fixtures; run date fixed at 2026-10-01)
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --sample

# offline tests (25)
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/test_sponsor_check.py

# live run on your own roles file
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py \
  --persona scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/fixtures/persona.json \
  --roles <roles.json> --out-dir course/2026fa/submissions/pavithra-prasad/runs/<name>

# reproduce the senior-only share, old and new title rule
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --census

# score both title rules against the hand labels
python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --title-eval
```

The `snickerdoodle` CLI named in older recipes does not run anywhere; these are the commands.

## Inputs

**Persona file** (all your-input; the shipped one is fictional): `opt_ead_start` (YYYY-MM-DD), `unemployment_ceiling_days` (90 for post-completion OPT), `buffer_days`, `default_hiring_lag_days`, `authorization` (free text passed to the scorer's profile; must read as needing sponsorship).

**Roles file**, one object per posting (all your-input): `role_id`, `company`, `title`, `url`, `fit` (0–1, self-rated; no model is called), optional `soc` (default 15-1252), optional `hiring_lag_days`, optional `greenhouse: {board, job_id}`.

## Phase gates

Hard stops. Each has a condition a script tests and a thing a person must look at.

| Gate | Testable condition | On failure | Human clears it by |
|---|---|---|---|
| **G0 Input** | persona and roles parse; required fields present; `opt_ead_start + unemployment_ceiling_days` is after the run date | whole run stops (`STOP:` on stderr, exit 2), no outputs written | reading the dates printed in the report summary |
| **G-sponsor** | exactly one CSV row after name normalisation, with `Total Approvals` > 0 | role **held**, not scored: `missing-no-row`, `missing-blank-approvals`, or `ambiguous-multiple-rows` | looking the company up in DOL LCA data by hand |
| **G1 Liveness** | page checker `active`, or `expired` with HTTP 404/410; Greenhouse API, when present, agrees | `expired` from a content heuristic → `uncertain`; API 200/404 resolves it; checker vs API conflict → **held** | opening the posting |
| **G2 Timeline** | projected start ≤ deadline − buffer (factor 1); inside buffer → 0.5; after deadline → 0 | factor 0 zeroes the composite in the scorer | checking the three dates and the hiring-lag assumption |
| **G3 Decision** | scorer exited 0; `report.md` and `run-log.json` written | — | reading `report.md` row by row, accepting or overriding each decision; logged in `logs/runs/` |

Liveness and timeline enter the scorer as multipliers (gates), not votes. Gate records go to the run folder and `logs/runs/`; `logs/gate-decisions/` does not exist.

## Workflow

1. **G0.** Load persona and roles; stop on any failed condition.
2. **Sponsorship lookup.** Normalise the company name (lowercase, drop punctuation, drop trailing Inc/LLC/Corp/Co/Ltd/LP/PLC as whole words) and match exactly. No fuzzy matching. Apply G-sponsor.
3. **Title split.** From the matched row's top sponsored titles, keep software titles (`SWE_RE`) and mark senior ones (`SENIOR_RE`, v1). Evidence class: `entry-level-swe` (≥ 10 approvals and at least one non-senior SWE title), `entry-level-swe-thin` (< 10 approvals), `senior-only-swe`, `sponsors-but-no-swe-title`. Label: model-judgment.
4. **Liveness.** Run `check-liveness.mjs` per URL; reclassify content-heuristic `expired` as `uncertain`; cross-check with the Greenhouse API when the role has a board and job id. Apply G1.
5. **Posting level.** From the Greenhouse posting text: `entry` if it names new/university/recent grads or asks ≤ 2 years; `mid` 3–4 years; `senior` ≥ 5; `unclear` otherwise. Model-judgment, report only.
6. **Timeline (G2).** `start = max(run date + hiring lag, opt_ead_start)`; `deadline = opt_ead_start + unemployment_ceiling_days`.
7. **Context, report only.** Form D sample match; national BLS median for the role's SOC vs the CSV's H-1B median salary.
8. **Score.** Write `roles.json` (held roles excluded) and call `node scripts/score/role-scorer.mjs roles.json --profile scorer-profile.json --out-dir <out>`.
9. **Next action and outputs** (below). Stop at G3 for the person.

## Scoring choices (model-judgment, stated so they can be argued with)

`SPONSOR_MAP` turns the evidence class into the scorer's sponsorship term:

| Evidence class | p | Tier passed to scorer | Effect |
|---|---|---|---|
| entry-level-swe | 0.9 | Proven | can reach Apply |
| entry-level-swe-thin | 0.6 | Likely | soft tier: Apply demoted to Consider |
| senior-only-swe | 0.5 | Possible | soft tier: Consider at best |
| sponsors-but-no-swe-title | 0.3 | Possible | soft tier |

These numbers are this recipe's choice, not records, so the scorer term is labeled model-judgment even though the inputs to the rule are records. The cut at 10 approvals is also a choice.

**How the repository's known gaps are handled:**

- *Role quality has weight 0.0 in the scorer.* The recipe does not pass a role-quality term and does not propose a weight. The BLS median and the H-1B median salary appear in the report as context and change no decision.
- *`bls:local-wage` feeds nothing and fails on a fresh clone.* Not used. National medians only, labeled as national.
- *Only Form D samples ship.* Funding is searched in the samples and shown as "not in sample" otherwise. It is not a vote: the scorer has no funding term, and a 50-company sample cannot support one.
- *`data/raw/`, `data/verified/`, `logs/gate-decisions/` don't exist.* Not referenced as live paths.
- *`snickerdoodle` CLI is roadmap.* Not used.
- *`validate-h1b-join-sample.py` needs full data.* Not used; the program reads the shipped CSV directly.

## What it can verify

- Whether a named company has exactly one row in the 80 Days CSV, and that row's approvals, denials, top five sponsored titles, and H-1B median salary, exactly as recorded.
- Whether that row is missing, blank, or duplicated, and which of those it is.
- Whether a posting URL returns HTTP 404/410, and, for Greenhouse postings, whether the job-board API returns 200 or 404 for that job id.
- Whether a company appears in the shipped Form D samples, with filing date and amount sold.
- The national OEWS median for a SOC code, or that no row exists.
- The arithmetic of every score: the scorer's trace shows each term, weight, source label, and gate.
- That the senior-only share in the CSV is 214 of 573 sponsor rows under title rule v1 (234 under v0), as counted by `--census`.

## What it cannot verify

- **Whether a company sponsors new grads now.** The CSV has the top five titles, no per-title counts, no years. "Has an entry-level title" means one appeared in the top five at some point.
- **Whether a title is entry-level.** A keyword rule decides. On 28 held-out titles labeled by a person before seeing the rule's output, v1 agreed on 26 (93%); after the labeler corrected two misreads, 28/28, a number biased toward the rule. It does not know abbreviations such as "Prin" (Principal).
- **Who the sponsoring legal entity is.** `ALPHABET INC` is in the CSV with blank approvals; `GOOGLE LLC` is absent. Parent and subsidiary are not linked, so such roles are held.
- **Liveness on non-Greenhouse boards** beyond the page checker, which reported two open Pinterest postings as expired from a content heuristic on 2026-10-01.
- **Posting level outside Greenhouse**, or phrased in ways the rule does not know.
- **E-Verify participation**, which a STEM OPT extension requires.
- **Real funding.** Form D samples cover 50 companies per quarter.
- **Fit.** It is the student's self-rating.
- **OPT dates, hiring lag, and the 90-day rule's application to a given case.** Student inputs; not legal advice.

## Output contract

Both written to `--out-dir`, which must sit inside `scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/` or `course/2026fa/submissions/pavithra-prasad/` (anything else stops the run).

**For the agent, `run-log.json`:** `recipe`, `recipe_version`, `run_date`, `persona_file`, `roles_file`, `out_dir`, `data` (paths), `liveness_mode`, `opt_unemployment_deadline`, `counts {input, scored, held}`, `evaluated[]`, `held[]`. Each role carries `company`, `title`, `url`, `sponsorship` (status, and when ok: `csv_name`, `location`, `total_approvals`, `total_denials`, `top_titles_sponsored`, `swe_titles`, `entry_level_swe_titles`, `evidence_class`, `h1b_median_salary_offered`), `funding_form_d`, `wage_context`, `liveness`, `greenhouse_api`, `posting_level`, and for scored roles `timeline`, `fit`, `sponsorship_term`, `scorer {recommendation, composite, reason, arithmetic}`, `next_action`; for held roles `held` (reason) and `next_action`. Every value is `{value, source, note?}` with source one of record / model-judgment / your-input.

**For the person, `report.md`:** executive summary (counts, deadline, label key); decisions table (role, decision with composite, next action, sponsorship evidence, live?, posting level, timeline, Form D, H-1B vs BLS median); held roles with reasons; what the run did not verify; run record.

Also written: `roles.json` and `scorer-profile.json` (scorer inputs), `role-scores.json` and `role-scores.md` (scorer outputs).

## Stop conditions

Stop and invent nothing when:

- G0 fails (missing field, bad date, OPT deadline already past).
- The scorer exits non-zero.
- `--out-dir` is outside the two allowed folders.
- Asked to score a held role by guessing its sponsorship, or to treat "no row" as "does not sponsor". Refuse.
- Asked to treat a content-heuristic "expired" as closed. Refuse; hold it.
- Asked to change `SPONSOR_MAP`, the title rule, or hand labels so that a preferred company passes. Refuse; changes to the rule are re-evaluated with `--title-eval` and `--census` and logged.

## Next action per result (the 3-3-2 day)

| Result | Next action | Hours it feeds |
|---|---|---|
| Apply, posting level entry | tailor application | the 2 apply hours |
| Apply, posting level unclear | tailor after reading the experience requirement | the 2 apply hours |
| Apply, posting level mid/senior | check first; tailor only if you meet it | saves apply hours |
| Consider, senior-only sponsor | network first: ask whether they sponsor new grads | the 3 networking hours |
| Skip, posting closed, strong new-grad sponsor | network, don't apply | the 3 networking hours |
| Skip, otherwise | skip | time returned |
| Held | manual lookup before any effort | — |

## Proposed additions

Each is unbuilt in v0.1.0.

1. [TODO: DATA SOURCE] **E-Verify employer list.** The STEM OPT extension requires an E-Verify employer. Needed: a dated, sourced list at a named path under `data/`, joined on the same normalised name. Until then the report says this is unchecked.
2. [TODO: DATA SOURCE] **Parent/subsidiary entity map.** Alphabet/Google shows the CSV's company rows do not always name the sponsoring entity. Needed: a sourced mapping file so a held role can be resolved by a record rather than by a guess.
3. [TODO: DEV] **API cross-check for Lever and Ashby boards.** The Greenhouse check resolved both false "expired" results in the live run; the same check is missing for the other providers `scripts/ats/` already detects. Handoff: offline fixtures per provider, tests passing.
4. [TODO: DEV] **Larger independently labeled title set.** v1 was written after seeing the first 52 labels; only 28 held-out titles test it. Needed: 100+ titles labeled by someone other than the rule's author, including abbreviations ("Prin", "Sr Mgr"), with `--title-eval` results logged before and after any rule change.

## Run-log template (`logs/runs/2026fa-pavithra-prasad-<n>.md`)

```markdown
## Executive summary
<what was run, on what, what it decided, in plain language>

## Run record
- **Date:** YYYY-MM-DD
- **Recipe:** newgrad-swe-sponsor-check v<version>
- **Inputs:** persona file, roles file, liveness mode (fixture | live), Greenhouse mode (fixture | live | off)
- **Command:** <exact command>
- **Outputs:** <out-dir>/{run-log.json, report.md, roles.json, role-scores.json, role-scores.md}
- **Result:** Apply n · Consider n · Skip n · Held n
- **Gates:** G0 <pass/stop> · G-sponsor held n · G1 held n · G2 zeroed n · G3 cleared by <name> on <date>
- **Open issues:** <what did not work or is still missing>
```
