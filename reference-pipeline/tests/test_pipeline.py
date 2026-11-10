import copy
import json
import tempfile
import unittest
from pathlib import Path
from tacitus_pipeline.core import PipelineError, build, canonical, digest, load_collection, write_bundle
ROOT = Path(__file__).resolve().parents[1]

def fixture():
    return (load_collection(ROOT/'examples/assessment/collection.json'), json.loads((ROOT/'ontology/policy.json').read_text()), json.loads((ROOT/'layers/assessment-evidence.json').read_text()))

def run(data=None, ontology=None, layer=None, budget=24500):
    a,b,c=fixture()
    return build(data or a, ontology or b, layer or c, question='Map evidence reuse and review roles.', budget=budget)

class PipelineTests(unittest.TestCase):
    def test_real_source_example_retains_conditions_and_roles(self):
        r=run();self.assertEqual(r['receipt.json']['selected_statements'],3);self.assertEqual(r['receipt.json']['source_records'],2)
        self.assertIn('where designated',canonical(r['capsule.json']));self.assertIn('If any of the obligations',r['brief.md']);self.assertEqual(r['workflow.json']['model_calls'],0)
        packet=r['capsule.json'];ids={e['id'] for e in packet['entities']};self.assertTrue(all(s['subject'] in ids and s['object'] in ids and s['relation'] in packet['relations'] for s in packet['statements']))
    def test_source_tampering_refuses(self):
        a,_,_=fixture();a['sources'][0]['text']+='changed'
        with self.assertRaises(PipelineError):run(data=a)
    def test_rehashing_source_does_not_fix_stale_statement(self):
        a,_,_=fixture();a['sources'][0]['text']+='changed';a['sources'][0]['version']=digest(a['sources'][0]['text'])
        with self.assertRaises(PipelineError):run(data=a)
    def test_quote_and_span_tampering_refuse(self):
        for key,value in [('quote','invented'),('start',-1),('end',999999)]:
            a,_,_=fixture();a['statements'][0][key]=value
            with self.assertRaises(PipelineError):run(data=a)
    def test_lost_qualification_refuses(self):
        a,_,_=fixture();a['statements'][0]['qualifiers']=[]
        with self.assertRaises(PipelineError):run(data=a)
    def test_domain_range_and_dangling_entity_refuse(self):
        for key,value in [('relation','unsupported'),('object','missing'),('subject','dpo')]:
            a,_,_=fixture();a['statements'][0][key]=value
            with self.assertRaises(PipelineError):run(data=a)
    def test_cannot_self_promote_review(self):
        a,_,_=fixture();a['statements'][0]['review_state']='accepted'
        with self.assertRaises(PipelineError):run(data=a)
    def test_required_evidence_is_never_cut(self):
        with self.assertRaises(PipelineError):run(budget=2000)
        r=run(budget=4500);self.assertLessEqual(r['receipt.json']['context_bytes'],4500);self.assertEqual(r['receipt.json']['omitted_statements'],1);self.assertEqual(len(r['capsule.json']['statements']),2)
    def test_canonical_result_independent_of_input_order(self):
        a,_,_=fixture();a['sources'].reverse();a['entities'].reverse();a['statements'].reverse();self.assertEqual(run()['receipt.json']['context_sha256'],run(data=a)['receipt.json']['context_sha256'])
    def test_duplicate_source_edition_coalesces_without_deleting_interpretations(self):
        a,_,c=fixture();s=copy.deepcopy(a['sources'][0]);s['id']='same-edition';a['sources'].append(s);stmt=copy.deepcopy(a['statements'][0]);stmt['id']='second-interpretation';stmt['source_id']=s['id'];a['statements'].append(stmt);c['statement_ids'].append(stmt['id']);r=run(data=a,layer=c);self.assertEqual(r['receipt.json']['source_records'],2);self.assertEqual(len(r['capsule.json']['statements']),4)
    def test_graph_endpoints_and_jsonld_objects_resolve(self):
        r=run();ids={n['id'] for n in r['graph.json']['nodes']};self.assertTrue(all(e['source'] in ids and e['target'] in ids for e in r['graph.json']['edges']));self.assertEqual(len(ids),len(r['graph.jsonld']['@graph']));self.assertTrue(any(n['kind']=='Qualification' for n in r['graph.json']['nodes']))
    def test_path_escape_refuses_and_refusal_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text(json.dumps({'sources':[{'file':'../outside.txt'}]}))
            with self.assertRaises(PipelineError):load_collection(p)
            out=Path(d)/'output';self.assertFalse(out.exists())
    def test_outputs_require_explicit_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            write_bundle(run(),d)
            with self.assertRaises(PipelineError):write_bundle(run(),d)
            write_bundle(run(),d,force=True)
    def test_unicode_codepoints_and_exact_bytes(self):
        a,b,c=fixture();s=a['sources'][1];s['text']='😀 '+s['text'];s['version']=digest(s['text'])
        for r in a['statements']:
            if r['source_id']==s['id']:r['start']+=2;r['end']+=2;r['source_version']=s['version']
        self.assertIn('where designated',canonical(run(data=a)['capsule.json']))
    def test_unresolved_layer_and_duplicate_ids_refuse(self):
        a,_,c=fixture();a['entities'].append(a['entities'][0])
        with self.assertRaises(PipelineError):run(data=a)
        c['statement_ids'].append('missing')
        with self.assertRaises(PipelineError):run(layer=c)

if __name__=='__main__':unittest.main()
