# Stable Studionet deployment evidence

**Current active lifecycle: corrected version is being deployed.** The initial immutable version was deployed on Studionet and preserved as superseded evidence in `deployments/attempt_1.json`. Its first comparison reverted during `ComparisonRecorded.emit()` because the event exceeded GenVM's indexed-topic limit. The event definition is corrected in the source; because deployed code is immutable, a new contract instance and selection are required. The active manifest is reset and records only the corrected lifecycle.

Network: `studionet` — chain ID `61999` — RPC `https://studio.genlayer.com/api`.

Before *every* deployment/write:

1. Confirm stable GenLayer SDK effective RPC is `https://studio.genlayer.com/api` and actual chain ID is **61999**. Run `python scripts/live_studionet.py --verify-only`; it uses the stable `genlayer-py==0.16.3` Studionet chain preset and reads the chain ID through the SDK. The separate raw JSON-RPC `eth_chainId` probe returned HTTP 403 here; the SDK read succeeded and returned 61999. If the SDK check fails, abort before signing or broadcasting.
2. Do not switch to preview environment or adapt a preview chain ID as a workaround.
3. Set `GENLAYER_PRIVATE_KEY` and a separately funded `GENLAYER_UNAUTHORIZED_PRIVATE_KEY` in the process environment. Never store either in git. The pinned stable Python client does not expose the newer `estimate_transaction_fees` method; its stable `write_contract`/`deploy_contract` methods manage the transaction envelope. Do not install a preview SDK to obtain a different fee API.
4. Save exact CLI/Python commands and actual finalized transactions.

Use `demo/selection.json` as an input manifest, not proof of execution. Its three fixture URLs are pinned to pushed commit `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5` and each raw URL returned HTTP 200. The script `scripts/live_studionet.py` checks effective RPC plus actual chain ID before every deployment/write, checkpoints submitted hashes, and waits for `FINALIZED` receipts. It normalizes the stable RPC's `consensus_data.leader_receipt` only when final majority agreement and a return/error outcome are both present. The first live run exposed and corrected two actual runtime issues (stable SDK execution-result shape and typed `CalldataAddress` constructor calldata) plus the contract event topic limit. The first deployed instances are superseded; a corrected lifecycle is now being run with user-authorized funded test wallets. It refuses placeholder fixture URLs and does not force a certified winner.

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

The lifecycle script uses `genlayer-py==0.16.3`; it waits for a finalized receipt and verifies its execution result before recording success. Direct Mode cannot test address-based cross-contract calls, so the MeritAwardGate checks require the deployed typed interface on Studionet. The SDK identity probe confirmed actual chain ID 61999 before all observed writes. Preserve exact finalized hashes and execution evidence; do not change network target.
