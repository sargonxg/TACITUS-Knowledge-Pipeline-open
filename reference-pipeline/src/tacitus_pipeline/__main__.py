"""Run the reference pipeline without credentials or services."""
import argparse
import json
import sys
from pathlib import Path
from .core import PipelineError, build, load_collection, write_bundle

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build'])
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--ontology', type=Path, required=True)
    parser.add_argument('--layer', type=Path, required=True)
    parser.add_argument('--question', required=True)
    parser.add_argument('--budget', type=int, default=24000)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--force', action='store_true')
    a = parser.parse_args()
    try:
        result = build(load_collection(a.input), json.loads(a.ontology.read_text()), json.loads(a.layer.read_text()), question=a.question, budget=a.budget)
        write_bundle(result, a.output, force=a.force)
    except (PipelineError, OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f'Pipeline refused: {error}\n')
    print(json.dumps(result['receipt.json'], indent=2))

if __name__ == '__main__':
    main()
