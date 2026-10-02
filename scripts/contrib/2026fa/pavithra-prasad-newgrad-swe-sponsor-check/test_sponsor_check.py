#!/usr/bin/env python3
"""Offline tests for sponsor_check.py. No network: liveness comes from
fixtures/liveness.json; the scorer is the repo's own role-scorer.mjs, run
locally with node. Run from the repo root:

  python3 scripts/contrib/2026fa/pavithra-prasad-newgrad-swe-sponsor-check/test_sponsor_check.py
"""

import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sponsor_check as sc  # noqa: E402

FIX = os.path.join(HERE, "fixtures")
GH_FIX = os.path.join(FIX, "greenhouse")
RUN_DATE = dt.date(2026, 10, 1)
LABELS = {sc.REC, sc.MODEL, sc.INPUT}


def sources(obj):
    """Every 'source' value anywhere in a nested structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "source":
                yield v
            else:
                yield from sources(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from sources(v)


class FixtureRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = tempfile.mkdtemp(prefix="test-run-", dir=HERE)
        cls.log = sc.run(os.path.join(FIX, "persona.json"), os.path.join(FIX, "roles.json"), cls.out,
                         os.path.join(FIX, "liveness.json"), RUN_DATE, GH_FIX)
        cls.by = {e["role_id"]: e for e in cls.log["evaluated"] + cls.log["held"]}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    def rec(self, rid):
        return self.by[rid]["scorer"]["recommendation"]

    def test_both_outputs_written(self):
        for f in ("run-log.json", "report.md", "roles.json", "role-scores.json", "role-scores.md"):
            self.assertTrue(os.path.exists(os.path.join(self.out, f)), f)

    def test_every_value_labeled(self):
        found = set(sources(self.log))
        self.assertTrue(found, "no labels found")
        self.assertTrue(found <= LABELS, found - LABELS)

    def test_entry_level_sponsor_applies(self):
        self.assertEqual(self.by["pinterest-swe1"]["sponsorship"]["evidence_class"]["value"], "entry-level-swe")
        self.assertEqual(self.rec("pinterest-swe1"), "Apply")

    def test_senior_only_cannot_cleanly_apply(self):  # F3
        self.assertEqual(self.by["chime-backend"]["sponsorship"]["evidence_class"]["value"], "senior-only-swe")
        self.assertNotEqual(self.rec("chime-backend"), "Apply")

    def test_dead_posting_is_gated_and_becomes_network_target(self):  # F4
        e = self.by["databricks-newgrad"]
        self.assertEqual(e["scorer"]["composite"], 0)
        self.assertEqual(self.rec("databricks-newgrad"), "Skip")
        self.assertTrue(e["next_action"].startswith("network, don't apply"))

    def test_databricks_found_in_form_d_sample(self):
        self.assertTrue(self.by["databricks-newgrad"]["funding_form_d"]["value"])

    def test_missing_row_is_held_not_zero(self):  # F1
        e = self.by["google-swe"]
        self.assertEqual(e["sponsorship"]["status"], "missing-no-row")
        self.assertNotIn("scorer", e)

    def test_blank_approvals_is_held(self):  # F2
        self.assertEqual(self.by["alphabet-swe"]["sponsorship"]["status"], "missing-blank-approvals")
        self.assertNotIn("scorer", self.by["alphabet-swe"])

    def test_ambiguous_name_is_held(self):
        self.assertEqual(self.by["peloton-fullstack"]["sponsorship"]["status"], "ambiguous-multiple-rows")

    def test_uncertain_liveness_resolved_by_api(self):
        e = self.by["uber-backend"]
        self.assertNotIn("held", e)
        self.assertEqual(e["liveness"]["value"], "active")
        self.assertIn("Greenhouse API HTTP 200", e["liveness"]["note"])

    def test_checker_api_conflict_is_held(self):
        self.assertIn("Greenhouse API HTTP 404", self.by["twilio-conflict"]["held"])

    def test_senior_posting_changes_next_action_not_score(self):
        e = self.by["airbnb-fullstack"]
        self.assertEqual(e["posting_level"]["value"], "senior")
        self.assertEqual(self.rec("airbnb-fullstack"), "Apply")
        self.assertTrue(e["next_action"].startswith("check first"))

    def test_new_grad_posting_is_entry(self):
        self.assertEqual(self.by["pinterest-swe1"]["posting_level"]["value"], "entry")

    def test_timeline_past_deadline_zeroes(self):  # F5 (per role)
        e = self.by["smartsheet-swe"]
        self.assertEqual(e["timeline"]["value"], 0.0)
        self.assertEqual(self.rec("smartsheet-swe"), "Skip")

    def test_missing_soc_row_reports_missing(self):  # F6
        w = self.by["airbnb-fullstack"]["wage_context"]
        self.assertIsNone(w["value"])
        self.assertIn("no BLS row", w["note"])

    def test_scorer_input_has_no_held_roles(self):
        with open(os.path.join(self.out, "roles.json")) as f:
            ids = {r["role_id"] for r in json.load(f)}
        self.assertEqual(ids, {e["role_id"] for e in self.log["evaluated"]})


class Stops(unittest.TestCase):
    def test_deadline_passed_stops_run(self):  # F5 (whole run)
        out = tempfile.mkdtemp(prefix="test-stop-", dir=HERE)
        try:
            with self.assertRaises(sc.StopRun) as cm:
                sc.run(os.path.join(FIX, "persona-deadline-passed.json"), os.path.join(FIX, "roles.json"), out,
                       os.path.join(FIX, "liveness.json"), RUN_DATE)
            self.assertIn("deadline", str(cm.exception))
            self.assertFalse(os.path.exists(os.path.join(out, "report.md")))
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_refuses_to_write_outside_namespace(self):
        with self.assertRaises(sc.StopRun):
            sc.run(os.path.join(FIX, "persona.json"), os.path.join(FIX, "roles.json"),
                   os.path.join(sc.REPO, "data", "examples"), os.path.join(FIX, "liveness.json"), RUN_DATE)


class Rules(unittest.TestCase):
    def test_norm_strips_suffix_words_only(self):
        self.assertEqual(sc.norm("Databricks, Inc."), sc.norm("DATABRICKS INC"))
        self.assertEqual(sc.norm("Cisco"), "cisco")

    def test_content_heuristic_expired_is_not_trusted(self):
        # regression: 2026-10-01 live run, Pinterest posting open on the API was reported expired
        self.assertEqual(sc.classify_liveness("expired", "insufficient content — likely nav/footer only")[0], "uncertain")
        self.assertEqual(sc.classify_liveness("expired", "HTTP 404")[0], "expired")
        self.assertEqual(sc.classify_liveness("active", "")[0], "active")

    def test_census_v0_reproduces_brief(self):
        c = sc.seniority_census(sc.SENIOR_RE_V0)
        self.assertEqual((c["swe_sponsor_rows"], c["senior_only_rows"]), (573, 234))

    def test_census_v1(self):
        c = sc.seniority_census()
        self.assertEqual((c["swe_sponsor_rows"], c["senior_only_rows"]), (573, 214))

    def test_v1_treats_level_2_consistently(self):
        self.assertFalse(sc.SENIOR_RE.search("Software Engineer II"))
        self.assertFalse(sc.SENIOR_RE.search("Software Engineer 2"))
        self.assertTrue(sc.SENIOR_RE.search("Software Engineer III"))
        self.assertTrue(sc.SENIOR_RE.search("Software Engineer 3"))
        self.assertFalse(sc.SENIOR_RE.search("Member of Technical Staff"))
        self.assertTrue(sc.SENIOR_RE.search("Staff Software Engineer"))
        self.assertFalse(sc.SENIOR_RE.search("Software Engineer (11525.3365)"))

    def test_posting_level_rule(self):
        mk = lambda c: {"http_status": 200, "title": "", "content": c}
        self.assertEqual(sc.posting_level(mk("4+ years of software engineering experience"))["value"], "mid")
        self.assertEqual(sc.posting_level(mk("We want university grads"))["value"], "entry")
        self.assertEqual(sc.posting_level(mk("Great team"))["value"], "unclear")
        self.assertIsNone(sc.posting_level({"http_status": 404})["value"])

    def test_offline_run_never_calls_api_without_fixtures(self):
        out = tempfile.mkdtemp(prefix="test-offline-", dir=HERE)
        try:
            log = sc.run(os.path.join(FIX, "persona.json"), os.path.join(FIX, "roles.json"), out,
                         os.path.join(FIX, "liveness.json"), RUN_DATE)
            self.assertTrue(all(e["greenhouse_api"]["value"] is None for e in log["evaluated"] + log["held"]))
        finally:
            shutil.rmtree(out, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
