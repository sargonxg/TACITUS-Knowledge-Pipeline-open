#!/usr/bin/env python3
"""Verify a publication snapshot without rebuilding its PDF or calling models."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re
import subprocess

root = Path(__file__).resolve().parent
manifest = json.loads((root/'manifest.json').read_text())
for name, item in manifest['files'].items():
    data = (root/name).read_bytes()
    assert len(data) == item['bytes'], name
    assert hashlib.sha256(data).hexdigest() == item['sha256'], name
benchmark = root.parents[1]/'wind-tunnel-us/v1/benchmark.json'
assert hashlib.sha256(benchmark.read_bytes()).hexdigest() == manifest['benchmarkSha256']
subprocess.run(['node', str(benchmark.parent/'score.mjs'), 'verify', str(benchmark)], check=True, capture_output=True)
refs = json.loads((root/'references.json').read_text())
assert len(refs) == 14 and len({r['id'] for r in refs}) == 14
assert (root/'wind-tunnel-methodology-v1.0.pdf').read_bytes().startswith(b'%PDF-')
paper = json.loads((root/'paper.json').read_text())
assert paper['version'] == manifest['version'] == '1.0'
assert 'not independently peer-reviewed' in (root/'citation.bib').read_text().lower()


class Reader(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.fragments=[];self.headings=[];self.tables=0;self.captions=0;self.math=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and a.get('href','').startswith('#'):self.fragments.append(a['href'][1:])
        if re.fullmatch('h[1-6]',tag):self.headings.append(tag)
        if tag=='table':self.tables+=1
        if tag=='caption':self.captions+=1
        if tag=='math' and a.get('display')=='block':self.math+=1


html=(root/'index.html').read_text();reader=Reader();reader.feed(html)
assert len(reader.ids) == len(set(reader.ids)), 'Duplicate document anchors'
assert set(reader.fragments) <= set(reader.ids), 'Unresolved internal citation or section link'
assert reader.headings.count('h1')==1, 'The reading page should have one document title'
assert reader.tables == reader.captions == 3
assert reader.math == 3
assert not re.search(r'<script\b|\son\w+=|\sstyle=', html), 'Publication must work with the company CSP'
assert all('ref-'+r['id'] in reader.ids for r in refs)
assert '<!-- RESULTS_TABLE -->' not in paper['articleHtml']
print(f"Verified {len(manifest['files'])} artifact hashes, 14 references, all internal links, 3 tables and 3 equations.")
