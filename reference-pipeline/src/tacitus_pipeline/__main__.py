"""Validate sources, inspect changes and build reusable task context."""
import argparse
import json
from pathlib import Path
from .core import PipelineError, build, load_collection, validate, write_bundle
from .interchange import app_bundle, collection_diff
from .selection import select_layer
from .standards import standards_graph


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'validate', 'diff'])
    parser.add_argument('--input', type=Path)
    parser.add_argument('--ontology', type=Path)
    parser.add_argument('--layer', type=Path)
    parser.add_argument('--question')
    parser.add_argument('--budget', type=int, default=24000)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--before', type=Path)
    parser.add_argument('--after', type=Path)
    parser.add_argument('--selection', choices=['authored', 'bm25', 'graph'], default='authored')
    parser.add_argument('--app-export', action='store_true')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'diff':
            if not args.before or not args.after:
                parser.error('diff requires --before and --after')
            result = collection_diff(load_collection(args.before), load_collection(args.after))
        else:
            if not args.input or not args.ontology:
                parser.error('--input and --ontology are required')
            data = load_collection(args.input)
            ontology = json.loads(args.ontology.read_text(encoding='utf-8'))
            sources, entities, statements = validate(data, ontology)
            result = {'valid': True, 'sources': len(sources), 'entities': len(entities), 'statements': len(statements), 'model_calls': 0}
            if args.command == 'build':
                if not args.layer or not args.question or not args.output:
                    parser.error('build requires --layer, --question and --output')
                layer = json.loads(args.layer.read_text(encoding='utf-8'))
                explanation = None
                if args.selection != 'authored':
                    layer, explanation = select_layer(data, ontology, layer, args.question, mode=args.selection)
                bundle = build(data, ontology, layer, question=args.question, budget=args.budget)
                if explanation:
                    bundle['selection.json'] = explanation
                if args.app_export:
                    bundle['app-bundle.json'] = app_bundle(data, ontology, layer, question=args.question, budget=args.budget)
                    bundle['standards.jsonld'] = standards_graph(data, ontology, layer)
                write_bundle(bundle, args.output, force=args.force)
                result = bundle['receipt.json']
    except (PipelineError, OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f'Pipeline refused: {error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
