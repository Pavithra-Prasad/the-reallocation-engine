# Frictional Log

## Executive summary

This is the honest record of building the new-grad software-engineer sponsor check over 30 September – 3 October 2026: what was tried, what went wrong, what was checked, and who did what. The work was done with an AI coding assistant (Claude Code). The assistant wrote most of the code and first drafts; I chose the domain and scope, ran the program myself, labeled the test titles, reviewed and overrode decisions, and asked the questions that exposed several of the errors below. Where an error was the assistant's, it says so.

**Who is who below:** "I" is Pavithra-Prasad. "AI" is the Claude Code assistant (model Claude Opus 5.5).

---

## 1. Attempts, expectations, what happened

| # | What was tried | Expected | What happened | Who |
|---|---|---|---|---|
| 1 | `npm run verify` on a fresh clone | pass | failed: `ModuleNotFoundError: No module named 'yaml'` (manifest check) | AI ran it; I approved installing PyYAML |
| 2 | `npm run ats:scan -- --dry-run` | a scan | `portals.yml not found`; worked with `REALLOCATION_ENGINE_PORTALS=data/ats/portals.example.yml` | AI |
| 3 | `npm install` | no repo changes | modified tracked `package-lock.json`; reverted so it stays out of the PR | AI |
| 4 | I ran `sponsor_check.py --sample` myself | output | `[Errno 2] No such file or directory`; I was inside `course/…/pavithra-prasad`. Worked after `cd` to repo root | me |
| 5 | Same run on my Python 3.13 (the AI used 3.9.6) | same result | same result, 17/17 tests passed; reran the 25-test version on 3.13 on 2026-10-02: 25/25 OK; the final 29-test version: see `TEST-REPORT.md` | me |
| 6 | First live run on real postings | Pinterest new-grad role scored | both Pinterest postings **Skipped as "expired"**; the Greenhouse API said HTTP 200 (open) | AI ran; found by comparing with the API |
| 7 | Held-out title test: I labeled 30 titles before seeing the rule | some disagreement | 26/28 agreement; 2 "maybe" excluded | me (labels), AI (eval) |
| 8 | Break attempt: misspelled "Pintrest Inc" | held | held, but the output **listed files that were never written** | AI found while reviewing the output |
| 9 | Hand cross-check: I grepped the Pinterest row from the CSV | values match the report | approvals, denials, salary, and titles matched; but the raw line contains a real phone number and officers' names, which `pii-scan` would flag in `course/`, so only the compared columns are pasted | me (ran it), AI (noticed the PII issue) |

## 2. What was checked, changed, or learned

- **Review of the first Change Brief.** I asked the AI to review its own draft critically before building. It found it had used "Meta vs Meta Platforms" as an example without checking it. Checking showed **Google, Amazon, and Meta Platforms have no rows at all, and Alphabet Inc has a blank row**. That became failure case F2 and one of the recipe's named failure modes. The same review found the brief said "the rule is mine" about a rule the AI wrote; removed.
- **"Why not use the job description?"** I suggested checking the posting text for seniority. The AI explained that the sponsorship history has no descriptions (only five titles per company), but the current posting does. I asked for it to be built. It found that **Databricks "Software Engineer, Web Products" asks 4+ years** while scoring Apply.
- **"What's n/a in the last 3 rows?"** My question exposed two problems: "not checked" was labeled model-judgment, and the sample only had posting text for 4 of 10 roles because of how the fixtures were built. Both fixed.
- **Title labels.** Two of my held-out labels disagreed with the rule. Looking again, both were misreads on my part ("Senior … (Mobile Team)" I had marked yes; "QA Analyst and Tester" I had marked no). I corrected them, but the original labels and the reason are kept in the file, and the worked run reports both numbers because the corrected one is biased toward the rule. "Prin Developer, IT" stays an open question ("Prin" may mean Principal).
- **Liveness.** Learned that "expired" from the repo's checker can mean "the page didn't render enough text," not "the job is gone." Only HTTP 404/410 is now treated as expired.
- **Learned about the lifecycle.** The AI first told me option (a), E-Verify out of scope, would allow RUNNABLE-SAMPLE. It then corrected itself: the assignment requires typed TODOs and the repo forbids any TODO above DRAFT. I chose DRAFT.

**Unresolved questions**
- Is 0.9 / 0.6 / 0.5 / 0.3 (`SPONSOR_MAP`) a sensible mapping? Nothing in the repo pins it.
- Does "Software Engineer II" really count as reachable for a new grad everywhere? It varies by company.
- Should the maintained `check-liveness.mjs` itself stop calling content-heuristic results "expired"? I worked around it in my own namespace rather than patching a maintained file.

### My reflection

