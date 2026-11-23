import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'evaluations' / '2026-11-23-provider-probe'

class ProviderProbeRecording(unittest.TestCase):
    def test_checkpoint_and_six_explicit_results(self):
        manifest = json.loads((ROOT / 'manifest.json').read_text())
        for name, expected in manifest['files'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)
        report = json.loads((ROOT / 'report.json').read_text())
        self.assertEqual(report['attempted_calls'], 6)
        for row in report['records']:
            recorded = json.loads((ROOT / row['receipt']).read_text())
            self.assertEqual(recorded['response']['success'], True)
            self.assertEqual(recorded['request_sha256'], row['request_sha256'])
            answer = json.loads(recorded['response']['result']['choices'][0]['message']['content'])
            self.assertEqual(answer['claims'], row['claims'])

    def test_fidelity_failures_and_acceptance_limits_are_retained(self):
        report = json.loads((ROOT / 'report.json').read_text())
        self.assertIn('required_condition_omitted', report['records'][0]['assistant_review']['flags'])
        self.assertIn('procedural_status_strengthened_beyond_source', report['records'][5]['assistant_review']['flags'])
        self.assertLess(report['estimated_cost_usd_ignoring_cache_discount'], .25)
        for key in ('quality_gain_established', 'accepted_for_general_generation', 'generation_enabled', 'gateway_tested', 'application_dispatch_tested'):
            self.assertFalse(report[key])
