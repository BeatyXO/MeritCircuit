#!/usr/bin/env python3
"""Read-only chain-id probe. Never broadcasts writes or uses a private key.

genlayer RPC may not support eth_chainId; an unsupported method is a BLOCKER,
not permission to assume network identity or switch to a different network.
"""
import json
import sys
import urllib.request

RPC = 'https://studio.genlayer.com/api'
EXPECTED = 61999


def main():
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []}).encode()
    req = urllib.request.Request(RPC, body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
    except Exception as exc:
        raise SystemExit(f'Network identity not established; do not write: {exc}')
    value = data.get('result')
    if not isinstance(value, str):
        raise SystemExit(f'Unsupported eth_chainId response: {data!r}; use supported stable SDK network read before writes')
    chain_id = int(value, 16) if value.startswith('0x') else int(value)
    if chain_id != EXPECTED:
        raise SystemExit(f'CHAIN MISMATCH: expected {EXPECTED}, got {chain_id}')
    print(f'Confirmed RPC {RPC} chain ID {chain_id}')


if __name__ == '__main__':
    main()
