#!/usr/bin/env python3
"""Replay assembly and verify historical provider records. No inference/network."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
sys.path.insert(0, str(REPO / 'reference-pipeline/src'))
from tacitus_pipeline.core import build, load_collection, PipelineError
from tacitus_pipeline.interchange import app_bundle


def source_edition_case():
    """Rebuild the existing real-source fixture, without fetching or inference."""
    fixture = REPO/'reference-pipeline/examples/citation-guidance'
    spec = importlib.util.spec_from_file_location('tacitus_paper_edition_case', fixture/'compile.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    proof, bundle = module.compile_proof()
    assert proof == json.loads((fixture/'proof.json').read_text())
    assert proof['comparison']['wording_unchanged'] is True
    assert proof['comparison']['modality'] == 'suggested guidance'
    assert proof['status'] == 'proposed'
    assert proof['receipt']['context_bytes'] == 4726
    assert proof['receipt']['source_records'] == 2
    assert proof['receipt']['selected_statements'] == 3
    assert proof['receipt']['model_calls'] == 0
    assert not proof['receipt']['model_quality_gain_established']
    return {
        'publication': 'TAC-2026-01', 'version': '1.1',
        'evidence_scope': 'Offline source-edition assembly check; development material, not held-out efficacy evidence.',
        'pdf_verification': 'Capture includes official PDF hashes. This publication replay verifies the pinned extracted text; it does not download PDFs.',
        'proof': proof,
        'capsule': bundle['capsule.json'],
        'graph': bundle['graph.json'],
        'standards': bundle['standards.jsonld'],
    }


def replay():
    collection = load_collection(ROOT / 'demo/collection.json')
    ontology = json.loads((REPO/'reference-pipeline/ontology/team-knowledge.json').read_text())
    layer = json.loads((ROOT/'demo/layer.json').read_text())
    bundle = build(collection, ontology, layer,
                   question='Does the supplied material establish final renewal approval, and what context must travel with the answer?',
                   budget=18000)
    assert len(bundle['capsule.json']['statements']) == 4
    assert not bundle['capsule.json']['omissions']
    assert bundle['receipt.json']['model_calls'] == 0
    assert not bundle['receipt.json']['model_quality_gain_established']
    assert all(s['review_state']=='proposed' for s in bundle['capsule.json']['statements'])
    bundle['app-bundle.json'] = app_bundle(collection, ontology, layer,
        question=bundle['capsule.json']['question'], budget=18000)
    try:
        build(collection, ontology, layer, question='Retain the complete decision context.', budget=2000)
    except PipelineError as error:
        assert 'Required complete evidence exceeds the budget' in str(error)
    else:
        raise AssertionError('Required context must not be silently truncated')

    probe = REPO/'reference-pipeline/evaluations/2026-11-23-provider-probe'
    manifest = json.loads((probe/'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        assert hashlib.sha256((probe/name).read_bytes()).hexdigest() == expected, name
    report = json.loads((probe/'report.json').read_text())
    assert report['attempted_calls'] == report['responses_received'] == 6
    prompt = completion = 0
    for row in report['records']:
        recorded = json.loads((probe/row['receipt']).read_text())
        assert recorded['response']['success'] is True
        assert recorded['request_sha256'] == row['request_sha256']
        claims = json.loads(recorded['response']['result']['choices'][0]['message']['content'])['claims']
        assert claims == row['claims']
        assert all(set(c['citation_ids']) <= {'e1','e2'} for c in claims)
        prompt += row['prompt_tokens']; completion += row['completion_tokens']
    assert (prompt, completion) == (1257,450)
    assert not report['quality_gain_established']
    assert not report['application_dispatch_tested']
    edition = source_edition_case()
    return bundle, {'historical_provider_responses':6,
                    'historical_prompt_tokens':prompt,'historical_completion_tokens':completion,
                    'general_quality_gain_established':False,'new_model_calls':0,
                    'source_edition_statements':edition['proof']['receipt']['selected_statements'],
                    'source_edition_sources':edition['proof']['receipt']['source_records'],
                    'source_edition_context_bytes':edition['proof']['receipt']['context_bytes'],
                    'probe_manifest_sha256':hashlib.sha256((probe/'manifest.json').read_bytes()).hexdigest()}


def main():
    bundle, observation = replay()
    for name in ('graph.json','capsule.json','receipt.json','app-bundle.json'):
        (ROOT/'demo'/name).write_text(json.dumps(bundle[name],ensure_ascii=False,indent=2)+'\n')
    (ROOT/'observations.json').write_text(json.dumps(observation,indent=2)+'\n')
    (ROOT/'source-edition-case.json').write_text(json.dumps(source_edition_case(),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'demo_nodes':len(bundle['graph.json']['nodes']),
                      'demo_edges':len(bundle['graph.json']['edges']),
                      'capsule_bytes':bundle['receipt.json']['context_bytes'],
                      'retained_statements':len(bundle['capsule.json']['statements']),
                      **observation},indent=2))


if __name__ == '__main__':
    main()
