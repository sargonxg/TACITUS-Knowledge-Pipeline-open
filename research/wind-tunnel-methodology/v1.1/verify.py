#!/usr/bin/env python3
"""Verify the versioned publication offline, without a PDF rebuild or inference."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re
import subprocess

root = Path(__file__).resolve().parent
canonical = 'https://tacitus.me/research/wind-tunnel/paper/v1.1/'
manifest = json.loads((root/'manifest.json').read_text())
for name, item in manifest['files'].items():
    data = (root/name).read_bytes()
    assert len(data) == item['bytes'], name
    assert hashlib.sha256(data).hexdigest() == item['sha256'], name
benchmark = root.parents[1]/'wind-tunnel-us/v1/benchmark.json'
assert hashlib.sha256(benchmark.read_bytes()).hexdigest() == manifest['benchmarkSha256']
assert manifest['benchmarkSourceCommit'] == '2b51dfee375b1ee0e5fd1ee7a99edd1623d8cac4'
assert manifest['canonical'] == canonical
subprocess.run(['node', str(benchmark.parent/'score.mjs'), 'verify', str(benchmark)], check=True, capture_output=True)
assert json.loads((root/'results.json').read_text()) == json.loads((root.parent/'v1/results.json').read_text()), 'The publication revision must not change scores'
refs = json.loads((root/'references.json').read_text())
assert len(refs) == 14 and len({r['id'] for r in refs}) == 14
assert (root/'wind-tunnel-methodology-v1.1.pdf').read_bytes().startswith(b'%PDF-')
paper = json.loads((root/'paper.json').read_text())
assert paper['version'] == manifest['version'] == '1.1'
assert paper['date'] == manifest['date'] == '2026-11-24'
assert 'Research Preparation' in paper['title']
bib = (root/'citation.bib').read_text()
assert 'not independently peer-reviewed' in bib.lower()
assert 'version = {1.1}' in bib and canonical in bib
agenda = json.loads((root/'evaluation-agenda.json').read_text())
assert agenda['status'] == 'proposed_not_run' and agenda['newInferenceCalls'] == 0


class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[];self.fragments=[];self.headings=[];self.tables=0;self.captions=0;self.math=0;self.images=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and a.get('href','').startswith('#'):self.fragments.append(a['href'][1:])
        if re.fullmatch('h[1-6]',tag):self.headings.append(tag)
        if tag=='table':self.tables+=1
        if tag=='caption':self.captions+=1
        if tag=='math' and a.get('display')=='block':self.math+=1
        if tag=='img':self.images.append(a)


html=(root/'index.html').read_text();reader=Reader();reader.feed(html)
assert len(reader.ids) == len(set(reader.ids)), 'Duplicate document anchors'
assert set(reader.fragments) <= set(reader.ids), 'Unresolved internal citation or section link'
assert reader.headings.count('h1')==1, 'The reading page should have one document title'
assert reader.tables == reader.captions == 4
assert reader.math == 3
assert all('alt' in a for a in reader.images)
assert not re.search(r'<script\b|\son\w+=|\sstyle=', html), 'Publication must work with the company CSP'
assert f'<link rel="canonical" href="{canonical}">' in html
assert all('ref-'+r['id'] in reader.ids for r in refs)
assert '<!-- RESULTS_TABLE -->' not in paper['articleHtml']
assert '<!-- ITEMS_TABLE -->' not in paper['articleHtml']
assert 'citation_publication_date" content="2026/11/24"' in html
assert 'wind-tunnel-methodology-v1.0.pdf' not in html
assert '/research/wind-tunnel/paper/">Version 1.0 archive' in html
for image in reader.images:
    source = image['src']
    if '/paper/v1.1/' in source:
        assert (root/source.split('/paper/v1.1/',1)[1]).is_file(), source
print(f"Verified {len(manifest['files'])} artifact hashes, unchanged v1 scores, 14 references, internal links, 4 captioned tables and 3 MathML equations.")
