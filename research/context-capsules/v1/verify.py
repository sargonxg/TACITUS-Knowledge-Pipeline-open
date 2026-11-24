#!/usr/bin/env python3
"""Verify proposal identity, references, context replay and publication artifacts."""
from pathlib import Path, PurePosixPath
from html.parser import HTMLParser
import hashlib
import json
import re
from replay import replay

ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'manifest.json').read_text())
assert manifest['publication']=='TAC-2026-01' and manifest['newInferenceCalls']==0
for name,item in manifest['files'].items():
    assert not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
    data=(ROOT/name).read_bytes();assert len(data)==item['bytes'],name
    assert hashlib.sha256(data).hexdigest()==item['sha256'],name
for name,expected in manifest['referenceInputs'].items():
    data=(ROOT.parents[2]/'reference-pipeline'/name).read_bytes()
    assert hashlib.sha256(data).hexdigest()==expected,name
bundle,observation=replay();assert observation['new_model_calls']==0
assert json.loads((ROOT/'demo/capsule.json').read_text())==bundle['capsule.json']
assert json.loads((ROOT/'demo/app-bundle.json').read_text())==bundle['app-bundle.json']
refs=json.loads((ROOT/'references.json').read_text())
assert len(refs)==len({r['id'] for r in refs})==18
protocol=json.loads((ROOT/'evaluation-protocol.json').read_text())
assert protocol['status']=='proposed_not_registered_not_executed' and protocol['results']==[]
assert not protocol['quality_improvement_established']
assert (ROOT/'tacitus-context-capsules-v1.0.pdf').read_bytes().startswith(b'%PDF-')


class Reader(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.fragments=[];self.h1=0;self.tables=0;self.captions=0;self.math=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and a.get('href','').startswith('#'):self.fragments.append(a['href'][1:])
        if tag=='h1':self.h1+=1
        if tag=='table':self.tables+=1
        if tag=='caption':self.captions+=1
        if tag=='math' and a.get('display')=='block':self.math+=1


page=(ROOT/'index.html').read_text();r=Reader();r.feed(page)
assert len(r.ids)==len(set(r.ids))
assert set(r.fragments)<=set(r.ids)
assert r.h1==1 and r.tables==r.captions==4 and r.math==4
assert all('ref-'+v['id'] in r.ids for v in refs)
assert not re.search(r'<script\b|\son\w+=|\sstyle=',page)
assert 'Confirmatory experiments have not been run' in page
assert 'not independently peer-reviewed' in (ROOT/'citation.bib').read_text().lower()
assert manifest['privateAppSourceReviewCommit']=='2f11863ed506502a2bc508840a8e4d30ff69f15f'
print(f"Verified {len(manifest['files'])} artifact hashes, 18 references, 4 tables, 4 equations, synthetic context and six prior provider records; zero new model calls.")
