from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tacitus_pipeline.core import PipelineError, canonical, digest, load_collection, write_bundle
from tacitus_pipeline.interchange import app_bundle, collection_diff
from tacitus_pipeline.selection import select_layer

ROOT = Path(__file__).resolve().parents[1]


class InterchangeTests(unittest.TestCase):
    def setUp(self):
        self.data = load_collection(ROOT / 'examples/team-handoff/collection.json')
        self.ontology = json.loads((ROOT / 'ontology/team-knowledge.json').read_text())
        self.layer = json.loads((ROOT / 'layers/team-handoff.json').read_text())
        self.question = 'What context must travel with a recommendation to another teammate?'

    def test_export_preserves_unicode_sources_and_exact_manifest(self):
        bundle = app_bundle(self.data, self.ontology, self.layer, question=self.question)
        self.assertEqual(bundle, json.loads((ROOT / 'examples/team-handoff/app-bundle.json').read_text()))
        self.assertEqual(bundle['sha256'], digest({key: value for key, value in bundle.items() if key != 'sha256'}))
        self.assertNotIn('file', bundle['collection']['sources'][0])
        self.assertEqual(bundle['collection']['sources'][0]['text'][0], '🧭')
        self.assertTrue(all(row['review_state'] == 'proposed' for row in bundle['capsule']['statements']))

    def test_changed_source_identifies_affected_interpretations(self):
        after = deepcopy(self.data)
        after['sources'][0]['version'] = 'a' * 64
        self.assertEqual(len(collection_diff(self.data, after)['interpretations_requiring_review']), 3)
        self.assertEqual(collection_diff(self.data, self.data)['changed_sources'], [])

    def test_lexical_and_graph_selection_keep_required_qualifications(self):
        for mode in ['bm25', 'graph']:
            layer, explanation = select_layer(self.data, self.ontology, self.layer, self.question, mode=mode, limit=1)
            self.assertTrue(set(self.layer['required_statement_ids']) <= set(layer['statement_ids']))
            self.assertEqual(explanation['model_calls'], 0)
            app_bundle(self.data, self.ontology, layer, question=self.question)

    def test_export_refuses_modified_source_and_approval_promotion(self):
        bad = deepcopy(self.data)
        bad['sources'][0]['text'] += 'altered'
        with self.assertRaises(PipelineError):
            app_bundle(bad, self.ontology, self.layer, question=self.question)
        bad = deepcopy(self.data)
        bad['statements'][0]['review_state'] = 'approved'
        with self.assertRaises(PipelineError):
            app_bundle(bad, self.ontology, self.layer, question=self.question)

    def test_failed_directory_swap_restores_the_complete_previous_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'bundle'
            write_bundle({'a.json': {'version': 1}}, output)
            rename = Path.rename
            def failed_stage(path, target):
                if path.name == 'stage':
                    raise OSError('Synthetic failed rename')
                return rename(path, target)
            with patch.object(Path, 'rename', failed_stage), self.assertRaises(OSError):
                write_bundle({'a.json': {'version': 2}}, output, force=True)
            self.assertEqual((output / 'a.json').read_text(), canonical({'version': 1}) + '\n')
            self.assertFalse(output.with_name('bundle.lock').exists())

    def test_standards_view_preserves_exact_passages_and_proposed_status(self):
        from tacitus_pipeline.standards import standards_graph
        view = standards_graph(self.data, self.ontology, self.layer)
        passages = [row for row in view['@graph'] if 'tacitus:codepointStart' in row]
        self.assertEqual(len(passages), 3)
        for passage in passages:
            self.assertEqual(self.data['sources'][0]['text'][passage['tacitus:codepointStart']:passage['tacitus:codepointEnd']], passage['prov:value'])
        self.assertTrue(all(row.get('tacitus:reviewState', 'proposed') == 'proposed' for row in view['@graph']))
