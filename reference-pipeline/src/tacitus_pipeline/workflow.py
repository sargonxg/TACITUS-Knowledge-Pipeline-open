"""Run with python -m tacitus_pipeline.workflow. Explicit generation; no silent fallback."""
import argparse,json
from pathlib import Path
from .core import PipelineError,digest,write_bundle
from .generation import prepare,invoke,complete,markdown

def load_bundle(path):
    root=Path(path);bundle={}
    for name in ['capsule.json','graph.json','workflow.json','receipt.json']:
        p=root/name
        if p.stat().st_size>2_000_000:raise PipelineError('Bundle file exceeds 2 MB.')
        bundle[name]=json.loads(p.read_text(encoding='utf-8'))
    if bundle['capsule.json'].get('format')!='tacitus-reference-context/1' or bundle['receipt.json'].get('context_sha256')!=digest(bundle['capsule.json']):raise PipelineError('Context checksum or format mismatch.')
    return bundle

def preflight_output(path,force=False):
    output=Path(path)
    if output.exists() and (not output.is_dir() or (any(output.iterdir()) and not force)):
        raise PipelineError('Output exists. Choose a new directory or explicitly use --force before making a model call.')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['prepare','generate','import']);parser.add_argument('--bundle',required=True);parser.add_argument('--arm',choices=['structured','flat'],default='structured');parser.add_argument('--output',required=True);parser.add_argument('--force',action='store_true');parser.add_argument('--provider',choices=['cloudflare','ollama','openai-compatible']);parser.add_argument('--model');parser.add_argument('--endpoint');parser.add_argument('--recording');args=parser.parse_args()
    try:
        preflight_output(args.output,args.force)
        bundle=load_bundle(args.bundle);request=prepare(bundle,args.arm)
        if args.command=='prepare':
            write_bundle({'request.json':request,'request-receipt.json':{'request_sha256':digest(request),'arm':args.arm,'model_calls':0}},args.output,force=args.force);print('Prepared provider request; no model call made.');return
        if args.command=='generate':
            if not args.provider or not args.model:raise PipelineError('Generation needs explicit --provider and --model.')
            raw,receipt=invoke(request,provider=args.provider,model=args.model,endpoint=args.endpoint)
        else:
            if not args.recording:raise PipelineError('Import needs --recording from an explicitly executed provider request.')
            p=Path(args.recording)
            if p.stat().st_size>2_000_000:raise PipelineError('Recording exceeds 2 MB.')
            record=json.loads(p.read_text());receipt=record['receipt'];raw=record['response']
            if receipt.get('request_sha256')!=digest(request):raise PipelineError('Recording does not match this exact prepared request.')
            receipt={**receipt,'import_validation':'Checksum binds supplied files; importer does not authenticate provider transport or token counts.'}
        result=complete(bundle,raw,receipt,args.arm)
        write_bundle({'workflow-result.json':result,'draft.md':markdown(result),'provider-response.json':raw},args.output,force=args.force);print(json.dumps({'status':result['artifact']['review_state'],'items':len(result['artifact']['items']),'model_calls':1,'semantic_entailment':'not_automatically_verified'}))
    except (PipelineError,OSError,KeyError,TypeError,ValueError) as e:parser.exit(2,'Refused: '+str(e)+'\n')
if __name__=='__main__':main()
