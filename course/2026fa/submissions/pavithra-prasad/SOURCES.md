# Sources and Credits

## Executive summary

This lists what the submission is built on (the repository, its governing documents, its data, outside services, and tools) and separates what the AI assistant contributed from what I decided, checked, changed, or rejected.

## Repository and governing documents

- *The Reallocation Engine*, Nik Bear Brown, `github.com/nikbearbrown/the-reallocation-engine`, forked at commit `015843d` (2026-09-30). License: see `LICENSE`.
- `SNICKERDOODLE.md` (constitution: gates, provenance, lifecycle, attestation format), `DOMAIN.md` (known gaps), `CONTRIBUTING.md` (namespaces, engine API), `DATA_CONTRACT.md` §Zero-Conditions (fictional personas), `recipes/_shared.md` (run-log template).
- Style models: `recipes/scan.md`, `recipes/local-wage-adjustment.md`, `recipes/local-wage-adjustment.card.md`.
- Assignment: *The Reallocation Engine — Recipe Design Assignment*, INFO 7375, Fall 2026.

## Code reused (called, not copied)

- `scripts/score/role-scorer.mjs`: composite, weights, threshold, Apply/Consider/Skip, audit trace.
- `scripts/ats/check-liveness.mjs` (and `scripts/ats/liveness-browser.mjs`, which it imports): page liveness.
- `scripts/conformance.mjs`, `scripts/pii-scan.mjs`, `scripts/doctor.mjs`: checks.

## Data (all shipped in the repo; none modified)

| File | Origin (per the repo) | Used for |
|---|---|---|
| `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` | 80 Days to Stay (Humanitarians AI), SEC Form D × DOL H-1B mapping | sponsorship rows, titles, H-1B median salary |
| `data/sec/form-d/processed/sample/companies-sec-{2025q2,2025q3,2025q4,2026q1}-d.sample.json` | SEC Form D, first 50 companies per quarter | funding context |
| `data/bls/compact/soc_occupation_compact.csv` | BLS OEWS 2024 + O*NET | national median wage |
| `data/ats/portals.example.yml` | repo example | baseline scan only |

## Outside services contacted

- `boards-api.greenhouse.io` (public job-board API): posting status and text for three real postings on 2026-10-01 (Pinterest jobs 7838591 and 7782546, Databricks job 8635225002), and to find them. Posting text is not stored in the repo; the test fixtures under `fixtures/greenhouse/` are invented.
- The posting URLs themselves, through `check-liveness.mjs` (Playwright).

## Personas

- "Meera Joshi" and "Test Persona" in `fixtures/` are fictional and invented for this submission, with `@example.com` addresses. No real personal data is used anywhere.

## Tools

- Claude Code (Anthropic), model Claude Opus 5.5: AI coding assistant, used throughout.
- Node 20.18.0, npm 10.8.2, Python 3.9.6 (AI's runs) and 3.13 (my runs), PyYAML 6.0.3, git 2.50.1, gh 2.88.1.

## What the AI contributed vs what I did

**AI (Claude Code):** read the repo and summarised it; profiled the data (the 573/234 census, the Alphabet/Google gap); wrote `sponsor_check.py`, `test_sponsor_check.py`, the fixtures, the README, the recipe and card, and first drafts of every document in this folder; ran the baselines, live runs, and break attempts; proposed the title rule, `SPONSOR_MAP` numbers, and the 10-approval cut.

**Me (Pavithra-Prasad):** chose the domain and target roles from my own situation; chose to model it with a fictional persona; decided scope (rejected keeping the extras as TODOs; asked for them to be built); proposed the job-description check; requested a critical review of the first brief and questioned the "n/a" cells, each of which led to a fix; questioned whether the branch name exposed personal data; ran the program and tests on my own machine; labeled 30 held-out titles blind and corrected two misreads, with the originals kept; reviewed every sample decision and overrode one; chose DRAFT as the honest status; ran the hand cross-check against the CSV in my own terminal (WORKED-RUN §4a).

**Accepted from the AI without change:** the gate design, the held-vs-scored rule, the fixture companies.
**Modified:** the brief's privacy framing (my choice, b), the report's posting-level column (after my "n/a" question), the scope (my request).
**Rejected:** the recommendation to leave the three DEV additions unbuilt; the AI's first claim that option (a) allowed RUNNABLE-SAMPLE (the AI corrected it).
