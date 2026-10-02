# Frictional Log

## Executive summary

This is the honest record of building the new-grad software-engineer sponsor check over 30 September – 1 October 2026: what was tried, what went wrong, what was checked, and who did what. The work was done with an AI coding assistant (Claude Code). The assistant wrote most of the code and first drafts; I chose the domain and scope, ran the program myself, labeled the test titles, reviewed and overrode decisions, and asked the questions that exposed several of the errors below. Where an error was the assistant's, it says so.

**Who is who below:** "I" is Pavithra-Prasad. "AI" is the Claude Code assistant (model Claude Opus 5.5).

---

## 1. Attempts, expectations, what happened

| # | What was tried | Expected | What happened | Who |
|---|---|---|---|---|
| 1 | `npm run verify` on a fresh clone | pass | failed: `ModuleNotFoundError: No module named 'yaml'` (manifest check) | AI ran it; I approved installing PyYAML |
| 2 | `npm run ats:scan -- --dry-run` | a scan | `portals.yml not found`; worked with `REALLOCATION_ENGINE_PORTALS=data/ats/portals.example.yml` | AI |
| 3 | `npm install` | no repo changes | modified tracked `package-lock.json`; reverted so it stays out of the PR | AI |
| 4 | I ran `sponsor_check.py --sample` myself | output | `[Errno 2] No such file or directory`; I was inside `course/…/pavithra-prasad`. Worked after `cd` to repo root | me |
| 5 | Same run on my Python 3.13 (the AI used 3.9.6) | same result | same result, 17/17 tests passed (25/25 later) | me |
| 6 | First live run on real postings | Pinterest new-grad role scored | both Pinterest postings **Skipped as "expired"**; the Greenhouse API said HTTP 200 (open) | AI ran; found by comparing with the API |
| 7 | Held-out title test: I labeled 30 titles before seeing the rule | some disagreement | 26/28 agreement; 2 "maybe" excluded | me (labels), AI (eval) |
| 8 | Break attempt: misspelled "Pintrest Inc" | held | held, but the output **listed files that were never written** | AI found while reviewing the output |
| 9 | Hand cross-check: I grepped the Pinterest row from the CSV | values match the report | approvals, denials, salary, and titles matched; but the raw line contains a real phone number and officers' names, which `pii-scan` would flag in `course/`, so only the compared columns are pasted | me (ran it), AI (noticed the PII issue) |

## 2. What was checked, changed, or learned

- **"Is this AI slop?"** I asked the AI to review its own first Change Brief. It found it had used "Meta vs Meta Platforms" as an example without checking it. Checking showed **Google, Amazon, and Meta Platforms have no rows at all, and Alphabet Inc has a blank row**. That became failure case F2 and one of the recipe's named failure modes. The same review found the brief said "the rule is mine" about a rule the AI wrote; removed.
- **"Why not use the job description?"** I suggested checking the posting text for seniority. The AI explained that the sponsorship history has no descriptions (only five titles per company), but the current posting does. I asked for it to be built. It found that **Databricks "Software Engineer, Web Products" asks 4+ years** while scoring Apply.
- **"What's n/a in the last 3 rows?"** My question exposed two problems: "not checked" was labeled model-judgment, and the sample only had posting text for 4 of 10 roles because of how the fixtures were built. Both fixed.
- **Title labels.** Two of my held-out labels disagreed with the rule. Looking again, both were misreads on my part ("Senior … (Mobile Team)" I had marked yes; "QA Analyst and Tester" I had marked no). I corrected them, but the original labels and the reason are kept in the file, and the worked run reports both numbers because the corrected one is biased toward the rule. "Prin Developer, IT" stays an open question ("Prin" may mean Principal).
- **Liveness.** Learned that "expired" from the repo's checker can mean "the page didn't render enough text," not "the job is gone." Only HTTP 404/410 is now treated as expired.
- **Learned about the lifecycle.** The AI first told me option (a), E-Verify out of scope, would allow RUNNABLE-SAMPLE. It then corrected itself: the assignment requires typed TODOs and the repo forbids any TODO above DRAFT. I chose DRAFT.

**Unresolved questions**
- Is 0.9 / 0.6 / 0.5 / 0.3 (`SPONSOR_MAP`) a sensible mapping? Nothing in the repo pins it.
- Does "Software Engineer II" really count as reachable for a new grad everywhere? It varies by company.
- Should the maintained `check-liveness.mjs` itself stop calling content-heuristic results "expired"? I worked around it in my own namespace rather than patching a maintained file.

✍️ *Pavithra: add 2–4 sentences in your own words: what surprised you most, and what you would do differently.*

## 3. Human / AI contributions

| Area | AI did | I decided, checked, changed, or rejected |
|---|---|---|
| Domain | proposed three recipe ideas from the data | **chose** option 1 for my situation (SWE/Backend/Full-Stack, Dec 2026, OPT, four metros) |
| Scope | recommended keeping the build small, with the extras as TODOs | **rejected** that and asked for the three DEV additions to be built now |
| Posting-level check | built it | **my idea** (use the job description) |
| Privacy | flagged that my real OPT situation in the brief could count as immigration details | **chose** to describe a situation type plus a fictional persona; **agreed** to set the repo's git email to the GitHub noreply address |
| Branch name | explained the handle is required by the assignment | **questioned** whether my handle in the branch was personal data |
| Folder | — | **redirected** the clone location after rejecting the first command |
| STEM status | — | **supplied**: my degree is STEM-eligible |
| Code, tests, fixtures, recipe, card, reports | wrote the drafts | ran the program and tests myself on my machine (Python 3.13) |
| Title labels | drafted the first 52 labels and the rule | **labeled** the 30 held-out titles blind; corrected 2 misreads with the originals kept |
| Decision gate (G3) | presented the sample decisions | **reviewed** each one; **overrode** Airbnb (Apply → don't apply: asks 5+ years) |
| Status | explained the conflict | **chose** DRAFT over RUNNABLE-SAMPLE |
| Hand cross-check | gave the command; trimmed PII columns from the pasted output | **ran it** in my own terminal and confirmed the values match (WORKED-RUN §4a) |

**AI errors caught during the work:** an unchecked example (Meta), an authorship claim ("the rule is mine"), a premature "gate cleared by Pavithra-Prasad" in the recipe frontmatter (fixed to "pending" until I actually reviewed), a wrong statement about which status option (a) allowed, a name normaliser that turned "Cisco" into "cis", a liveness parser that grabbed the wrong output line, and an output message listing unwritten files.

## 4. Traceability

| Claim | Where to see it |
|---|---|
| Baselines before/after | `TEST-REPORT.md` |
| False "expired" on Pinterest | `worked-run/live-run-1-before-fix/`, `worked-run/live-run-final/`, `WORKED-RUN.md` §2 |
| Title rule v0 → v1 | `sponsor_check.py` (`SENIOR_RE_V0`, `SENIOR_RE`), `--census`, `--title-eval`, `fixtures/title-labels*.csv` |
| My held-out labels and corrections | `fixtures/title-labels-heldout.csv` (`label_note` column) |
| Break attempts | `worked-run/break-tests/break-tests-terminal.txt` |
| Gate decision and override | `logs/runs/2026fa-pavithra-prasad-1.md` |
| Predictions vs outcomes | `CHANGE-BRIEF.md`, Revisions section |
| Regression tests per fix | `test_sponsor_check.py` (test names listed in `WORKED-RUN.md`, "Broke during testing, fixed") |
| Commits | branch `contrib/2026fa-pavithra-prasad-newgrad-swe-sponsor-check` (SHA in `SUBMISSION.md`) |
