"""Source-pinned diplomatic wording review. Literal checks, not semantic approval."""
from __future__ import annotations
import argparse,copy,json,re
from pathlib import Path
from .core import PipelineError,build,canonical,digest,load_collection,unique,write_bundle

BOUNDARY='Literal retention checks do not establish entailment, legal effect, current applicability or expert approval. Hashes establish local consistency, not author authentication or an immutable external history.'
def require(value,message):
 if not value:raise PipelineError(message)
def wording_checks(capsule,choices,draft):
 statements={s['id']:s for s in capsule['statements']};checks=[]
 for sid in draft['evidence_ids']:
  s=statements[sid]
  for i,q in enumerate(s['qualifiers']):checks.append({'id':f'{sid}:qualification:{i}','kind':'qualification','statement_id':sid,'source_version':s['source_version'],'literal':q['text'],'present':q['text'].lower() in draft['text'].lower()})
 for c in choices:
  if c['statement_id'] in draft['evidence_ids']:checks.append({'id':c['id'],'kind':'declared_wording','statement_id':c['statement_id'],'source_version':statements[c['statement_id']]['source_version'],'literal':c['literal'],'present':c['literal'].lower() in draft['text'].lower()})
 return checks

def review_graph(base,history):
 graph=copy.deepcopy(base)
 def node(id,kind,label):graph['nodes'].append({'id':id,'kind':kind,'label':label})
 def edge(a,b,relation):graph['edges'].append({'id':f'language:{len(graph["edges"])}','source':a,'target':b,'relation':relation})
 for c in history['choices']:
  node('choice:'+c['id'],'LanguageChoice',c['literal']);edge('choice:'+c['id'],'statement:'+c['statement_id'],'quotesWording')
 for d in history['drafts']:
  node('draft:'+d['id'],'DraftVersion',d['text'])
  for sid in d['evidence_ids']:edge('draft:'+d['id'],'statement:'+sid,'cites')
  for c in history['choices']:
   if c['statement_id'] in d['evidence_ids']:edge('draft:'+d['id'],'choice:'+c['id'],'checkedAgainst')
  if d['parent']:edge('draft:'+d['id'],'draft:'+d['parent'],'revises')
 for e in history['events']:
  node('event:'+e['id'],{'proposal':'Proposal','discussion':'Discussion','review':'Review'}[e['kind']],e['note']);edge('event:'+e['id'],'draft:'+e['draft_id'],'discusses' if e['kind']=='discussion' else e['kind'])
  if e.get('choice_id'):edge('event:'+e['id'],'choice:'+e['choice_id'],'concernsWording')
  for sid in e['evidence_ids']:edge('event:'+e['id'],'statement:'+sid,'cites')
 return graph

def assemble(collection,ontology,layer,history):
 require(isinstance(history,dict) and history.get('format')=='tacitus-language-history/1','Unsupported language-history format.')
 require(history.get('scope')=='synthetic_editorial_exercise','The bundled history must be explicitly synthetic.')
 bundle=build(collection,ontology,layer,question='Inspect historical support language, conditions and proposed draft revisions.',budget=24000)
 c=bundle['capsule.json'];statements=unique(c['statements'],'statements');h=copy.deepcopy(history)
 for k,limit in [('choices',50),('drafts',100),('events',400)]:require(isinstance(h.get(k),list) and 0<len(h[k])<=limit,'Missing or oversized '+k)
 choices=unique(h['choices'],'wording choices');drafts=unique(h['drafts'],'drafts');unique(h['events'],'events')
 for choice in choices.values():
  require(choice.get('statement_id') in statements and isinstance(choice.get('literal'),str) and choice['literal'] and choice['literal'] in statements[choice['statement_id']]['quote'],'Declared wording must be exact source text.')
  require(isinstance(choice.get('rationale'),str) and 0<len(choice['rationale'])<=4000,'A wording choice needs an authored review rationale.')
 seen=set()
 for d in h['drafts']:
  require(set(d)=={'id','parent','text','evidence_ids'},'Draft fields must be explicit; approval fields are unsupported.')
  require(d['parent'] is None or d['parent'] in seen,'Draft parents must precede revisions.')
  require(isinstance(d['text'],str) and 0<len(d['text'])<=10000,'Invalid draft wording.')
  require(isinstance(d['evidence_ids'],list) and 0<len(d['evidence_ids'])<=20 and len(set(d['evidence_ids']))==len(d['evidence_ids']) and all(s in statements for s in d['evidence_ids']),'Draft citations must resolve uniquely.')
  d['sha256']=digest(d);seen.add(d['id'])
 head=None;proposed=set()
 for i,e in enumerate(h['events']):
  require(set(e)<= {'id','kind','draft_id','note','evidence_ids','choice_id'} and e.get('kind') in ['proposal','discussion','review'],'Only proposals, discussions and pending review records are supported.')
  require(e.get('draft_id') in drafts and isinstance(e.get('note'),str) and 0<len(e['note'])<=4000,'Event needs a draft and bounded note.')
  require(isinstance(e.get('evidence_ids'),list) and 0<len(e['evidence_ids'])<=20 and len(set(e['evidence_ids']))==len(e['evidence_ids']) and all(s in drafts[e['draft_id']]['evidence_ids'] for s in e['evidence_ids']),'Event evidence must belong to its draft.')
  require(not e.get('choice_id') or e['choice_id'] in choices and choices[e['choice_id']]['statement_id'] in e['evidence_ids'],'Discussion wording must resolve to its evidence.')
  if e['kind']=='proposal':
   require(e['draft_id'] not in proposed and (not drafts[e['draft_id']]['parent'] or drafts[e['draft_id']]['parent'] in proposed),'Proposals must preserve revision order.')
   proposed.add(e['draft_id'])
  else:require(e['draft_id'] in proposed,'Discussion must follow a proposal.')
  e.update(sequence=i,previous_sha256=head,actor='synthetic editorial exercise',review_state='pending');e['sha256']=digest(e);head=e['sha256']
 require(proposed==set(drafts),'Every draft needs a proposal record.')
 snapshots=[{'id':s['id'],'text':s['text'],'sha256':s['version'],'url':s['url'],'rights_note':s['rights_note']} for s in collection['sources'] if any(s['id'] in x['aliases'] for x in c['sources'])]
 return {'format':'tacitus-language-review/1','capsule':c,'context_sha256':digest(c),'source_snapshots':snapshots,'base_graph':bundle['graph.json'],'history':h,'ledger_head':head,'checks':{d['id']:wording_checks(c,h['choices'],d) for d in h['drafts']},'graph':review_graph(bundle['graph.json'],h),'model_calls':0,'review_state':'pending','boundary':BOUNDARY}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['input','ontology','layer','history','output']:p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--force',action='store_true');a=p.parse_args()
 try:
  result=assemble(load_collection(a.input),json.loads(a.ontology.read_text()),json.loads(a.layer.read_text()),json.loads(a.history.read_text()))
  write_bundle({'language-review.json':result,'language-graph.json':result['graph']},a.output,force=a.force)
 except (PipelineError,OSError,ValueError,KeyError,TypeError) as e:p.exit(2,f'Language review refused: {e}\n')
 print(json.dumps({'draft_versions':len(result['history']['drafts']),'history_events':len(result['history']['events']),'model_calls':0,'review_state':'pending'}))
if __name__=='__main__':main()
