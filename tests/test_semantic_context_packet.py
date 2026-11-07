"""Budget boundaries must preserve source/review semantics, not just row count."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

EXAMPLE = Path(__file__).resolve().parents[1] / 'examples/political_semantics'
sys.path.insert(0, str(EXAMPLE))
from context_packet import compile_packet, encoded
from semantic_layer import load


class SemanticPacketTests(unittest.TestCase):
    def setUp(self):
        self.data = load()

    def compile(self, **kwargs):
        return compile_packet(self.data, kwargs.pop('lens', 'mediation'),
                              kwargs.pop('question', 'consent inclusion'), kwargs.pop('budget_bytes', 8000), **kwargs)

    def test_real_source_selection_keeps_complete_records_and_reference_closure(self):
        result = self.compile()
        packet = result['packet']
        self.assertTrue(packet['records'])
        originals = {row['id']: row for row in self.data['records']}
        evidence = {row['id']: row for row in packet['evidence']}
        sources = {row['id'] for row in packet['sources']}
        actors = {row['id'] for row in packet['actors']}
        concepts = {row['id'] for row in packet['concepts']}
        for row in packet['records']:
            self.assertEqual(originals[row['id']], row)
            self.assertFalse(row['human_reviewed'])
            self.assertIn(row['attributed_to'], actors)
            self.assertTrue(set(row['concept_ids']) <= concepts)
            for link in row['evidence']:
                self.assertIn(link['evidence_id'], evidence)
                self.assertIn(link['quote'], evidence[link['evidence_id']]['text'])
        self.assertTrue({row['source_id'] for row in evidence.values()} <= sources)
        self.assertEqual(result, self.compile())

    def test_exact_utf8_budget_hash_and_complete_omission_accounting(self):
        for budget in [2000, 4000, 6000, 8000, 12000, 30000]:
            result = self.compile(budget_bytes=budget, question='موافقة consent')
            receipt = result['receipt']; raw = encoded(result['packet'])
            self.assertLessEqual(len(raw), budget)
            self.assertEqual(len(raw), receipt['packet_bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt['packet_sha256'])
            ids = receipt['included'] + [row['id'] for row in receipt['omitted']]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertEqual({row['id'] for row in self.data['records']}, set(ids))

    def test_oversized_high_ranked_bundle_does_not_starve_later_evidence(self):
        target = self.data['records'][0]
        target['statement'] = 'needle ' * 12000
        result = self.compile(question='needle', budget_bytes=8000)
        self.assertIn({'id': target['id'], 'reason': 'budget'}, result['receipt']['omitted'])
        self.assertTrue(result['packet']['records'])

    def test_exact_full_bundle_boundary_admits_all_and_one_byte_less_reports_loss(self):
        complete = self.compile(budget_bytes=30000)
        exact = complete['receipt']['packet_bytes']
        accepted = self.compile(budget_bytes=exact)
        reduced = self.compile(budget_bytes=exact - 1)
        self.assertEqual(5, accepted['receipt']['retained_records'])
        self.assertEqual(exact, accepted['receipt']['packet_bytes'])
        self.assertLess(reduced['receipt']['retained_records'], 5)
        self.assertTrue(any(row['reason'] == 'budget' for row in reduced['receipt']['omitted']))

    def test_publication_filter_and_review_states_never_promote_drafts(self):
        result = self.compile(lens='media_narrative', budget_bytes=30000)
        self.assertEqual(2, len(result['packet']['records']))
        self.assertEqual(2, sum(row['reason'] == 'review_required' for row in result['receipt']['omitted']))
        historical = self.compile(published_by='2012-06-30', budget_bytes=30000)
        self.assertEqual(['record-mediation-consent'], historical['receipt']['included'])
        self.assertEqual(4, sum(row['reason'] == 'publication_cutoff' for row in historical['receipt']['omitted']))
        hr = self.compile(lens='hr_policy', budget_bytes=30000)['packet']['records'][0]
        self.assertEqual('not_assessed', hr['applicability']['status'])

    def test_tampered_quote_rejected_before_compilation(self):
        self.data['records'][0]['evidence'][0]['quote'] = 'unretained passage'
        with self.assertRaises(ValueError):
            self.compile()

    def test_boundaries_and_packet_only_cli_match_receipt_bytes(self):
        for budget in [True, 255, 8000.5]:
            with self.assertRaises(ValueError):
                self.compile(budget_bytes=budget)
        with self.assertRaises(ValueError):
            self.compile(budget_bytes=256)
        with self.assertRaises(ValueError):
            self.compile(question='')
        result = self.compile()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'packet.json'
            subprocess.run([sys.executable, str(EXAMPLE / 'context_packet.py'), '--lens', 'mediation',
                            '--question', 'consent inclusion', '--budget-bytes', '8000', '--packet-only',
                            '--out', str(output)], check=True)
            self.assertEqual(encoded(result['packet']), output.read_bytes())


if __name__ == '__main__':
    unittest.main()
