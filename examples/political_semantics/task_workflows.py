"""Build five inspectable policy work packets from retained attributed excerpts; no model calls."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from context_packet import compile_packet, encoded
from semantic_layer import HERE, load
from verify_packet import verify

QUESTIONS = {
    'resolution_brief': 'resolution endorses shall transitional governing implementation',
    'communique_comparison': 'Geneva communique transitional governing mutual consent endorsement',
    'mediation_preparation': 'mediation consent inclusion parties impartiality',
    'media_framing_review': 'Reuters reports attributed speaker headline framing',
    'hr_policy_application': 'violence harassment world work convention applicability',
}
PACKAGE_SCOPE = 'File integrity and reproducible selection; no independent truth or human approval implied.'


def build_task(data: dict[str, Any], task: str, budget: int = 8000,
               published_by: str | None = None) -> dict[str, Any]:
    if task not in QUESTIONS or task not in data['recipes']:
        raise ValueError(f'Unknown task: {task}')
    recipe = data['recipes'][task]
    result = compile_packet(data, recipe['lens'], QUESTIONS[task], budget, published_by)
    verify(result, data)
    return {'task': task, 'intended_output': recipe['output'], 'context': result,
            'review_questions': recipe['review_questions'],
            'unresolved_checks': [{'field': field, 'status': 'requires_analyst_assessment'}
                                  for field in recipe['required_evidence_fields']],
            'analyst_interpretation': None, 'hypotheses': [], 'approval': 'not_reviewed',
            'scope': 'A preparation worksheet, not a completed brief, bias assessment or legal opinion.'}


def markdown(work: dict[str, Any]) -> str:
    packet = work['context']['packet']; receipt = work['context']['receipt']
    evidence = {e['id']: e for e in packet['evidence']}
    sources = {s['id']: s for s in packet['sources']}
    lines = ['# ' + work['task'].replace('_', ' '), '', work['scope'], '',
             '## Selection', '', f"Retained {receipt['retained_records']} of {receipt['eligible_records']} eligible records; "
             f"{receipt['packet_bytes']} exact compact UTF-8 bytes within {receipt['budget_bytes']} bytes. "
             'The worksheet and receipt add bytes outside that budget. No token-count or reasoning-quality claim.', '',
             '## Attributed source assertions', '']
    for row in packet['records']:
        lines += ['### ' + row['id'], '', row['statement'], '',
                  f"Primitive: {row['primitive']}; modality: {row['modality']}; review: {row['review_state']}. "
                  f"Human reviewed: {row['human_reviewed']}.", '']
        for link in row['evidence']:
            e = evidence[link['evidence_id']]; s = sources[e['source_id']]
            # JSON quoting retains the exact original passage, including line breaks and punctuation.
            lines += ['Exact retained passage: ' + json.dumps(link['quote'], ensure_ascii=False), '',
                      f"Source: [{s['id']}]({s['url']}); evidence: `{e['id']}`.", '',
                      'Evidence metadata (dates, locators and attribution retained):', '',
                      '```json', json.dumps(e, ensure_ascii=False, sort_keys=True, indent=2), '```', '']
    lines += ['## Unresolved applicability and evidence checks', '']
    lines += [f"- [ ] {check['field']}: requires analyst assessment." for check in work['unresolved_checks']]
    lines += ['', '## Human review questions', '']
    lines += ['- ' + q for q in work['review_questions']]
    lines += ['', '## Analyst interpretation and hypotheses', '',
              'Not supplied. Record interpretations separately from quotations and mark hypotheses explicitly.', '',
              '## Omissions', '', '```json', json.dumps(receipt['omitted'], indent=2), '```', '']
    return '\n'.join(lines)


def export(data: dict[str, Any], tasks: list[str], destination: Path, budget: int,
           published_by: str | None = None) -> dict[str, Any]:
    # Validate and prepare all results before writing: invalid options cannot leave a partial package.
    if not tasks or len(set(tasks)) != len(tasks):
        raise ValueError('Choose at least one unique task')
    works = [build_task(data, task, budget, published_by) for task in tasks]
    if destination.exists():
        raise ValueError('Output path already exists; choose a fresh directory to preserve prior work')
    files: dict[str, bytes] = {}
    comparison = []
    for work in works:
        task = work['task']
        files[task + '.json'] = (json.dumps(work, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
        files[task + '.md'] = markdown(work).encode('utf-8')
        files[task + '.packet.json'] = encoded(work['context']['packet'])
        files[task + '.inspection.json'] = (json.dumps(work['context'], ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
        for size in sorted(set([4000, 8000, 16000, budget])):
            r = build_task(data, task, size, published_by)['context']['receipt']
            comparison.append({k: r[k] for k in ['budget_bytes','packet_bytes','eligible_records','retained_records','omitted','retained_primitives']} | {'task': task})
    files['budget-comparison.json'] = (json.dumps(comparison, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
    manifest = {'format': 'political-task-package/1', 'tasks': tasks,
                'files': {name: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()} for name, raw in sorted(files.items())},
                'scope': PACKAGE_SCOPE}
    destination.mkdir(parents=True)
    for name, raw in files.items():
        (destination / name).write_bytes(raw)
    (destination / 'manifest.json').write_bytes((json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode())
    return manifest


def verify_package(directory: Path, data: dict[str, Any]) -> dict[str, Any]:
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    if set(manifest) != {'format','tasks','files','scope'} or manifest.get('format') != 'political-task-package/1' or manifest.get('scope') != PACKAGE_SCOPE:
        raise ValueError('Unsupported package format')
    if not isinstance(manifest.get('tasks'), list) or not manifest['tasks'] or len(set(manifest['tasks'])) != len(manifest['tasks']):
        raise ValueError('Invalid task list')
    expected_names = {task + suffix for task in manifest['tasks'] for suffix in ['.json','.md','.packet.json','.inspection.json']} | {'budget-comparison.json'}
    if set(manifest['files']) != expected_names:
        raise ValueError('Missing or unexpected manifest file')
    if set(p.name for p in directory.iterdir()) != expected_names | {'manifest.json'}:
        raise ValueError('Package has missing or unlisted files')
    for name, metadata in manifest['files'].items():
        if Path(name).name != name or not (directory / name).is_file() or (directory / name).is_symlink():
            raise ValueError('Unsafe package path')
        raw = (directory / name).read_bytes()
        if len(raw) != metadata['bytes'] or hashlib.sha256(raw).hexdigest() != metadata['sha256']:
            raise ValueError('Package file integrity mismatch')
    comparison = []
    for task in manifest['tasks']:
        work = json.loads((directory / (task + '.json')).read_text(encoding='utf-8'))
        p = work['context']['packet']; r = work['context']['receipt']
        expected = build_task(data, task, r['budget_bytes'], p['published_by'])
        if work != expected or (directory / (task + '.md')).read_bytes() != markdown(expected).encode('utf-8'):
            raise ValueError('Worksheet differs from attributed source reconstruction')
        inspection = json.loads((directory / (task + '.inspection.json')).read_text(encoding='utf-8'))
        verify(inspection, data)
        if inspection != expected['context'] or (directory / (task + '.packet.json')).read_bytes() != encoded(p):
            raise ValueError('Packet variants disagree')
        for size in sorted(set([4000, 8000, 16000, r['budget_bytes']])):
            report = build_task(data, task, size, p['published_by'])['context']['receipt']
            comparison.append({key: report[key] for key in ['budget_bytes','packet_bytes','eligible_records','retained_records','omitted','retained_primitives']} | {'task': task})
    if json.loads((directory / 'budget-comparison.json').read_text(encoding='utf-8')) != comparison:
        raise ValueError('Budget comparison differs from source reconstruction')
    return {'status': 'verified', 'tasks': len(manifest['tasks']), 'files': len(manifest['files']), 'scope': manifest['scope']}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', choices=['all', *QUESTIONS], default='all')
    parser.add_argument('--budget-bytes', type=int, default=8000)
    parser.add_argument('--published-by')
    parser.add_argument('--corpus', type=Path, default=HERE / 'corpus.json')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--out', type=Path)
    group.add_argument('--verify', type=Path)
    args = parser.parse_args()
    try:
        data = load(args.corpus)
        result = verify_package(args.verify, data) if args.verify else export(data, list(QUESTIONS) if args.task == 'all' else [args.task], args.out, args.budget_bytes, args.published_by)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f'Task workflow failed: {error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
