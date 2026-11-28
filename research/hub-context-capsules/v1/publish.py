# /// script
# requires-python = ">=3.12"
# dependencies = ["huggingface_hub>=1.0,<2"]
# ///
"""Publish only owned public research; retain immutable assets and source history."""
from pathlib import Path
import argparse
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download
from huggingface_hub.errors import RepositoryNotFoundError

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--publish",action="store_true",help="Explicitly publish the reviewed public dataset and Space entry pages")
parser.add_argument("--spaces-only",action="store_true",help="Skip dataset creation when resuming an inspected partial publication")
args=parser.parse_args()
if not args.publish:parser.error("Publishing is opt-in: use --publish only after reviewing the release and account")

api=HfApi()
assert api.whoami()['name']=='Giuliocc','Unexpected publishing account'
source='9428e93ce812a70494874da615f848b919e4700d'
dataset='Giuliocc/tacitus-context-capsules'
if not args.spaces_only:
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary)
        archive=urllib.request.urlopen('https://api.github.com/repos/sargonxg/TACITUS-Knowledge-Pipeline-open/tarball/'+source,timeout=45).read()
        with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as tar:tar.extractall(root/'source',filter='data')
        repo=next((root/'source').iterdir())
        bundle=root/'context-release'
        subprocess.run([sys.executable,str(repo/'research/hub-context-capsules/v1/build.py'),'--output',str(bundle)],check=True)
        subprocess.run([sys.executable,str(bundle/'verify.py')],check=True)
        try:
            api.repo_info(dataset,repo_type='dataset')
        except RepositoryNotFoundError:
            api.create_repo(dataset,repo_type='dataset',private=False)
        else:
            raise RuntimeError('The dataset already exists; review it instead of overwriting another release')
        baseline=api.repo_info(dataset,repo_type='dataset').sha
        commit=api.upload_folder(repo_id=dataset,repo_type='dataset',folder_path=bundle,parent_commit=baseline,commit_message='Publish source-pinned TACITUS context capsules v0.1.0')
        api.create_tag(dataset,repo_type='dataset',tag='v0.1.0',revision=commit.oid)
        print(json.dumps({'dataset':dataset,'commit':commit.oid,'source':source,'counts':json.loads((bundle/'release.json').read_text())['counts']}),flush=True)

products=[
    ('Giuliocc/doxa-lab','DOXA','Review language and evidence with the source passages close to each finding.','https://doxa.tacitus.me/','https://github.com/sargonxg/DOXA-by-TACITUS','https://huggingface.co/Giuliocc/doxa-wording-encoder','doxa-analyst.v1.webp'),
    ('Giuliocc/doxa-scorecard','DOXA Evidence','Inspect the evidence model, its benchmark and the limits of a screening result.','https://doxa.tacitus.me/scorecard/','https://github.com/sargonxg/DOXA-by-TACITUS','https://huggingface.co/Giuliocc/doxa-evidence-verifier','doxa-analyst.v1.webp'),
    ('Giuliocc/windtunnel-lab','Wind Tunnel','Explore source-backed audience research and design the human fieldwork needed to test a question.','https://windtunnel.tacitus.me/','https://github.com/sargonxg/A2_WINDTUNNEL_CLOUD','https://huggingface.co/Giuliocc/windtunnel-response-cross-wave','wind-tunnel-kite.v1.webp'),
]
for identity,title,description,app,github,model,art in products:
    info=api.repo_info(identity,repo_type='space')
    assert info.card_data and info.card_data.get('sdk')=='static'
    files=api.list_repo_files(identity,repo_type='space',revision=info.sha)
    card=Path(hf_hub_download(identity,'README.md',repo_type='space',revision=info.sha)).read_text()
    match=re.match(r'\A---\s*\n(.*?)\n---',card,re.S)
    assert match,'Space front matter missing'
    yaml=match.group(1)
    yaml=re.sub(r'^app_file:.*$','app_file: index.html',yaml,flags=re.M) if re.search(r'^app_file:',yaml,re.M) else yaml+'\napp_file: index.html'
    card=card[:match.start(1)]+yaml+card[match.end(1):]
    notice='\n\n<!-- tacitus-hosted-product-boundary:start -->\n## Product access\n\n[Sign in to '+title+']('+app+'). This Space presents public research. The hosted workspace requires authentication on the product domain. Models, datasets, methods and frozen source assets remain available for inspection and reproducibility. The code and historical documentation below describe research releases; they do not imply model correctness or human approval.\n<!-- tacitus-hosted-product-boundary:end -->\n'
    card=re.sub(r'\n*<!-- tacitus-hosted-product-boundary:start -->.*?<!-- tacitus-hosted-product-boundary:end -->\n?',notice,card,flags=re.S) if '<!-- tacitus-hosted-product-boundary:start -->' in card else card+notice
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+title+''' · TACITUS research</title><style>:root{font:16px/1.65 system-ui,sans-serif;background:#f7f8f6;color:#173a2f}body{margin:0}main{max-width:760px;margin:6vh auto;padding:28px}header{display:flex;align-items:center;gap:24px}img{width:76px;height:96px;object-fit:contain;image-rendering:pixelated}h1,h2,small{font-family:ui-monospace,monospace}h1{font-size:clamp(2.2rem,8vw,4rem);line-height:1.05;margin:.2em 0}p{max-width:64ch}nav{display:flex;flex-wrap:wrap;gap:12px;margin:28px 0}a{color:#174d3c;text-underline-offset:4px}.button{background:#174d3c;color:white;padding:12px 20px;text-decoration:none;border:1px solid #174d3c}section{border-top:1px solid #baccc0;margin-top:35px;padding-top:15px}.links{display:flex;gap:20px;flex-wrap:wrap}small{letter-spacing:.08em}a:focus-visible{outline:3px solid #b47b1e;outline-offset:4px}</style><main data-tacitus-research-entry="1"><header><img src="https://tacitus.me/assets/brand/'''+art+'''" alt=""><div><small>TACITUS · EXPERIMENTAL RESEARCH</small><h1>'''+title+'''</h1></div></header><p>'''+description+'''</p><nav><a class="button" href="'''+app+'''" target="_top">Sign in to the workspace ↗</a><a href="https://tacitus.me/product/" target="_top">About the products</a></nav><section><h2>Inspect the research.</h2><p>Code, model cards, evaluation data and historical source snapshots remain public. Use the authenticated product for document review, saved work and research tools.</p><div class="links"><a href="'''+github+'''" target="_top">GitHub ↗</a><a href="'''+model+'''" target="_top">Hugging Face model ↗</a><a href="https://huggingface.co/'''+identity+'''/tree/main" target="_top">Research files ↗</a></div></section><section><h2>Read the limits with the result.</h2><p>These are experimental research tools. Published evaluation results are specific to their datasets and tasks. A graph, model score or generated answer does not establish factual correctness, political neutrality or reliable forecasts. Keep source versions, uncertainty and human judgment visible.</p></section></main></html>'''
    operations=[CommitOperationAdd(path_in_repo='README.md',path_or_fileobj=card.encode()),CommitOperationAdd(path_in_repo='index.html',path_or_fileobj=html.encode())]
    if 'dist/index.html' in files:operations.append(CommitOperationAdd(path_in_repo='dist/index.html',path_or_fileobj=html.encode()))
    commit=api.create_commit(identity,repo_type='space',operations=operations,parent_commit=info.sha,commit_message='Present research publicly; route working tools to the authenticated TACITUS product')
    print(json.dumps({'space':identity,'previous':info.sha,'commit':commit.oid,'app':app,'retainedResearchAssets':True}),flush=True)
