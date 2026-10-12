# Stable Studionet deployment evidence

**Current status: NOT DEPLOYED / NOT VERIFIED.** No address, transaction, hash, or test result in `deployments/studionet.json` is represented as live evidence.

Network: `studionet` — chain ID `61999` — RPC `https://studio.genlayer.com/api`.

Before *every* deployment/write:

1. Confirm stable GenLayer SDK effective RPC is `https://studio.genlayer.com/api` and actual chain ID is **61999**. Run `python scripts/live_studionet.py --verify-only`; it uses the stable `genlayer-py==0.16.3` Studionet chain preset and reads the chain ID through the SDK. The separate raw JSON-RPC `eth_chainId` probe returned HTTP 403 here; the SDK read succeeded and returned 61999. If the SDK check fails, abort before signing or broadcasting.
2. Do not switch to preview environment or adapt a preview chain ID as a workaround.
3. Set `GENLAYER_PRIVATE_KEY` and a separately funded `GENLAYER_UNAUTHORIZED_PRIVATE_KEY` in the process environment. Never store either in git. The pinned stable Python client does not expose the newer `estimate_transaction_fees` method; its stable `write_contract`/`deploy_contract` methods manage the transaction envelope. Do not install a preview SDK to obtain a different fee API.
4. Save exact CLI/Python commands and actual finalized transactions.

Use `demo/selection.json` as an input manifest, not proof of execution. The script `scripts/live_studionet.py` is built against the installed stable SDK and checks effective RPC plus actual chain ID before every deployment/write. It checkpoints submitted hashes and waits for `FINALIZED` receipts. It refuses placeholder fixture URLs and does not force a certified winner. Run `python scripts/live_studionet.py --run` only after the fixtures have been pushed and pinned. It has not been run because the fixture commit is not yet public and no signing keys are configured.

Require real evidence for: both deploys, selection creation, criteria/candidates, sealing, consensus assessments, complete pair matrix, ranking hash, `winner_certified=true` for consumer success, gate success, wrong definition rejection, wrong ranking rejection, losing candidate rejection, replay rejection, and explorer references. If ranking cannot certify a strict winner, do **not** claim a successful award gate lifecycle; report the blocker.

## CLI and tests

```bash
python -m pip install -r requirements-test.txt
python scripts/preflight.py
python -m compileall -q contracts tests scripts
python -m pytest -q tests/test_merit_circuit.py
python -m pytest -q tests/direct/
python scripts/live_studionet.py --verify-only
python scripts/live_studionet.py --run
python scripts/preflight.py --final
```

The lifecycle script uses `genlayer-py==0.16.3`; it waits for a finalized receipt and verifies its execution result before recording success. Direct Mode cannot test address-based cross-contract calls, so the MeritAwardGate checks require the deployed typed interface on Studionet. The SDK identity probe confirmed chain ID 61999, but no transaction was sent because signing keys are not configured in this environment. Record immutable fixture SHA and complete receipt metadata. Do not change network target.
