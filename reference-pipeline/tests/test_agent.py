import json,unittest
from pathlib import Path
from tacitus_pipeline.agent import start,request,advance
from tacitus_pipeline.core import PipelineError,digest
from tacitus_pipeline.workflow import load_bundle
ROOT=Path(__file__).resolve().parents[1]
def bundle():return load_bundle(ROOT/'examples/syria-negotiation/compiled')
def reply(state,action):return {'response':action},{'request_sha256':digest(request(state)),'provider':'test','model_requested':'fixture'}
class AgentTests(unittest.TestCase):
 def test_draft_requires_actual_evidence_tool_step(self):
  b=bundle();s=start(b);a=json.loads((ROOT/'examples/syria-negotiation/structured-recording.json').read_text())['response']['result']['response'];raw,r=reply(s,{'action':'draft','artifact':a})
  with self.assertRaises(PipelineError):advance(b,s,raw,r)
 def test_unknown_tool_and_arbitrary_url_refuse(self):
  for action in [{'action':'browse','url':'https://example.org'},{'action':'publish'},{'action':'inspect_evidence','statement_ids':['not-selected']}]:
   b=bundle();s=start(b);raw,r=reply(s,action)
   with self.assertRaises(PipelineError):advance(b,s,raw,r)
 def test_response_binding_and_context_tampering_refuse(self):
  b=bundle();s=start(b);raw,r=reply(s,{'action':'inspect_evidence','statement_ids':['convene-talks']});r['request_sha256']='0'*64
  with self.assertRaises(PipelineError):advance(b,s,raw,r)
  r['request_sha256']=digest(request(s));b['capsule.json']['question']='changed'
  with self.assertRaises(PipelineError):advance(b,s,raw,r)
 def test_finite_step_budget_never_executes_unbounded_loop(self):
  b=bundle();s=start(b,max_steps=2);a={'action':'inspect_evidence','statement_ids':['convene-talks']};s,_=advance(b,s,*reply(s,a))
  with self.assertRaises(PipelineError):advance(b,s,*reply(s,a))
 def test_live_agent_recordings_replay_to_review_not_approval(self):
  b=bundle();s=start(b);result=None
  for i in [0,1]:
   r=json.loads((ROOT/f'examples/syria-negotiation/agent-recording-{i}.json').read_text());s,result=advance(b,s,r['response'],r['receipt'])
  self.assertEqual(s['status'],'draft_for_human_review');self.assertEqual(result['run']['model_calls'],2);self.assertEqual(result['run']['usage']['total_tokens'],2427);self.assertEqual(len(s['inspected']),3)
 def test_failed_real_protocol_attempt_is_refused(self):
  p=ROOT/'examples/syria-negotiation/agent-refused-attempt';s=json.loads((p/'agent-state.json').read_text());r=json.loads((p/'provider-recording.json').read_text())
  with self.assertRaises(PipelineError):advance(bundle(),s,r['response'],r['receipt'])
if __name__=='__main__':unittest.main()
