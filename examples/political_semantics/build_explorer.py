#!/usr/bin/env python3
"""Build one offline HTML evidence explorer from the validated teaching corpus."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path

from semantic_layer import export_jsonld, export_sql, load

HERE = Path(__file__).resolve().parent


def script_json(value: object) -> str:
    """Prevent source text from closing its inert HTML script container."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def csp_hash(text: str) -> str:
    return "sha256-" + base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()


def build(destination: Path, corpus: Path = HERE / "corpus.json") -> Path:
    data = load(corpus)
    styles = (HERE / "explorer.css").read_text(encoding="utf-8")
    javascript = (HERE / "explorer.js").read_text(encoding="utf-8")
    payload = script_json({"corpus": data, "jsonld": export_jsonld(data), "sql": export_sql(data)})
    policy = f"default-src 'none'; script-src '{csp_hash(javascript)}'; style-src '{csp_hash(styles)}'; connect-src 'none'; base-uri 'none'; form-action 'none'"
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{policy}">
<meta name="description" content="Inspect short source-linked political records, task lenses, attribution and review boundaries. Runs offline without API keys.">
<title>TACITUS · Policy evidence explorer</title><style>{styles}</style></head>
<body><a class="skip" href="#records">Skip to evidence</a>
<header><a class="wordmark" href="https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open">TACITUS <span>RESEARCH EXAMPLE / 01</span></a>
<p class="eyebrow">Sources before synthesis</p><h1>Read the evidence.<br><span>Keep the distinctions.</span></h1>
<p class="lede">A small political research desk: UN resolutions, a communiqué, mediation guidance, reported statements and policy text. Change the task. Inspect what the source actually says.</p>
<div class="facts"><span><strong>{len(data['sources'])}</strong> sources</span><span><strong>{len(data['records'])}</strong> typed records</span><span><strong>{len(data['lenses'])}</strong> task lenses</span><span><strong>0</strong> model calls</span></div>
</header><main><aside aria-labelledby="task-title"><p class="eyebrow">01 / Select the work</p><h2 id="task-title">What are you doing?</h2>
<div id="lenses" class="lens-list" aria-label="Task lenses"></div>
<label for="recipe">Recurring task</label><select id="recipe"><option value="">Choose a recipe</option></select>
<label for="published-by">Consulted source published by</label><input id="published-by" type="date">
<p class="hint">A publication filter, not a claim about what was known or legally in force at that time.</p>
<label class="check"><input id="drafts" type="checkbox"> Include analyst drafts and candidates</label>
<div class="boundary"><strong>Checked wording ≠ verified conclusion.</strong><p>No record has human approval. Drafts, hypotheses and applicability questions keep their own status.</p></div>
</aside><section id="records" aria-labelledby="results-title" tabindex="-1"><div class="results-heading"><div><p class="eyebrow">02 / Follow the source</p><h2 id="results-title"></h2></div><p id="count" role="status" aria-live="polite"></p></div>
<p id="purpose"></p><div id="recipe-detail"></div><div id="record-list"></div>
<section class="exports" aria-labelledby="exports-title"><p class="eyebrow">03 / Take it with you</p><h2 id="exports-title">Inspectable, portable data.</h2>
<p>The selected JSON is this example's teaching format. Full exports include drafts and candidates; retain review-state rules when querying them.</p>
<div class="buttons"><button id="selection">Download selected JSON</button><button id="jsonld">Full JSON-LD 1.1</button><button id="sql">Full local SQLite SQL</button></div>
<p class="hint">No native capsule interchange or automatic PRAXIS attachment is claimed. SQLite portability is tested locally; this is not a live D1 migration.</p></section>
</section></main><footer><strong>Small on purpose.</strong><p>Curated excerpts, not a complete corpus. Source hashes check retained bytes, not truth. A single headline does not establish outlet-wide bias. HR applicability remains unassessed.</p><p>All interactions run in this file. No analytics, model service, database or network fetch is used. Opening a source link leaves the offline explorer.</p></footer>
<script type="application/json" id="dataset">{payload}</script><script>{javascript}</script></body></html>'''
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / "index.html"
    output.write_text(html, encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("dist"))
    parser.add_argument("--corpus", type=Path, default=HERE / "corpus.json")
    args = parser.parse_args()
    output = build(args.out, args.corpus)
    print(f"Built {output.resolve()} ({output.stat().st_size:,} bytes). Open it directly; no server or API keys required.")


if __name__ == "__main__":
    main()
