#!/usr/bin/env python3
"""sponsor_check.py — New-grad SWE sponsor check (INFO 7375, Fall 2026).

For each candidate role it gathers evidence from repo data, labels every value
record / model-judgment / your-input, writes a roles.json, runs the EXISTING
scorer (scripts/score/role-scorer.mjs), and writes two outputs:

  run-log.json  for the agent (every input, gate, label, and held role)
  report.md     for the person (decisions, next actions, what was not verified)

Roles whose sponsorship record is missing or ambiguous, or whose liveness is
uncertain, are HELD: not scored, listed for a human. No value is invented.

Usage (from repo root):
  python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --sample
  python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py --census
  python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/sponsor_check.py \
      --persona <persona.json> --roles <roles.json> --out-dir <dir> \
      [--liveness-fixture <liveness.json>] [--run-date YYYY-MM-DD]

Without --liveness-fixture, liveness is checked live with
scripts/ats/check-liveness.mjs against the posting URLs in the roles file, and
roles that carry a Greenhouse board/job id are cross-checked against
boards-api.greenhouse.io. Those are the only network hosts this script
contacts. With --liveness-fixture the run is offline: Greenhouse answers come
only from --greenhouse-fixture-dir, never the network.
"""

import argparse
import ast
import csv
import datetime as dt
import glob
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

SPONSOR_CSV = "data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv"
FORM_D_GLOB = "data/sec/form-d/processed/sample/companies-sec-*.sample.json"
BLS_CSV = "data/bls/compact/soc_occupation_compact.csv"
SCORER = "scripts/score/role-scorer.mjs"
LIVENESS = "scripts/ats/check-liveness.mjs"
# Public Greenhouse job-board API: the only other network host this script contacts.
GH_API = "https://boards-api.greenhouse.io/v1/boards/%s/jobs/%s?content=true"

# Outputs may only go inside the author's own namespaces.
ALLOWED_OUT = [
    "scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check",
    "course/2026fa/submissions/pavithra-prasad",
]

REC, MODEL, INPUT = "record", "model-judgment", "your-input"

# Seniority rule (a judgment, not a record): a sponsored title counts as SWE if
# it matches SWE_RE, and as senior if it matches SENIOR_RE.
SWE_RE = re.compile(r"software|backend|back-end|full.?stack|developer|\bSDE\b|\bSWE\b", re.I)
# v0 (first pass, kept for --title-eval): treated "II" as senior but missed "2",
# and counted "Member of Technical Staff" as senior.
SENIOR_RE_V0 = re.compile(r"senior|\bsr\b\.?|staff|principal|lead|manager|director|architect|\bIII\b|\bII\b", re.I)
# v1: level II / 2 is mid-level and reachable for a new grad; III / 3 and up,
# L5+, and "Staff" (except "Technical Staff") are senior.
SENIOR_RE = re.compile(
    r"senior|\bsr\b\.?|(?<!technical )staff|principal|lead|manager|director|architect|head of"
    r"|\b(?:III|IV|V)\b|(?:engineer|developer|SDE)\s+[3-9]\b|\bL[5-9]\b", re.I)

# Rule mapping evidence class -> scorer sponsorship term. These numbers are a
# design choice of this recipe, documented in the recipe; they are not records.
SPONSOR_MAP = {
    "entry-level-swe": {"p": 0.9, "tier": "Proven"},
    "entry-level-swe-thin": {"p": 0.6, "tier": "Likely"},   # < 10 approvals
    "senior-only-swe": {"p": 0.5, "tier": "Possible"},
    "sponsors-but-no-swe-title": {"p": 0.3, "tier": "Possible"},
}
THIN_APPROVALS = 10

SUFFIXES = {"incorporated", "inc", "llc", "corporation", "corp", "company", "co", "ltd", "lp", "plc"}


class StopRun(Exception):
    """A hard gate failed for the whole run."""


def norm(name):
    """Exact match key: lowercase words, punctuation dropped, trailing legal
    suffixes (Inc, LLC, ...) removed as whole words. No fuzzy matching."""
    words = re.sub(r"[^a-z0-9 ]", " ", (name or "").lower()).split()
    while words and words[-1] in SUFFIXES:
        words.pop()
    return "".join(words)


def num(s):
    try:
        return float(str(s).strip())
    except (TypeError, ValueError):
        return None


