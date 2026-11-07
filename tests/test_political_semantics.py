"""Evidence integrity and deterministic task selection, without network or APIs."""

import copy
import importlib.util
import json
import sqlite3
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "examples/political_semantics/semantic_layer.py"
SPEC = importlib.util.spec_from_file_location("political_semantic_example", MODULE)
semantic = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(semantic)


class PoliticalSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.data = semantic.load()

    def rejects(self, update, pattern):
        update(self.data)
        with self.assertRaisesRegex(ValueError, pattern):
            semantic.validate(self.data)

    def test_verified_sources_and_common_primitives_are_retained(self):
        semantic.validate(self.data)
        self.assertEqual(5, len(self.data["sources"]))
        self.assertEqual(3, sum(x["verification"] == "direct_pdf" for x in self.data["sources"]))
        primitives = {r["primitive"] for group in ("actors", "records", "evidence") for r in self.data[group]}
        self.assertEqual(semantic.PRIMITIVES, primitives)
        self.assertFalse(any(r["human_reviewed"] for r in self.data["records"]))

    def test_excerpt_tampering_and_wrong_quote_fail_independently(self):
        original = copy.deepcopy(self.data)
        self.rejects(lambda d: d["evidence"][0].update(text="replacement text"), "hash mismatch")
        self.data = original
        self.rejects(lambda d: d["records"][0]["evidence"][0].update(quote="not present"), "quote does not match")

    def test_dangling_references_rejected(self):
        self.rejects(lambda d: d["records"][0]["evidence"][0].update(evidence_id="missing"), "dangling evidence")

    def test_attribution_chain_and_author_references_checked(self):
        self.rejects(lambda d: d["records"][6].update(attribution_chain=["missing"]), "dangling attribution chain")

    def test_indexed_candidate_is_not_verified_source_evidence(self):
        self.rejects(lambda d: d["evidence"][-1].update(review_state="source_verified"), "cannot be promoted")

    def test_human_review_needs_explicit_identity_time_and_decision(self):
        self.rejects(lambda d: d["records"][0].update(review_state="human_reviewed"), "flag and state")
        self.data = semantic.load()
        self.rejects(lambda d: d["records"][0].update(review_state="human_reviewed", human_reviewed=True), "reviewer identity")
        self.data = semantic.load()
        record = self.data["records"][0]
        record.update(review_state="human_reviewed", human_reviewed=True,
                      review={"reviewer": "unit-test reviewer (not a real corpus review)",
                              "reviewed_at": "2026-11-07T00:00:00Z", "decision": "approved"})
        semantic.validate(self.data)

    def test_adopted_text_cannot_be_promoted_to_observed_implementation(self):
        self.rejects(lambda d: d["records"][0].update(implementation="observed"), "does not prove implementation")

    def test_interpretation_cannot_be_relabelled_as_verified_source_wording(self):
        self.rejects(lambda d: d["records"][7].update(review_state="source_verified"), "masquerade")

    def test_bias_score_and_equivalence_overclaims_rejected(self):
        self.rejects(lambda d: d["sources"][3].update(bias_score=0.5), "unsupported equivalence")
        self.data = semantic.load()
        self.rejects(lambda d: d["concepts"][0].update({"owl:sameAs": "https://example.org/concept"}), "unsupported equivalence")

    def test_temporal_fields_are_distinct_and_intervals_cannot_be_invented(self):
        source = next(x for x in self.data["sources"] if x["id"] == "source-geneva")
        event = next(x for x in self.data["records"] if x["primitive"] == "Event")
        self.assertEqual("2013-09-27", source["published"]["value"])
        self.assertEqual("2012-06-30", event["time"]["occurred_on"])
        self.assertIsNone(event["time"]["valid_from"])
        self.rejects(lambda d: d["records"][0]["time"].update(valid_from="2015-12-18"), "unknown validity")

    def test_query_excludes_drafts_and_hr_applicability_candidates(self):
        media = semantic.query(self.data, "media_narrative")
        self.assertEqual(["record-headline", "record-reported-position"], [x["id"] for x in media["records"]])
        self.assertEqual(4, len(semantic.query(self.data, "media_narrative", include_drafts=True)["records"]))
        self.assertEqual([], semantic.query(self.data, "hr_policy")["records"])
        self.assertEqual(1, len(semantic.query(self.data, "hr_policy", include_drafts=True)["records"]))
        self.rejects(lambda d: d["records"][-1]["applicability"].update(status="applies"), "cannot determine HR")

    def test_publication_cutoff_does_not_claim_historical_truth(self):
        early = semantic.query(self.data, "mediation", published_by="2012-08-01")
        self.assertEqual(["record-mediation-consent"], [x["id"] for x in early["records"]])
        guidance = next(x for x in self.data["sources"] if x["id"] == "source-guidance")
        guidance["published"] = {"value": "2012", "precision": "year"}
        self.assertEqual([], semantic.query(self.data, "mediation", published_by="2012-08-01")["records"])
        self.assertEqual(1, len(semantic.query(self.data, "mediation", published_by="2012-12-31")["records"]))

    def test_jsonld_is_deterministic_and_all_local_references_resolve(self):
        first = semantic.export_jsonld(self.data)
        self.data["records"].reverse()
        self.assertEqual(first, semantic.export_jsonld(self.data))
        identifiers = {x["@id"] for x in first["@graph"]}
        for node in first["@graph"]:
            for key in ("prov:wasDerivedFrom", "prov:wasAttributedTo", "dct:subject"):
                refs = node.get(key, [])
                if isinstance(refs, dict):
                    refs = [refs]
                for ref in refs:
                    self.assertIn(ref["@id"], identifiers)
        self.assertNotIn("sameAs", json.dumps(first))

    def test_sql_export_integrity_and_lens_results_agree(self):
        sql = semantic.export_sql(self.data)
        with sqlite3.connect(":memory:") as db:
            db.executescript(sql)
            self.assertEqual([], db.execute("PRAGMA foreign_key_check").fetchall())
            self.assertEqual(("ok",), db.execute("PRAGMA integrity_check").fetchone())
            rows = db.execute("""SELECT a.id FROM policy_semantic_verified_assertions a
                    JOIN policy_semantic_assertion_lenses l ON l.assertion_id=a.id
                    WHERE l.lens_id='mediation' ORDER BY a.id""").fetchall()
            self.assertEqual([x["id"] for x in semantic.query(self.data, "mediation")["records"]], [x[0] for x in rows])
            self.assertEqual(5, db.execute("SELECT COUNT(*) FROM policy_semantic_recipes").fetchone()[0])
            with self.assertRaises(sqlite3.IntegrityError):
                with db:
                    db.execute("INSERT INTO policy_semantic_assertion_lenses VALUES ('missing', 'record-headline')")


if __name__ == "__main__":
    unittest.main()
