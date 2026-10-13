# Stable Studionet deployment evidence

**Primary selection incomplete; separate consumer proof complete.** Earlier deploy attempts are archived in `deployments/attempt_1.json` through `attempt_4.json`. Current MeritCircuit is `0x0dA56CfDDc73442247456C095A368187a557F446` and MeritAwardGate is `0x74cFFb3AECD829C6280bb7647E7Fc17Ef560aEF2`. Selection 1 (3 candidates, 2 criteria) has definition hash `98188e8cf9b721d1a8f514700e23c34fc797b7dd8c1bcf011bb97042d379a656`; pairs 1–2 and 2–3 finalized, but pair 1–3 criterion 2 exhausted three attempts with `INDETERMINATE` / `mirrored verdict inconsistency`. Do not retry or rank that selection.

Selection 2 is a separate, two-candidate gate demonstration using the pinned synthetic Alpha/Beta sources and the unchanged criteria. It finalized at margin +100 and certified candidate 1 with ranking hash `2deec450bc40aa3cb3ab0c8695240c9223ec028f58ea833b9f7347cb9535e426`. A real typed gate award succeeded, then wrong-definition, wrong-ranking, losing-candidate, replay, and unauthorized-caller probes all finalized with expected errors. See `deployments/award_scenario.json`; it does not represent the incomplete selection 1 as complete.

Network: `studionet` — chain ID `61999` — RPC `https://studio.genlayer.com/api`.

Before *every* deployment/write:

1. Confirm stable GenLayer SDK effective RPC is `https://studio.genlayer.com/api` and actual chain ID is **61999**. Run `python scripts/live_studionet.py --verify-only`; it uses the stable `genlayer-py==0.16.3` Studionet chain preset and reads the chain ID through the SDK. The separate raw JSON-RPC `eth_chainId` probe returned HTTP 403 here; the SDK read succeeded and returned 61999. If the SDK check fails, abort before signing or broadcasting.
2. Do not switch to preview environment or adapt a preview chain ID as a workaround.
3. Set `GENLAYER_PRIVATE_KEY` and a separately funded `GENLAYER_UNAUTHORIZED_PRIVATE_KEY` in the process environment. Never store either in git. The pinned stable Python client does not expose the newer `estimate_transaction_fees` method; its stable `write_contract`/`deploy_contract` methods manage the transaction envelope. Do not install a preview SDK to obtain a different fee API.
4. Save exact CLI/Python commands and actual finalized transactions.

Use `demo/selection.json` as an input manifest, not proof of execution. Its three fixture URLs are pinned to pushed commit `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5` and each raw URL returned HTTP 200. The script `scripts/live_studionet.py` checks effective RPC plus actual chain ID before every deployment/write, checkpoints submitted hashes, and waits for `FINALIZED` receipts. It normalizes the stable RPC's `consensus_data.leader_receipt` only when final majority agreement and a return/error outcome are both present. Live tests exposed and corrected the SDK result shape, typed `CalldataAddress` constructor, and event topic limit. The current source uses an explicit four-field JSON example, preserves exact key/type/quote validation, adds valid enum whitespace/case normalization, mirrored-order checks, and whitespace-only quote-anchor normalization without changing the rubric, weights, or three-attempt cap. It refuses placeholder fixture URLs and does not force a certified winner.

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
python scripts/advance_studionet_pairs.py
python scripts/run_studionet_gate_scenario.py
python scripts/preflight.py --final
```

The lifecycle script uses `genlayer-py==0.16.3`; it waits for a finalized receipt and verifies its execution result before recording success. Direct Mode cannot test address-based cross-contract calls, so the MeritAwardGate checks require the deployed typed interface on Studionet. The SDK identity probe confirmed actual chain ID 61999 before all observed writes. Preserve exact finalized hashes and execution evidence; do not change network target.


## Recorded selection outcomes

- Selection 1 pair margins: 1–2 `+100`, 2–3 `−100`. It has 2 finalized pairs out of 3 and no ranking hash. The unresolved 1–3 criterion has three finalized INDETERMINATE records with reason `mirrored verdict inconsistency`; there is also one separately recorded canceled `NO_MAJORITY` transaction that did not execute an assessment.
- Selection 2 ranking: candidate 1 is the strict Condorcet winner at `+100`; definition hash `58efb2b4ae8d4bc25eaeb61d667275566181eb181c896c4ca7c97c51e31bc495`; ranking hash `2deec450bc40aa3cb3ab0c8695240c9223ec028f58ea833b9f7347cb9535e426`. [Finalized ranking transaction](https://explorer-studio.genlayer.com/tx/0xa058dc6866e239bc81dac4325b42d5c3362bd2f47456c04d1c5438f957dde0b7); [successful typed award transaction](https://explorer-studio.genlayer.com/tx/0x8b3e01035b941bab901ac7d3e48d752f73340565c38f8053ac3897ea1927049a); [wrong-definition rejection](https://explorer-studio.genlayer.com/tx/0xa8bab84ecef4593c79482badd9235376bfdb71532f63680f2b888feacaf70a62).
- The separate scenario's five finalized gate rejections are listed in `deployments/award_scenario.json` with exact transaction hashes and leader errors. Explorer transaction URLs are recorded there. The ranking and successful-award pages were visibly confirmed as FINALIZED in the GenLayer Studio Explorer; all other listed transaction statuses and error payloads were verified via stable SDK receipts.
- `python scripts/preflight.py --final` correctly remains failing because the primary three-candidate selection has no complete ranking.
