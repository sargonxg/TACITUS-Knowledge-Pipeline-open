"""Saved research packets must survive independent verification and fail on semantic tampering."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

EXAMPLE = Path(__file__).resolve().parents[1] / 'examples/political_semantics'
sys.path.insert(0, str(EXAMPLE))
from context_packet import encoded
from semantic_layer import load
from task_workflows import QUESTIONS, build_task, export, verify_package
from verify_packet import verify


class TaskWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.data = load()

    def test_every_workflow_retains_real_sources_and_unresolved_review(self):
        for task in QUESTIONS:
            work = build_task(self.data, task)
            self.assertTrue(work['context']['packet']['records'], task)
            self.assertEqual(work['approval'], 'not_reviewed')
            self.assertIsNone(work['analyst_interpretation'])
            self.assertFalse(work['hypotheses'])
            self.assertTrue(work['unresolved_checks'])
            self.assertTrue(all(c['status'] == 'requires_analyst_assessment' for c in work['unresolved_checks']))
            verify(work['context'], self.data)

    def test_valid_package_roundtrip_and_exact_packet_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'tasks'
            manifest = export(self.data, list(QUESTIONS), output, 8000)
            self.assertEqual(verify_package(output, self.data)['tasks'], 5)
            for task in QUESTIONS:
                inspection = json.loads((output / (task + '.inspection.json')).read_text(encoding='utf-8'))
                raw = (output / (task + '.packet.json')).read_bytes()
                self.assertEqual(raw, encoded(inspection['packet']))
                self.assertLessEqual(len(raw), 8000)
            self.assertEqual(len(manifest['files']), 21)

    def test_refuses_existing_directory_preserving_prior_work(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            marker = output / 'notes.txt'; marker.write_text('keep')
            with self.assertRaises(ValueError):
                export(self.data, list(QUESTIONS), output, 8000)
            self.assertEqual(marker.read_text(), 'keep')
            self.assertEqual(list(output.iterdir()), [marker])

    def test_bad_budget_leaves_no_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'tasks'
            with self.assertRaises(ValueError):
                export(self.data, list(QUESTIONS), output, 256)
            self.assertFalse(output.exists())

    def test_forged_packet_hash_cannot_hide_changed_passage(self):
        result = copy.deepcopy(build_task(self.data, 'mediation_preparation')['context'])
        result['packet']['evidence'][0]['text'] = 'A fabricated assertion'
        result['receipt']['packet_sha256'] = hashlib.sha256(encoded(result['packet'])).hexdigest()
        result['receipt']['packet_bytes'] = len(encoded(result['packet']))
        with self.assertRaises(ValueError):
            verify(result, self.data)

    def test_missing_source_and_unearned_approval_fail_verification(self):
        for edit in ['source', 'approval', 'omission']:
            result = copy.deepcopy(build_task(self.data, 'resolution_brief')['context'])
            if edit == 'source': result['packet']['sources'].pop()
            if edit == 'approval': result['packet']['records'][0]['human_reviewed'] = True
            if edit == 'omission': result['receipt']['omitted'] = []
            with self.assertRaises(ValueError): verify(result, self.data)

    def test_modified_file_and_unlisted_file_fail_package_checks(self):
        for edit in ['modified', 'extra', 'missing']:
            with tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / 'tasks'
                export(self.data, ['hr_policy_application'], output, 8000)
                if edit == 'modified': (output / 'hr_policy_application.md').write_text('Unsupported legal conclusion')
                if edit == 'extra': (output / 'unreviewed.txt').write_text('extra')
                if edit == 'missing': (output / 'hr_policy_application.packet.json').unlink()
                with self.assertRaises(ValueError): verify_package(output, self.data)

    def test_manifest_hash_rewrite_cannot_hide_fabricated_worksheet(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'tasks'; export(self.data, ['hr_policy_application'], output, 8000)
            name = 'hr_policy_application.md'; raw = b'This convention applies to every employer.'
            (output / name).write_bytes(raw)
            manifest = json.loads((output / 'manifest.json').read_text())
            manifest['files'][name] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
            (output / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError): verify_package(output, self.data)

    def test_forged_comparison_receipt_does_not_hide_omissions(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'tasks'; export(self.data, ['resolution_brief'], output, 8000)
            name = 'budget-comparison.json'
            rows = json.loads((output / name).read_text())
            rows[0]['omitted'] = []
            raw = json.dumps(rows).encode(); (output / name).write_bytes(raw)
            manifest = json.loads((output / 'manifest.json').read_text())
            manifest['files'][name] = {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
            (output / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError): verify_package(output, self.data)

    def test_manifest_cannot_promote_integrity_to_factual_or_legal_approval(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'tasks'; export(self.data, ['hr_policy_application'], output, 8000)
            manifest = json.loads((output / 'manifest.json').read_text())
            manifest['scope'] = 'Legally approved for all jurisdictions'
            (output / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError): verify_package(output, self.data)

    def test_cli_works_outside_checkout_and_verification_failure_is_nonzero(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'tasks'
            command = [sys.executable, str(EXAMPLE / 'task_workflows.py')]
            generated = subprocess.run(command + ['--task','resolution_brief','--out',str(output)], cwd=temporary, capture_output=True)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            verified = subprocess.run(command + ['--verify',str(output)], cwd=temporary, capture_output=True)
            self.assertEqual(verified.returncode, 0, verified.stderr)
            (output / 'resolution_brief.packet.json').write_bytes(b'{}')
            failed = subprocess.run(command + ['--verify',str(output)], cwd=temporary, capture_output=True)
            self.assertEqual(failed.returncode, 2)


if __name__ == '__main__': unittest.main()
