# Domain Justification: New-Grad SWE Sponsor Check

## Executive summary

This recipe is for international master's students finishing in December 2026 who will job-hunt on OPT for entry-level software roles and need a future H-1B sponsor. They can't easily see whether a "sponsor" has sponsored anyone below senior level, whether a posting is really open, or whether a "new grad" job asks for four years of experience. The recipe answers these from records before tailoring time is spent, and hands back the cases the records can't settle.

## Who, in exactly what situation

An F-1 student in a STEM-designated MS program (here, Information Systems) graduating in December 2026 and starting post-completion OPT in early 2027, with at most 90 accumulated days of unemployment allowed. Targets: Software Engineer, Backend, and Full-Stack roles (SOC 15-1252, 15-1254) in Boston, New York, the Bay Area, or Seattle. They need two separate things from an employer: willingness to sponsor an H-1B later (what this recipe scores), and E-Verify enrollment for the 24-month STEM OPT extension (no data in the repo).

## The information asymmetry

1. **"Sponsors software engineers" vs "sponsors senior software engineers."** In the 80 Days data, 214 of 573 sponsor rows with software-type titles list only senior titles. A sponsor list doesn't show this. It doesn't prove a company never sponsors new grads (only five titles are recorded), but it is the evidence the student has, and it is hidden.
2. **"Posting closed" vs "page didn't render."** The repo's page checker reported Pinterest's open "University Grad Software Engineer 2027" posting as expired.
3. **"No sponsorship record" vs "record under another legal name."** Google LLC has no row; Alphabet Inc has a blank one. "Not in the data" reads as "doesn't sponsor."

## Engine layers

80 Days to Stay (sponsorship vote; Form D samples as context), Job-Ops (`check-liveness.mjs` plus the Greenhouse API, the liveness gate), Cognitive Pivot (BLS national medians as context; role quality has weight 0 in the scorer), and the visa-timeline gate. Decisions come from the existing scorer, `scripts/score/role-scorer.mjs`.

## Where it fits the 3-3-2 day

It takes over the research half of the **2 research-and-apply hours**: per posting, sponsorship history, liveness, the experience asked for, and timing.

**Estimate, not measured:** by hand, about 15 minutes per posting; for 20 postings a week, about 5 hours. With the recipe, about 2–3 minutes per posting plus lookups for held roles: **roughly 3–4 hours a week saved**. Each Skip or "check first" also avoids about 45 minutes of tailoring.

It **feeds the 3 networking hours**: senior-only sponsors and strong sponsors with closed postings go into `network-targets.md`, each with a suggested first question. For jobs that aren't a clean Apply, "try these instead" names up to three same-city companies with entry-level sponsorship records (for Chime in San Francisco: DocuSign, Maplebear, Dropbox), turning a "no" into new companies to research.

## Domain-specific failure modes

1. **The invisible false skip.** A checker that misreads a JavaScript-rendered board as "expired" zeroes an open new-grad role. A skipped job is never seen again, so the student who trusts the tool most is least likely to catch it. Mitigation: only HTTP 404/410 counts as expired; anything else is held or confirmed with the job board's API.
2. **The senior-only sponsor read as "sponsors SWEs."** Students early in the search, who trust aggregate lists, are least likely to read the titles, and tailor for companies whose recorded software sponsorships are all senior. Mitigation: the title split (model-judgment, 26/28 agreement on unseen titles) demotes these to Consider with "network first."
