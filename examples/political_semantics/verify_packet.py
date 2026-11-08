"""Verify a saved inspection packet against its retained source corpus, offline."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any
from context_packet import compile_packet
from semantic_layer import HERE, load


def verify(result: dict[str, Any], corpus: dict[str, Any]) -> dict[str, Any]:
    """Recompute selection and all receipt fields; a self-consistent forged hash is insufficient."""
    if not isinstance(result, dict) or set(result) != {'packet', 'receipt'}:
        raise ValueError('Expected an inspection wrapper with packet and receipt')
    packet, receipt = result['packet'], result['receipt']
    if not isinstance(packet, dict) or not isinstance(receipt, dict):
        raise ValueError('Packet and receipt must be objects')
    expected = compile_packet(corpus, packet['lens'], packet['question'], receipt['budget_bytes'], packet.get('published_by'))
    if result != expected:
        raise ValueError('Packet or receipt differs from source-grounded deterministic reconstruction')
    return {'status': 'verified_against_retained_corpus', 'packet_bytes': receipt['packet_bytes'],
            'records': receipt['retained_records'], 'packet_sha256': receipt['packet_sha256'],
            'scope': 'Integrity and reproducibility only; not factual truth, legal applicability or human approval.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    parser.add_argument('--corpus', type=Path, default=HERE / 'corpus.json')
    args = parser.parse_args()
    try:
        result = verify(json.loads(args.packet.read_text(encoding='utf-8')), load(args.corpus))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f'Verification failed: {error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
