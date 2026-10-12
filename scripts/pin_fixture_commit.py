#!/usr/bin/env python3
"""Replace fixture reference placeholder after first pushed fixture commit.

The input SHA MUST be an already existing remote GitHub commit containing all
three fixture files. This script does not verify GitHub; agent must check remote.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'demo' / 'selection.json'
PLACEHOLDER = 'FIXTURE_COMMIT_PLACEHOLDER'


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r'[0-9a-f]{40}', sys.argv[1]):
        raise SystemExit('Usage: python scripts/pin_fixture_commit.py <REAL_PUSHED_40_HEX_SHA>')
    sha = sys.argv[1]
    raw = TARGET.read_text(encoding='utf-8')
    if PLACEHOLDER not in raw:
        raise SystemExit('No placeholder present; check for an already pinned fixture SHA')
    doc = json.loads(raw.replace(PLACEHOLDER, sha))
    for c in doc['candidates']:
        assert f'/BeatyXO/MeritCircuit/{sha}/fixtures/' in c['evidence_url'], 'unexpected fixture URL'
    TARGET.write_text(json.dumps(doc, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print(f'Pinned three fixture URLs to {sha} (now commit + push this change)')


if __name__ == '__main__':
    main()
