# Domain Justification: New-Grad SWE Sponsor Check

## Executive summary

This recipe is for international master's students finishing in December 2026 who will job-hunt on OPT for entry-level software roles and need a future H-1B sponsor. They can't easily see whether a "sponsor" sponsors new graduates or only senior hires, whether a posting is really open, or whether a "new grad" job quietly asks for four years of experience. The recipe answers these from records before any tailoring time is spent, and it hands back to the student the cases the records can't settle.

## Who, in exactly what situation

An F-1 student in a STEM-designated MS program (here, Information Systems) who graduates in December 2026 and starts post-completion OPT in early 2027. From the EAD start date, the student has 90 days of allowed unemployment. They are applying for Software Engineer, Backend, and Full-Stack roles (SOC 15-1252, 15-1254) in Boston, New York, the Bay Area, or Seattle, and they need an employer that will file an H-1B within OPT, plus a STEM extension. Their target list is the one every such student builds: big-name tech companies and well-funded startups.

## The information asymmetry

From the outside, three things look the same as their opposites:

1. **"Sponsors software engineers" vs "sponsors senior software engineers."** In the 80 Days data, 214 of 573 sponsor rows with software-type titles list *only* senior titles (rule v1; 234 under the first rule). The student sees a company on a sponsor list; the recruiter knows the company sponsors staff engineers and not new grads.
2. **"Posting closed" vs "page didn't render."** The repo's page checker reported Pinterest's open "University Grad Software Engineer 2027" posting as expired. A student who trusts a tool's "closed" never looks again.
3. **"No sponsorship record" vs "record under another legal name."** Google LLC has no row; Alphabet Inc has a blank row. "Not in the data" reads as "doesn't sponsor."

## Engine layers

- **80 Days to Stay:** sponsorship history (a vote) and Form D funding from the samples (context).
- **Job-Ops:** `check-liveness.mjs` plus the Greenhouse API (the liveness gate).
- **Cognitive Pivot:** BLS national medians for 15-1252/15-1254 next to the H-1B median salary (context only, since role quality carries weight 0 in the scorer).
- **Visa timeline:** the OPT unemployment deadline (a gate).

Decisions come from the existing scorer, `scripts/score/role-scorer.mjs`.

## Where it fits the 3-3-2 day

It takes over the research half of the **2 research-and-apply hours**: for each candidate posting, checking sponsorship history, whether the posting is open, the experience asked for, and the timeline.

**Estimate, not measured:** done by hand, those checks take roughly 15 minutes per posting (an H-1B lookup site, the company's titles, the posting, a calendar). For 20 postings a week, that's about 5 hours. With the recipe, the student reads one report, about 2–3 minutes per posting, plus manual lookups for held roles, so **roughly 3–4 hours a week saved**. The larger saving is indirect: every Skip or "check first" avoids roughly 45 minutes of tailoring.

It also **feeds the 3 networking hours**. Two outputs are networking targets, not applications: "network first" (a senior-only sponsor with a new-grad posting, like Chime in the sample) and "network, don't apply" (a strong new-grad sponsor whose posting closed). A tested, honest prototype is also a credibility-hours project in itself.

## Domain-specific failure modes

1. **The invisible false skip.** A liveness checker that misreads a JavaScript-rendered board as "expired" zeroes an open new-grad role at a strong sponsor. The student never sees a skipped job, so nothing prompts a second look. This is hardest to catch for the student who uses the tool most faithfully. Mitigation: only HTTP 404/410 counts as expired; everything else is held or confirmed with the job board's API.
2. **The senior-only sponsor read as "sponsors SWEs."** A company list that says "sponsors software engineers" sends a new grad to tailor for companies with no new-grad sponsorship record. Students early in the search, who trust aggregate lists, are least likely to read the titles. Mitigation: the title split, labeled model-judgment, demotes these to Consider with "network first." Its own error (26/28 agreement on unseen titles) is reported.
