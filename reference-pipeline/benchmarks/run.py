"""Reproducible assembly measurements; never a model-quality score."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from tacitus_pipeline.core import build,load_collection,PipelineError

def run():
 data=load_collection(ROOT/'examples/assessment/collection.json');ontology=json.loads((ROOT/'ontology/policy.json').read_text());layer=json.loads((ROOT/'layers/assessment-evidence.json').read_text());rows=[]
 for budget in [2000,4500,5500,24500]:
  try:r=build(data,ontology,layer,question='Map assessment evidence and review roles.',budget=budget);rows.append({'budget_bytes':budget,'status':'prepared',**r['receipt.json']})
  except PipelineError as e:rows.append({'budget_bytes':budget,'status':'refused','reason':str(e)})
 report={'format':'tacitus-assembly-benchmark/1','fixture':'Two original adopted-law passages, three authored mappings; no current legal assessment.','scope':'Complete evidence, byte limits, source editions and refusal behavior. Not model quality, token savings, latency or analyst-time measurement.','model_calls':0,'model_answer_evaluation':'work_in_progress_not_run','results':rows};return report
if __name__=='__main__':print(json.dumps(run(),indent=2))
