# Stable Studionet deployment evidence

**Selection 3 completed the three-candidate lifecycle and typed consumer checks on stable Studionet.** Earlier deploy attempts are archived in `deployments/attempt_1.json` through `attempt_4.json`. Current MeritCircuit is `0x0dA56CfDDc73442247456C095A368187a557F446` and MeritAwardGate is `0x74cFFb3AECD829C6280bb7647E7Fc17Ef560aEF2`.

Selection 2 is a separate, two-candidate gate demonstration using the pinned synthetic Alpha/Beta sources and the unchanged criteria. It finalized at margin +100 and certified candidate 1 with ranking hash `2deec450bc40aa3cb3ab0c8695240c9223ec028f58ea833b9f7347cb9535e426`. A real typed gate award succeeded, then wrong-definition, wrong-ranking, losing-candidate, replay, and unauthorized-caller probes all finalized with expected errors. See `deployments/award_scenario.json`; it does not represent the incomplete selection 1 as complete.

Selection 3 is the completed three-candidate live lifecycle. It uses immutable fixture commit `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5` and one 100-weight criterion, “Demonstrated implementation and integration evidence.” Definition hash: `20b2e6e358dac1f2af68cb48a28126bfa81f144a320af4a1efbd49d8246495c5`. Three independently assessed pairs finalized at 1–2 `+100`, 1–3 `−100`, and 2–3 `−100`; order `[3, 1, 2]`; strict winner candidate 3; ranking hash `f307162ec17b9465e31e63d7fbec3d395ae5564c88000d1705af8871b44d9cd6`.

- [Finalized ranking](https://explorer-studio.genlayer.com/tx/0x9c17e6cb013596edda37e40d820037c2cc881da2c8046e8cc4227e2842f40d93)
- [Successful typed gate award](https://explorer-studio.genlayer.com/tx/0x5eb53b57ad1dd473ef29d0d27c8fb8e86b1811ee0725e58f314fd5020de82b95)
- [Wrong definition](https://explorer-studio.genlayer.com/tx/0x79f7c3c3ea4671fcd7ed2e59c1fccb7d5f85b92ee35599457cb376446732c94b), [wrong ranking](https://explorer-studio.genlayer.com/tx/0xc707c228dc273c69f5983a22eba6f52643427b65f0fdf11c4a38a99124470179), [loser](https://explorer-studio.genlayer.com/tx/0x9cc6b92cbdde9e87bfb5a13368d45bbccfd1a2a655559062ef0e6194d40d2db9), [replay](https://explorer-studio.genlayer.com/tx/0x3465dc39f01cddeb5e1759410ff49571ccd9af75c39f0fd23b4761fd4c3068e8), and [unauthorized caller](https://explorer-studio.genlayer.com/tx/0x84278efc547527aa0c41145a740501100de5eca2bc9b36aab78b1486a7731997) rejections all finalized with their expected contract errors.

The original selection 1 remains archived, unchanged, at definition hash `98188e8cf9b721d1a8f514700e23c34fc797b7dd8c1bcf011bb97042d379a656`. Pair 1–3 criterion 2 exhausted its three attempts with `INDETERMINATE` / `mirrored verdict inconsistency`; it has no ranking. Selection 3 is a fresh selection and does not rewrite that result.

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
python scripts/run_studionet_full_lifecycle.py
python scripts/preflight.py --final
```

The lifecycle script uses `genlayer-py==0.16.3`; it waits for a finalized receipt and verifies its execution result before recording success. Direct Mode cannot test address-based cross-contract calls, so the MeritAwardGate checks require the deployed typed interface on Studionet. The SDK identity probe confirmed actual chain ID 61999 before all observed writes. Preserve exact finalized hashes and execution evidence; do not change network target.


## Recorded selection outcomes

- Selection 1 pair margins: 1–2 `+100`, 2–3 `−100`. It has 2 finalized pairs out of 3 and no ranking hash. The unresolved 1–3 criterion has three finalized INDETERMINATE records with reason `mirrored verdict inconsistency`; there is also one separately recorded canceled `NO_MAJORITY` transaction that did not execute an assessment. Full archive: `deployments/attempt_5.json`.
- Selection 2 ranking: candidate 1 is the strict Condorcet winner at `+100`; definition hash `58efb2b4ae8d4bc25eaeb61d667275566181eb181c896c4ca7c97c51e31bc495`; ranking hash `2deec450bc40aa3cb3ab0c8695240c9223ec028f58ea833b9f7347cb9535e426`. [Finalized ranking transaction](https://explorer-studio.genlayer.com/tx/0xa058dc6866e239bc81dac4325b42d5c3362bd2f47456c04d1c5438f957dde0b7); [successful typed award transaction](https://explorer-studio.genlayer.com/tx/0x8b3e01035b941bab901ac7d3e48d752f73340565c38f8053ac3897ea1927049a); [wrong-definition rejection](https://explorer-studio.genlayer.com/tx/0xa8bab84ecef4593c79482badd9235376bfdb71532f63680f2b888feacaf70a62).
- Selection 3 ranking: candidate 3 is the strict Condorcet winner; definition hash `20b2e6e358dac1f2af68cb48a28126bfa81f144a320af4a1efbd49d8246495c5`; ranking hash `f307162ec17b9465e31e63d7fbec3d395ae5564c88000d1705af8871b44d9cd6`. All three pair margins, quotes, assessment hashes, gate award record, transaction receipts and explorer URLs are in `deployments/studionet.json`.
- The separate scenario's five finalized gate rejections are listed in `deployments/award_scenario.json` with exact transaction hashes and leader errors. Explorer transaction URLs are recorded there. The ranking and successful-award pages were visibly confirmed as FINALIZED in the GenLayer Studio Explorer; all other listed transaction statuses and error payloads were verified via stable SDK receipts.
- `python scripts/preflight.py --final` passes locally against the completed selection 3 evidence. The original selection 1 remains explicitly indeterminate; do not claim it has a ranking or winner.