def parse_date(s, field):
    try:
        return dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        raise StopRun("G0 input: %s is missing or not YYYY-MM-DD (got %r)" % (field, s))


def labeled(value, source, note=None):
    out = {"value": value, "source": source}
    if note:
        out["note"] = note
    return out


# ── data loading ────────────────────────────────────────────────────────────

def load_sponsors():
    index = {}
    with open(os.path.join(REPO, SPONSOR_CSV), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            index.setdefault(norm(row["company_name"]), []).append(row)
    return index


def load_form_d():
    index = {}
    for path in sorted(glob.glob(os.path.join(REPO, FORM_D_GLOB))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for c in data.get("companies", []):
            key = norm(c["company"]["name"])
            index.setdefault(key, []).append({
                "name": c["company"]["name"],
                "date_filed": c["filing"].get("date_filed"),
                "total_amount_sold": c["funding"].get("total_amount_sold"),
                "file": os.path.relpath(path, REPO),
            })
    return index


def load_bls():
    index = {}
    with open(os.path.join(REPO, BLS_CSV), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            index.setdefault(row["bls_soc_code"], row)
    return index


# ── evidence ────────────────────────────────────────────────────────────────

def sponsorship_evidence(company, sponsors):
    rows = sponsors.get(norm(company), [])
    if not rows:
        return {"status": "missing-no-row",
                "why": "no row in the sponsorship CSV after name normalisation; absence of a row is not evidence of non-sponsorship"}
    if len(rows) > 1:
        return {"status": "ambiguous-multiple-rows",
                "why": "%d rows match: %s; the script will not pick one" % (len(rows), ", ".join(r["company_name"] for r in rows))}
    row = rows[0]
    approvals = num(row["Total Approvals"])
    if not approvals:
        return {"status": "missing-blank-approvals", "csv_name": row["company_name"],
                "why": "row exists but Total Approvals is blank or 0; this can mean the sponsoring entity has a different legal name"}
    try:
        titles = ast.literal_eval(row["top_job_titles_sponsored"] or "[]")
    except (ValueError, SyntaxError):
        titles = []
    swe = [t.strip() for t in titles if SWE_RE.search(t)]
    entry = [t for t in swe if not SENIOR_RE.search(t)]
    if not swe:
        cls = "sponsors-but-no-swe-title"
    elif not entry:
        cls = "senior-only-swe"
    elif approvals < THIN_APPROVALS:
        cls = "entry-level-swe-thin"
    else:
        cls = "entry-level-swe"
    return {
        "status": "ok",
        "csv_name": labeled(row["company_name"], REC),
        "location": labeled("%s, %s" % (row["city"], row["state"]), REC),
        "total_approvals": labeled(approvals, REC),
        "total_denials": labeled(num(row["Total Denials"]), REC),
        "top_titles_sponsored": labeled(titles, REC, "top five titles only; no per-title counts, no year"),
        "swe_titles": labeled(swe, MODEL, "keyword rule SWE_RE"),
        "entry_level_swe_titles": labeled(entry, MODEL, "keyword rule SENIOR_RE"),
        "evidence_class": labeled(cls, MODEL),
        "h1b_median_salary_offered": labeled(num(row["median_salary_offered"]), REC),
    }


def funding_evidence(company, form_d):
    hits = form_d.get(norm(company), [])
    if not hits:
        return labeled(None, REC, "not in the shipped Form D samples (50 companies per quarter); says nothing about real funding")
    return labeled(hits, REC)


def wage_evidence(soc, bls):
    row = bls.get(soc)
    if row is None:
        return labeled(None, REC, "missing: no BLS row for SOC %s" % soc)
    return {"soc_title": labeled(row["title"], REC),
            "national_annual_median_wage": labeled(num(row["annual_median_wage"]), REC),
            "oews_year": labeled(row["oews_year"], REC)}


def classify_liveness(result, reason):
    """Only an HTTP 404/410 counts as expired. check-liveness.mjs also says
    'expired' when a page shows little text (e.g. a JavaScript-rendered board);
    that is a content heuristic, so it is downgraded to uncertain and held.
    Found in the 2026-10-01 live run: a Pinterest posting open on the
    Greenhouse API was reported expired with 'insufficient content'."""
    if result == "expired" and not re.search(r"HTTP 4(04|10)", reason or ""):
        return "uncertain", "checker said expired from a content heuristic (%s), not an HTTP 404/410" % (reason or "no reason given")
    return result, reason


def liveness_results(roles, fixture_path):
    """Returns {role_id: (result, reason)} and the mode string."""
    out = {}
    if fixture_path:
        with open(fixture_path, encoding="utf-8") as f:
            saved = json.load(f)
        for r in roles:
            v = saved.get(r["role_id"], {"result": "uncertain", "reason": "no saved result"})
            if isinstance(v, str):
                v = {"result": v, "reason": {"expired": "HTTP 404", "uncertain": "saved result: uncertain"}.get(v, "")}
            out[r["role_id"]] = classify_liveness(v["result"], v.get("reason", ""))
        return out, "fixture:" + os.path.relpath(fixture_path, REPO)
    for r in roles:
        proc = subprocess.run(["node", os.path.join(REPO, LIVENESS), r["url"]],
                              cwd=REPO, capture_output=True, text=True)
        m = re.search(r"\b(active|expired|uncertain)\b\s+" + re.escape(r["url"]) + r"(?:\n[ \t]+(\S.*))?", proc.stdout)
        if m:
            out[r["role_id"]] = classify_liveness(m.group(1), (m.group(2) or "").strip())
        else:
            out[r["role_id"]] = ("uncertain", "could not parse checker output")
    return out, "live:" + LIVENESS


def greenhouse_lookup(role, fixture_dir=None):
    """Ask the Greenhouse job-board API about one posting. Needs role['greenhouse']
    = {board, job_id} (your-input). Returns {http_status, title, content} or None.
    With fixture_dir, reads <board>-<job_id>.json there instead (offline test)."""
    gh = role.get("greenhouse")
    if not gh:
        return None
    board, job_id = gh["board"], str(gh["job_id"])
    if fixture_dir:
        path = os.path.join(fixture_dir, "%s-%s.json" % (board, job_id))
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    try:
        with urllib.request.urlopen(GH_API % (board, job_id), timeout=20) as resp:
            body = json.load(resp)
            return {"http_status": resp.status, "title": body.get("title"), "content": body.get("content", "")}
    except urllib.error.HTTPError as e:
        return {"http_status": e.code, "title": None, "content": ""}
    except (urllib.error.URLError, OSError, ValueError):
        return None


def combine_liveness(checker, gh):
    """G1. The page checker and the API must not disagree. A clean API answer
    resolves an uncertain checker result; a conflict is held for a human."""
    result, reason = checker
    status = gh and gh.get("http_status")
    if status not in (200, 404, 410):
        return result, reason
    api_open = status == 200
    if result == "uncertain":
        return ("active" if api_open else "expired"), "%s; Greenhouse API HTTP %s" % (reason, status)
    if (result == "active") != api_open:
        return "uncertain", "page checker said %s but Greenhouse API HTTP %s" % (result, status)
    return result, "%s; Greenhouse API HTTP %s agrees" % (reason or result, status)


ENTRY_PHRASES = re.compile(r"new grad|university grad|recent grad|early career|entry.level|graduating (?:in|by)", re.I)
YEARS_RE = re.compile(r"(\d{1,2})\s*\+?\s*(?:-|–|to)?\s*(?:\d{1,2})?\s*\+?\s*years?(?:\s+of)?[^.]{0,40}experience", re.I)


def posting_level(gh):
    """Rule-based reading of the posting text (model-judgment, report only):
    entry if it names new/university grads or asks <= 2 years; else the minimum
    years asked for. It does not change the score, only the next action."""
    if not gh or gh.get("http_status") != 200:
        return labeled(None, MODEL, "no posting text (no Greenhouse id, or API did not return 200)")
    text = " ".join(re.sub(r"<[^>]+>", " ", html.unescape(gh.get("content") or "")).split())
    phrase = ENTRY_PHRASES.search(text) or ENTRY_PHRASES.search(gh.get("title") or "")
    years = [int(m.group(1)) for m in YEARS_RE.finditer(text)]
    min_years = min(years) if years else None
    if phrase and (min_years is None or min_years <= 2):
        return labeled("entry", MODEL, "posting says '%s'" % phrase.group(0))
    if min_years is None:
        return labeled("unclear", MODEL, "no new-grad phrase and no 'N years experience' found")
    level = "entry" if min_years <= 2 else ("mid" if min_years <= 4 else "senior")
    return labeled(level, MODEL, "posting asks %d+ years of experience" % min_years)


def timeline(persona, role, run_date):
    """G2. Returns (factor, explanation). All inputs are your-input."""
    ead = parse_date(persona.get("opt_ead_start"), "opt_ead_start")
    deadline = ead + dt.timedelta(days=int(persona["unemployment_ceiling_days"]))
    buffer_days = int(persona.get("buffer_days", 0))
    lag = int(role.get("hiring_lag_days", persona["default_hiring_lag_days"]))
    start = max(run_date + dt.timedelta(days=lag), ead)
    why = "start ≈ max(run %s + lag %dd, EAD %s) = %s; deadline %s; buffer %dd" % (
        run_date, lag, ead, start, deadline, buffer_days)
    if start > deadline:
        return 0.0, why + " → past deadline"
    if start > deadline - dt.timedelta(days=buffer_days):
        return 0.5, why + " → inside buffer"
    return 1.0, why + " → fits"


def next_action(rec, ev, live, level=None):
    if rec == "Apply":
        if level in ("mid", "senior"):
            return "check first: the posting asks for more experience than a new grad has; tailor only if you meet it"
        if level == "unclear":
            return "tailor application, after reading the posting's experience requirement (the rule could not find one)"
        return "tailor application"
    if live == "expired" and ev.get("evidence_class", {}).get("value") in ("entry-level-swe", "entry-level-swe-thin"):
        return "network, don't apply: strong new-grad sponsor but posting closed"
    if rec == "Consider":
        if ev.get("evidence_class", {}).get("value") == "senior-only-swe":
            return "network first: ask whether they sponsor new grads before tailoring"
        return "network first, then decide"
    return "skip"


# ── main flow ───────────────────────────────────────────────────────────────

def check_out_dir(out_dir):
    rel = os.path.relpath(os.path.abspath(out_dir), REPO)
    if not any(rel == a or rel.startswith(a + os.sep) for a in ALLOWED_OUT):
        raise StopRun("refusing to write outside the author's namespace: %s" % rel)
    return rel


def run(persona_path, roles_path, out_dir, liveness_fixture=None, run_date=None, greenhouse_fixture_dir=None):
    rel_out = check_out_dir(out_dir)
    with open(persona_path, encoding="utf-8") as f:
        persona = json.load(f)
    with open(roles_path, encoding="utf-8") as f:
        roles = json.load(f)

    # G0 input gate
    for k in ("opt_ead_start", "unemployment_ceiling_days", "default_hiring_lag_days"):
        if k not in persona:
            raise StopRun("G0 input: persona is missing %s" % k)
    run_date = run_date or dt.date.today()
    deadline = parse_date(persona["opt_ead_start"], "opt_ead_start") + dt.timedelta(days=int(persona["unemployment_ceiling_days"]))
    if run_date > deadline:
        raise StopRun("G0 input: OPT unemployment deadline %s is before run date %s; nothing to score" % (deadline, run_date))
    for r in roles:
        for k in ("role_id", "company", "title", "url", "fit"):
            if k not in r:
                raise StopRun("G0 input: role %s is missing %s" % (r.get("role_id", "?"), k))

    sponsors, form_d, bls = load_sponsors(), load_form_d(), load_bls()
    live, live_src = liveness_results(roles, liveness_fixture)

    evaluated, held, scorer_roles = [], [], []
    for r in roles:
        ev = sponsorship_evidence(r["company"], sponsors)
        offline = liveness_fixture is not None
        gh = None if (offline and not greenhouse_fixture_dir) else greenhouse_lookup(r, greenhouse_fixture_dir)
        live[r["role_id"]] = combine_liveness(live[r["role_id"]], gh)
        entry = {
            "role_id": r["role_id"], "company": labeled(r["company"], INPUT), "title": labeled(r["title"], INPUT),
            "url": labeled(r["url"], INPUT), "sponsorship": ev,
            "funding_form_d": funding_evidence(r["company"], form_d),
            "wage_context": wage_evidence(r.get("soc", "15-1252"), bls),
            "liveness": labeled(live[r["role_id"]][0], REC, "%s; %s" % (live_src, live[r["role_id"]][1] or "no reason")),
            "greenhouse_api": labeled(gh and gh.get("http_status"), REC,
                                      "fixture" if greenhouse_fixture_dir else ("live: boards-api.greenhouse.io" if gh else "not checked (no greenhouse id in roles file, or request failed)")),
            "posting_level": posting_level(gh),
        }
        if ev["status"] != "ok":
            entry["held"] = "G-sponsorship: " + ev["why"]
        elif live[r["role_id"]][0] == "uncertain":
            entry["held"] = "G1 liveness: uncertain (%s); a human must open the posting" % live[r["role_id"]][1]
        if "held" in entry:
            entry["next_action"] = "manual lookup before any effort"
            held.append(entry)
            continue
        t_factor, t_why = timeline(persona, r, run_date)
        entry["timeline"] = labeled(t_factor, INPUT, t_why)
        entry["fit"] = labeled(r["fit"], INPUT, "self-rated by the student; no model was called")
        sp = SPONSOR_MAP[ev["evidence_class"]["value"]]
        entry["sponsorship_term"] = labeled(sp, MODEL, "rule SPONSOR_MAP applied to the record")
        evaluated.append(entry)
        scorer_roles.append({
            "role_id": r["role_id"], "company": r["company"], "title": r["title"],
            "sponsorship": {"p": sp["p"], "tier": sp["tier"], "source": MODEL},
            "fit": {"p": r["fit"], "source": INPUT},
            "liveness": {"factor": 1.0 if live[r["role_id"]][0] == "active" else 0.0, "source": REC},
            "timeline": {"factor": t_factor, "source": INPUT},
        })

    os.makedirs(out_dir, exist_ok=True)
    roles_out = os.path.join(out_dir, "roles.json")
    profile_out = os.path.join(out_dir, "scorer-profile.json")
    with open(roles_out, "w", encoding="utf-8") as f:
        json.dump(scorer_roles, f, indent=2)
    with open(profile_out, "w", encoding="utf-8") as f:
        json.dump({"authorization": persona.get("authorization", "")}, f)

    scores = {"roles": []}
    if scorer_roles:
        proc = subprocess.run(["node", os.path.join(REPO, SCORER), roles_out, "--profile", profile_out, "--out-dir", out_dir],
                              cwd=REPO, capture_output=True, text=True)
        if proc.returncode != 0:
            raise StopRun("scorer failed: " + proc.stderr.strip())
        with open(os.path.join(out_dir, "role-scores.json"), encoding="utf-8") as f:
            scores = json.load(f)
    by_id = {s["role_id"]: s for s in scores["roles"]}
    for e in evaluated:
        s = by_id[e["role_id"]]
        e["scorer"] = {"recommendation": s["recommendation"], "composite": s["composite"], "reason": s["reason"], "arithmetic": s["trace"]["arithmetic"]}
        e["next_action"] = next_action(s["recommendation"], e["sponsorship"], e["liveness"]["value"], e["posting_level"]["value"])

    log = {
        "recipe": "pavithra-prasad-newgrad-swe-sponsor-check", "recipe_version": "0.1.0",
        "run_date": labeled(str(run_date), INPUT), "persona_file": os.path.relpath(persona_path, REPO),
        "roles_file": os.path.relpath(roles_path, REPO), "out_dir": rel_out,
        "data": {"sponsorship": SPONSOR_CSV, "form_d": FORM_D_GLOB, "bls": BLS_CSV, "scorer": SCORER},
        "liveness_mode": live_src, "opt_unemployment_deadline": labeled(str(deadline), INPUT),
        "counts": {"input": len(roles), "scored": len(evaluated), "held": len(held)},
        "evaluated": evaluated, "held": held,
    }
    with open(os.path.join(out_dir, "run-log.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, default=str)
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as f:
        f.write(render_report(log))
    return log


def render_report(log):
    ev, held = log["evaluated"], log["held"]
    recs = [e["scorer"]["recommendation"] for e in ev]
    n = lambda k: recs.count(k)
    skipped_or_held = n("Skip") + len(held)
    o = ["# New-grad SWE sponsor check — %s" % log["run_date"]["value"], "",
         "## Executive summary", "",
         "This report checks %d software job postings for a new graduate on OPT who will need visa sponsorship. "
         "It asks whether each company has a record of sponsoring entry-level software engineers, whether the posting is still open, "
         "and whether hiring can finish before the OPT unemployment deadline (%s, from the student's own dates)." % (
             log["counts"]["input"], log["opt_unemployment_deadline"]["value"]), "",
         "**Result:** Apply %d · Consider %d · Skip %d · Held for a human %d. "
         "%d of %d were skipped or held." % (n("Apply"), n("Consider"), n("Skip"), len(held), skipped_or_held, log["counts"]["input"]), "",
         "Labels: **record** = read from a repo data file; **model-judgment** = inferred by a rule in this script; **your-input** = supplied by the student, unchecked.", "",
         "## Decisions", "",
         "| Role | Decision | Next action | Sponsorship evidence | Live? | Posting level | Timeline | Form D (sample only) | H-1B median salary vs BLS median |",
         "|---|---|---|---|---|---|---|---|---|"]
    for e in sorted(ev, key=lambda e: -e["scorer"]["composite"]):
        sp = e["sponsorship"]
        wage = e["wage_context"]
        bls_w = wage.get("national_annual_median_wage", {}).get("value") if isinstance(wage, dict) and "soc_title" in wage else None
        h1b = sp["h1b_median_salary_offered"]["value"]
        fd = e["funding_form_d"]["value"]
        fd_txt = "; ".join("filed %s, sold $%s" % (h["date_filed"], "{:,.0f}".format(h["total_amount_sold"] or 0)) for h in fd) + " [record]" if fd else "not in sample"
        o.append("| %s · %s | **%s** (%.3f) | %s | %s: %d approvals; entry-level titles %s [record + model-judgment] | %s [record] | %s | %s [your-input] | %s | %s vs %s [record] |" % (
            e["company"]["value"], e["title"]["value"], e["scorer"]["recommendation"], e["scorer"]["composite"], e["next_action"],
            sp["evidence_class"]["value"], sp["total_approvals"]["value"], sp["entry_level_swe_titles"]["value"] or "none",
            e["liveness"]["value"], "%s: %s [model-judgment]" % (e["posting_level"]["value"], e["posting_level"]["note"]) if e["posting_level"]["value"] else "not checked (no posting text)",
            e["timeline"]["value"], fd_txt,
            "${:,.0f}".format(h1b) if h1b else "missing", "${:,.0f}".format(bls_w) if bls_w else "missing (no BLS row)"))
    o += ["", "## Held: a human must look these up", ""]
    if not held:
        o.append("None.")
    for e in held:
        o.append("- **%s · %s**: %s" % (e["company"]["value"], e["title"]["value"], e["held"]))
    o += ["", "## What this run did not verify", "",
          "- Whether a company sponsors *new grads today*: the CSV gives the top five sponsored titles with no year and no count per title.",
          "- Whether a title is entry-level: a keyword rule decides, and it is labeled model-judgment.",
          "- Posting level: a phrase and years-of-experience rule over the posting text (Greenhouse postings only); it can miss phrasing it does not know and it does not change the score.",
          "- E-Verify participation (needed for a STEM OPT extension): no data in the repo.",
          "- Funding: only the shipped Form D samples were searched; \"not in sample\" says nothing about real funding.",
          "- Salary: the BLS figure is a national median for the occupation, not an offer; role quality has weight 0 in the scorer, so it changed no decision.",
          "- OPT dates and hiring lag are the student's own inputs.", "",
          "## Run record", "",
          "- Liveness: `%s`" % log["liveness_mode"],
          "- Data: `%s`, `%s`, `%s`" % (log["data"]["sponsorship"], log["data"]["form_d"], log["data"]["bls"]),
          "- Scorer: `%s` (called, not copied); its own audit is `role-scores.md` in this folder" % log["data"]["scorer"],
          "- Agent log: `run-log.json` in this folder", ""]
    return "\n".join(o)


def title_eval(path=None):
    """Compare both seniority rules against hand labels (fixtures/title-labels.csv).
    A rule is right when 'senior' matches new_grad_reachable == 'no'."""
    paths = [path] if path else [os.path.join(HERE, "fixtures", n) for n in ("title-labels.csv", "title-labels-heldout.csv")]
    rows = []
    for pth in paths:
        if os.path.exists(pth):
            with open(pth, newline="", encoding="utf-8") as f:
                rows += [r for r in csv.DictReader(f) if r["new_grad_reachable"] in ("yes", "no")]
    out = {}
    for name, rule in (("v0", SENIOR_RE_V0), ("v1", SENIOR_RE)):
        res = {}
        for subset in ("random", "edge", "heldout"):
            sub = [r for r in rows if r["set"] == subset]
            if not sub:
                continue
            wrong = [r["title"] for r in sub if bool(rule.search(r["title"])) != (r["new_grad_reachable"] == "no")]
            res[subset] = {"n": len(sub), "correct": len(sub) - len(wrong), "wrong": wrong}
        out[name] = res
    return out


def seniority_census(rule=None):
    """Reproduces the brief's finding from the CSV: of rows with approvals and
    at least one SWE title in their top sponsored titles, how many list only
    senior SWE titles. The seniority rule is a model-judgment."""
    rule = rule or SENIOR_RE
    swe_sponsors = senior_only = 0
    for rows in load_sponsors().values():
        for row in rows:
            if not num(row["Total Approvals"]):
                continue
            try:
                titles = ast.literal_eval(row["top_job_titles_sponsored"] or "[]")
            except (ValueError, SyntaxError):
                continue
            swe = [t for t in titles if SWE_RE.search(t)]
            if not swe:
                continue
            swe_sponsors += 1
            senior_only += all(rule.search(t) for t in swe)
    return {"swe_sponsor_rows": swe_sponsors, "senior_only_rows": senior_only,
            "share": round(senior_only / swe_sponsors, 3) if swe_sponsors else None}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sample", action="store_true",
                    help="offline sample run: fixture persona, roles and liveness; run date 2026-10-01; "
                         "output to course/2026fa/submissions/pavithra-prasad/runs/sample")
    ap.add_argument("--census", action="store_true", help="print the senior-only share across the whole CSV (both rules) and exit")
    ap.add_argument("--title-eval", action="store_true", help="score both seniority rules against fixtures/title-labels.csv and exit")
    ap.add_argument("--persona")
    ap.add_argument("--roles")
    ap.add_argument("--out-dir")
    ap.add_argument("--liveness-fixture")
    ap.add_argument("--greenhouse-fixture-dir", help="read Greenhouse API answers from saved files instead of the network")
    ap.add_argument("--run-date")
    a = ap.parse_args(argv)
    if a.census:
        for name, rule in (("v0", SENIOR_RE_V0), ("v1", SENIOR_RE)):
            c = seniority_census(rule)
            print("census %s (%s): %d sponsor rows with a SWE title; %d list only senior SWE titles (%.1f%%) [record counted by a model-judgment keyword rule]" % (
                name, SPONSOR_CSV, c["swe_sponsor_rows"], c["senior_only_rows"], 100 * c["share"]))
        return 0
    if a.title_eval:
        for name, res in title_eval().items():
            for subset, r in res.items():
                print("rule %s, %s titles: %d/%d agree with hand labels; wrong: %s" % (
                    name, subset, r["correct"], r["n"], r["wrong"] or "none"))
        return 0
    if a.sample:
        fx = os.path.join(HERE, "fixtures")
        a.persona = a.persona or os.path.join(fx, "persona.json")
        a.roles = a.roles or os.path.join(fx, "roles.json")
        a.liveness_fixture = a.liveness_fixture or os.path.join(fx, "liveness.json")
        a.run_date = a.run_date or "2026-10-01"
        a.greenhouse_fixture_dir = a.greenhouse_fixture_dir or os.path.join(fx, "greenhouse")
        a.out_dir = a.out_dir or os.path.join(REPO, ALLOWED_OUT[1], "runs", "sample")
    if not (a.persona and a.roles and a.out_dir):
        ap.error("--persona, --roles and --out-dir are required unless --census")
    try:
        rd = dt.date.fromisoformat(a.run_date) if a.run_date else None
        log = run(a.persona, a.roles, a.out_dir, a.liveness_fixture, rd, a.greenhouse_fixture_dir)
    except StopRun as e:
        print("STOP: %s" % e, file=sys.stderr)
        return 2
    c = log["counts"]
    recs = [e["scorer"]["recommendation"] for e in log["evaluated"]]
    print("✓ %d roles → Apply %d · Consider %d · Skip %d · Held %d" % (
        c["input"], recs.count("Apply"), recs.count("Consider"), recs.count("Skip"), c["held"]))
    for e in log["evaluated"]:
        print("  %-9s %-28s %s" % (e["scorer"]["recommendation"], e["company"]["value"], e["next_action"]))
    for e in log["held"]:
        print("  %-9s %-28s %s" % ("HELD", e["company"]["value"], e["held"]))
    written = [f for f in ("run-log.json", "report.md", "roles.json", "role-scores.json", "role-scores.md")
               if os.path.exists(os.path.join(REPO, log["out_dir"], f))]
    print("  outputs: %s/{%s}" % (log["out_dir"], ", ".join(written)))
    if not log["evaluated"]:
        print("  scorer not run: no role passed the gates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
