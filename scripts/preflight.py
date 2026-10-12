#!/usr/bin/env python3
"""Static handoff preflight. Does NOT validate chain execution or Direct Mode."""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(condition, text):
    if not condition:
        raise RuntimeError(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--final', action='store_true', help='require immutable fixture SHA and populated live evidence')
    args = parser.parse_args()
    expected = {"network": "studionet", "chain_id": 61999, "rpc": "https://studio.genlayer.com/api"}
    manifest = json.loads((ROOT / 'deployments/studionet.json').read_text())
    check(all(manifest.get(k) == v for k, v in expected.items()), 'stable Studionet identity mismatch')
    config = (ROOT / 'gltest.config.yaml').read_text()
    check('https://studio.genlayer.com/api' in config and 'studionet:' in config, 'stable network config missing')
    check('studio-dev.genlayer.com' not in config and 'studio-next.genlayer.com' not in config, 'preview env forbidden')
    for path in (ROOT / 'contracts').glob('*.py'):
        content = path.read_text(encoding='utf-8')
        check('"Depends": "py-genlayer:' in content, f'GenVM SDK pin missing: {path}')
        ast.parse(content, filename=str(path))
    demo = json.loads((ROOT / 'demo/selection.json').read_text())
    check(sum(int(c['weight']) for c in demo['criteria']) == 100, 'fixture weights not 100')
    for c in demo['candidates']:
        check(c['evidence_url'].startswith('https://raw.githubusercontent.com/BeatyXO/MeritCircuit/'), 'wrong fixture origin')
        if args.final:
            check('FIXTURE_COMMIT_PLACEHOLDER' not in c['evidence_url'], 'fixture commit placeholder not pinned')
            check(re.search(r'/MeritCircuit/[0-9a-f]{40}/fixtures/', c['evidence_url']) is not None, 'fixture URL is not pinned to a full commit')
    check(not (ROOT / 'frontend').exists(), 'unexpected frontend')
    check(not any(ROOT.rglob('.env')), 'secret-bearing .env file present')
    if args.final:
        require_live = ('merit_circuit_address', 'merit_circuit_deploy_tx',
                        'merit_award_gate_address', 'merit_award_gate_deploy_tx',
                        'definition_hash', 'ranking_hash', 'selection_id',
                        'award_success_tx', 'replay_rejection_evidence')
        for field in require_live:
            check(manifest.get(field) not in (None, '', []), f'unproven live evidence: {field}')
        check(manifest.get('status') == 'VERIFIED', 'live verification status not established')
    print('Preflight PASS (' + ('final' if args.final else 'handoff') + ', static checks only)')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('Preflight FAIL:', exc, file=sys.stderr)
        raise SystemExit(1)
