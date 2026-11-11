import copy,json,tempfile,unittest
from pathlib import Path
from tacitus_pipeline.core import PipelineError,load_collection
from tacitus_pipeline.language import assemble
R=Path(__file__).resolve().parents[1]
def fixture():
 return [load_collection(R/'examples/syria-negotiation/collection.json'),json.loads((R/'ontology/negotiation.json').read_text()),json.loads((R/'layers/syria-negotiation.json').read_text()),json.loads((R/'examples/syria-negotiation/language-history.json').read_text())]
class LanguageTests(unittest.TestCase):
 def test_real_source_and_synthetic_history_are_distinct(self):
  result=assemble(*fixture());self.assertEqual(result['history']['scope'],'synthetic_editorial_exercise');self.assertEqual(result['model_calls'],0);self.assertEqual(result['review_state'],'pending');self.assertEqual(sum(c['present'] for c in result['checks']['initial']),0);self.assertEqual(sum(c['present'] for c in result['checks']['qualified']),3);self.assertIn('not author authentication',result['boundary'])
 def test_reproducible_graph_links_discussion_to_wording_and_source(self):
  r=assemble(*fixture());self.assertEqual(r,assemble(*fixture()));ids={n['id'] for n in r['graph']['nodes']};self.assertTrue(all(e['source'] in ids and e['target'] in ids for e in r['graph']['edges']));self.assertTrue(any(e['relation']=='concernsWording' for e in r['graph']['edges']));self.assertEqual(r['history']['events'][1]['previous_sha256'],r['history']['events'][0]['sha256']);self.assertTrue(any(e['relation']=='revises' for e in r['graph']['edges']))
 def test_changed_source_refused(self):
  args=fixture();args[0]['sources'][0]['text']='Changed';self.assertRaises(PipelineError,assemble,*args)
 def test_unquoted_wording_refused(self):
  args=fixture();args[3]['choices'][0]['literal']='agreed to establish';self.assertRaises(PipelineError,assemble,*args)
 def test_unresolved_citation_refused(self):
  args=fixture();args[3]['drafts'][0]['evidence_ids']=['invented'];self.assertRaises(PipelineError,assemble,*args)
 def test_duplicate_ids_and_cycles_refused(self):
  for mutation in ['duplicate','cycle']:
   args=fixture()
   if mutation=='duplicate':args[3]['drafts'].append(copy.deepcopy(args[3]['drafts'][0]))
   else:args[3]['drafts'][0]['parent']='qualified'
   self.assertRaises(PipelineError,assemble,*args)
 def test_approval_cannot_be_smuggled_into_draft_or_event(self):
  for key in ['drafts','events']:
   args=fixture();args[3][key][0]['approved']=True;self.assertRaises(PipelineError,assemble,*args)
 def test_discussion_must_follow_proposal_and_cite_its_draft(self):
  args=fixture();args[3]['events'][0],args[3]['events'][1]=args[3]['events'][1],args[3]['events'][0];self.assertRaises(PipelineError,assemble,*args)
  args=fixture();args[3]['events'][1]['evidence_ids']=['convene-talks'];self.assertRaises(PipelineError,assemble,*args)
 def test_history_bounds_and_synthetic_label_required(self):
  for change in ['length','scope']:
   args=fixture()
   if change=='length':args[3]['events'][0]['note']='x'*4001
   else:args[3]['scope']='real_diplomatic_negotiation'
   self.assertRaises(PipelineError,assemble,*args)
