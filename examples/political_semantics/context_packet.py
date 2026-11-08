#!/usr/bin/env python3
"""Compile a bounded, reference-complete packet from the real-source teaching corpus."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from semantic_layer import HERE, EVIDENCE_STATES, load, query


def encoded(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def compile_packet(data: dict[str, Any], lens: str, question: str, budget_bytes: int,
                   published_by: str | None = None) -> dict[str, Any]:
    """Rank by explicit token overlap; keep whole records and all referenced context.

    This is a greedy teaching example, not optimal packing, political saliency,
    contradiction detection, a native ContextCapsule or a measured model gain.
    """
    if type(budget_bytes) is not int or budget_bytes < 256:
        raise ValueError('budget_bytes must be an integer of at least 256')
    if not isinstance(question, str) or not question.strip():
        raise ValueError('question must be a non-empty string')
    eligible = query(data, lens, published_by=published_by)['records']
    eligible_ids = {row['id'] for row in eligible}
    digest = hashlib.sha256(encoded(data)).hexdigest()
    actors = {row['id'] for row in data['actors']}
    terms = set(re.findall(r'\w+', question.casefold()))

    def score(row: dict[str, Any]) -> int:
        return len(terms & set(re.findall(r'\w+', row['statement'].casefold())))

    def actor_references(value: Any) -> set[str]:
        if isinstance(value, dict):
            return set().union(*(actor_references(child) for child in value.values()))
        if isinstance(value, list):
            return set().union(*(actor_references(child) for child in value))
        return {value} if isinstance(value, str) and value in actors else set()

    def packet_for(records: list[dict[str, Any]]) -> dict[str, Any]:
        evidence_ids = {link['evidence_id'] for row in records for link in row['evidence']}
        evidence = sorted((row for row in data['evidence'] if row['id'] in evidence_ids), key=lambda row: row['id'])
        source_ids = {row['source_id'] for row in evidence}
        sources = sorted((row for row in data['sources'] if row['id'] in source_ids), key=lambda row: row['id'])
        actor_ids = actor_references([records, evidence, sources])
        concepts = {key for row in records for key in row['concept_ids']}
        return {'format': 'political-context-packet/1', 'input_sha256': digest,
                'lens': lens, 'purpose': data['lenses'][lens], 'question': question,
                'published_by': published_by, 'records': records, 'evidence': evidence,
                'sources': sources,
                'actors': sorted((row for row in data['actors'] if row['id'] in actor_ids), key=lambda row: row['id']),
                'concepts': sorted((row for row in data['concepts'] if row['id'] in concepts), key=lambda row: row['id']),
                'policy': 'Checked source wording only; no human approval is inferred. '
                          'Records retain unknown validity and applicability. Omitted context may change interpretation.',
                'limits': data['limits']}

    selected: list[dict[str, Any]] = []
    omitted = []
    if len(encoded(packet_for([]))) > budget_bytes:
        raise ValueError('budget is smaller than the packet envelope and question')
    for row in data['records']:
        if row['id'] in eligible_ids:
            continue
        reason = ('outside_lens' if lens not in row['lenses'] else
                  'review_required' if row['review_state'] not in EVIDENCE_STATES else 'publication_cutoff')
        omitted.append({'id': row['id'], 'reason': reason})
    for row in sorted(eligible, key=lambda row: (-score(row), row['id'])):
        if len(encoded(packet_for(selected + [row]))) <= budget_bytes:
            selected.append(row)
        else:
            omitted.append({'id': row['id'], 'reason': 'budget'})
            # Later evidence may fit even when this entire source bundle does not.
    packet = packet_for(selected)
    packet_bytes = encoded(packet)
    return {'packet': packet, 'receipt': {
        'input_sha256': digest, 'packet_sha256': hashlib.sha256(packet_bytes).hexdigest(),
        'packet_encoding': 'compact_sorted_json_utf8', 'packet_bytes': len(packet_bytes),
        'budget_bytes': budget_bytes, 'eligible_packet_bytes': len(encoded(packet_for(eligible))),
        'eligible_records': len(eligible), 'retained_records': len(selected),
        'eligible_primitives': sorted({row['primitive'] for row in eligible}),
        'retained_primitives': sorted({row['primitive'] for row in selected}),
        'included': [row['id'] for row in selected], 'omitted': sorted(omitted, key=lambda row: row['id']),
        'selection': 'question-token overlap on statements; stable ID tie-break; whole evidence bundles',
        'scope': 'Exact payload bytes, not model tokens or analytical quality; no network or model calls'}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, default=HERE / 'corpus.json')
    parser.add_argument('--lens', required=True)
    parser.add_argument('--question', required=True)
    parser.add_argument('--budget-bytes', type=int, default=8000)
    parser.add_argument('--published-by')
    parser.add_argument('--packet-only', action='store_true', help='Write only the exact bounded packet bytes, excluding the inspection receipt.')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    try:
        result = compile_packet(load(args.corpus), args.lens, args.question, args.budget_bytes, args.published_by)
        output = encoded(result['packet']) if args.packet_only else json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2).encode() + b'\n'
        if args.out:
            args.out.write_bytes(output)
        else:
            import sys
            sys.stdout.buffer.write(output)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f'Packet compilation failed: {error}\n')


if __name__ == '__main__':
    main()