*Points chosen by me from the session; wording drafted with the AI and approved by me.*

**What surprised me.** The repository's own liveness checker reported an open Pinterest new-grad posting as closed, and nothing in normal use would have shown me that mistake. I was also surprised that Google has no row in the sponsorship data at all, and that 37% of the software sponsors in the data list only senior titles. A "sponsor" list is much less useful to a new graduate than it looks.

**What I learned about working with AI.** The assistant wrote confident statements that were not true: an example it had not checked, a sentence claiming the title rule was mine, and a note saying I had reviewed the decisions before I had. My questions caught these: asking for a critical review of the draft, asking what "n/a" meant in the report, and asking why the job description wasn't used. That last question led to the posting-level check, which flags postings that ask for more experience than a new grad has (Databricks asked for 4+ years) without changing the score. I learned to treat the AI's output as a draft to verify, not an answer.

**What I would do differently.** Read titles more carefully when labeling (I misread two), ask what an unfamiliar output means as soon as I see it, and settle the project's scope earlier instead of adding features midway.

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
| Commits | branch `contrib/2026fa-pavithra-prasad-newgrad-swe-sponsor-check`: `9ec71e7` recipe, prototype, tests, docs (2026-10-02); `68b6d24` test report and reflection; a third commit applies the review fixes in §5 and §6. The final submitted SHA is in `SUBMISSION.md` in the Canvas ZIP (a file can't contain the SHA of its own commit). |

## 5. Pre-submission review

Before pushing, I had an independent AI reviewer (a fresh agent with no access to this conversation) grade the branch like a TA. Fixes made from it, 2026-10-02:

- Recipe said "three live runs"; there were four. Corrected.
- `--sample` rewrote tracked files (the scorer stamps today's date). It now writes to a gitignored `out/` folder in my namespace.
- A liveness result that my own rule had reclassified was labeled `record`; it is now `model-judgment`, with a test.
- The attestation was dated before some of its rows and did not say who ran what; now re-dated with a "Run by" column.
- E-Verify was "out of scope" in the brief but a TODO in the recipe; a brief revision now explains both.
- Added H-1B lottery/cap timing and the weakness of the timeline gate for this persona to "cannot verify". The reviewer's estimate of that weakness (about 150 days) was wrong; I computed it myself: the factor drops above a 176-day lag and the gate closes above 196.
- Reworded "about a third" to 37%, and removed a claim that Google is "one of the largest sponsors", which no record here supports.

## 6. Second review (ChatGPT)

I then gave the main files and the assignment to ChatGPT for a fresh strict grading (it estimated 45.5/59 on the parts it could score). The AI assistant checked each point against the files before anything changed. Accepted and fixed, 2026-10-02:

- **Invented fixtures labeled `record`.** Correct, and the most serious finding: test data I made up was being reported as a verified record. Fixture answers are now `your-input`, with a test.
- **The OPT deadline.** Correct: the 90 days are accumulated unemployment, not a calendar date counted from the EAD start. The program now takes days already used and states its assumption (continuous unemployment) next to the date.
- **"Every value labeled" was not true and the test did not check it.** Correct. The claim now says which fields are evidence, and a new test checks each one.
- **Overclaims in the justification and card:** "the recruiter knows they don't sponsor new grads", H-1B and STEM OPT/E-Verify run together, "has sponsored entry-level engineers". Reworded to what the data shows.
- **25 vs 26 tests and no clean checkout of the final code.** Rerun (see `TEST-REPORT.md`).
- "False 404s" in the reflection, and this log's date range. Corrected.

Rejected or partly rejected:
- **My degree.** ChatGPT said it was Software Engineering Systems. It is Information Systems; no change.
- **"Posting evidence not preserved."** Partly: `live-run-final/run-log.json` already keeps the HTTP status and matched phrase per posting (ChatGPT did not have that file). I added a sentence pointing to it rather than storing employers' posting text.
- **"The review ZIP is not runnable."** It was a review bundle, not the submission.

## 7. Two features added on the last day

After the reviews, I noticed classmates had built the same seniority idea, and asked what else could make the tool more useful. The AI offered two options; I chose to build both:

- **"Try these instead"** (the AI's recommendation): for a job that isn't a clean Apply, up to three other companies in the same city whose sponsorship record looks entry-level. Its first output suggested Uber and Pinterest, which were already in my list, so companies already in the run are now excluded.
- **Network targets** (my pick): a separate `network-targets.md` listing companies to talk to instead of applying to, each with a suggested first question. It connects the tool to the networking hours of the 3-3-2 day.

The AI said adding features on the deadline day carried risk (every saved output and document had to be regenerated). I accepted that risk. Both features add outputs only; no score or decision changed. 32 tests after this.

