import copy,json,tempfile,threading,unittest
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from tacitus_pipeline.core import build,load_collection,digest,PipelineError
from tacitus_pipeline.generation import prepare,check_artifact,complete,invoke,output_object
ROOT=Path(__file__).resolve().parents[1]
def fixture():
 p=ROOT/'examples/syria-negotiation';return build(load_collection(p/'collection.json'),json.loads((ROOT/'ontology/negotiation.json').read_text()),json.loads((ROOT/'layers/syria-negotiation.json').read_text()),question='Prepare a historical negotiation brief.')
def artifact():return {'title':'Review note','items':[{'text':'Historical requested or supported processes; implementation not established.','evidence_ids':['convene-talks','governance-process','ceasefire-link']}],'questions':['What happened later?'],'limitations':['Not a current situation assessment.']}
class GenerationTests(unittest.TestCase):
 def test_qualified_evidence_attached_without_model_rewriting(self):
  b=fixture();a=check_artifact(b,artifact());self.assertEqual(a['items'][0]['evidence'][0]['quote'],next(s['quote'] for s in b['capsule.json']['statements'] if s['id']=='convene-talks'));self.assertEqual(a['review_state'],'draft_for_human_review');self.assertEqual(a['checks']['semantic_entailment'],'not_automatically_verified')
 def test_unknown_omitted_or_duplicate_citation_refuses(self):
  for ids in [['fake'],['convene-talks','convene-talks'],[]]:
   a=artifact();a['items'][0]['evidence_ids']=ids
   with self.assertRaises(PipelineError):check_artifact(fixture(),a)
 def test_required_coverage_refuses(self):
  a=artifact();a['items'][0]['evidence_ids']=['convene-talks']
  with self.assertRaises(PipelineError):check_artifact(fixture(),a)
 def test_cannot_add_approval_or_action(self):
  for k in ['approved','tools','publish']:
   a=artifact();a[k]=True
   with self.assertRaises(PipelineError):check_artifact(fixture(),a)
 def test_empty_limits_and_unbounded_content_refuse(self):
  for field,value in [('limitations',[]),('questions',[]),('title','x'*201),('items',[])]:
   a=artifact();a[field]=value
   with self.assertRaises(PipelineError):check_artifact(fixture(),a)
 def test_provider_truncation_toolcall_and_non_json_refuse(self):
  for r in [{'choices':[{'finish_reason':'length','message':{'content':'{}'}}]},{'response':'bad'},{'tool_calls':[{'name':'publish'}],'response':artifact()},{'success':False},[],{'result':[]}]:
   with self.assertRaises(PipelineError):output_object(r)
 def test_cloudflare_and_openai_response_shapes(self):
  self.assertEqual(output_object({'result':{'response':artifact()}}),artifact());self.assertEqual(output_object({'choices':[{'finish_reason':'stop','message':{'content':json.dumps(artifact())}}]}),artifact())
 def test_flat_and_structured_requests_use_same_exact_evidence(self):
  b=fixture();s=prepare(b);f=prepare(b,'flat');self.assertEqual(s['messages'][0],f['messages'][0]);self.assertEqual(s['max_tokens'],f['max_tokens']);self.assertEqual(s['temperature'],f['temperature']);a=json.loads(s['messages'][1]['content']);z=json.loads(f['messages'][1]['content']);self.assertEqual({r['quote'] for r in a['statements']},{r['text'] for r in z['passages']})
 def test_invalid_remote_http_and_embedded_credentials_refuse(self):
  for u in ['http://example.org/v1/chat/completions','https://name:secret@example.org/api','https://example.org/api?key=secret','file:///tmp/model','https://example.org/#key']:
   with self.assertRaises(PipelineError):invoke(prepare(fixture()),provider='openai-compatible',model='test',endpoint=u)
 def test_direct_provider_http_calls_and_usage(self):
  class Handler(BaseHTTPRequestHandler):
   def do_POST(s):
    body=json.loads(s.rfile.read(int(s.headers['Content-Length'])));self.assertEqual(body['model'],'test-model');payload=json.dumps({'choices':[{'finish_reason':'stop','message':{'content':json.dumps(artifact())}}],'usage':{'prompt_tokens':10,'completion_tokens':20}}).encode();s.send_response(200);s.end_headers();s.wfile.write(payload)
   def log_message(*a):pass
  server=HTTPServer(('127.0.0.1',0),Handler);t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
  try:
   b=fixture();raw,receipt=invoke(prepare(b),provider='ollama',model='test-model',endpoint='http://127.0.0.1:'+str(server.server_port)+'/v1/chat/completions');r=complete(b,raw,receipt);self.assertEqual(r['run']['usage']['prompt_tokens'],10);self.assertEqual(r['run']['model_calls'],1);self.assertFalse(r['run']['answer_quality_gain_established'])
  finally:server.shutdown();server.server_close()
 def test_output_conflict_refuses_before_any_provider_call(self):
  from unittest.mock import patch
  from tacitus_pipeline.workflow import main
  with tempfile.TemporaryDirectory() as d:
   (Path(d)/'keep.txt').write_text('keep')
   with patch('sys.argv',['workflow','generate','--bundle',str(ROOT/'examples/syria-negotiation/compiled'),'--output',d,'--provider','cloudflare','--model','test']),patch('tacitus_pipeline.workflow.invoke') as call:
    with self.assertRaises(SystemExit):main()
    call.assert_not_called()
 def test_live_recordings_have_expected_checksums_and_resolve(self):
  p=ROOT/'examples/syria-negotiation'
  for arm in ['flat','structured']:
   record=json.loads((p/(arm+'-recording.json')).read_text());req=json.loads((p/(arm+'-request/request.json')).read_text());self.assertEqual(record['receipt']['request_sha256'],digest(req));r=complete(fixture(),record['response'],record['receipt'],arm);self.assertEqual(r['artifact']['review_state'],'draft_for_human_review')
if __name__=='__main__':unittest.main()
