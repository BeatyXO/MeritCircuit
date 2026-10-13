# Build status (2026-10-13)

**Implementation, tests, and a real certified consumer scenario are verified. The required three-candidate selection remains incomplete because one criterion exhausted its retry cap.** Repository: [BeatyXO/MeritCircuit](https://github.com/BeatyXO/MeritCircuit), branch `main`. Immutable fixture commit: `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5`; all three raw GitHub fixture URLs were verified HTTP 200.

Local verification:

- `python scripts/preflight.py`: PASS.
- `python -m compileall -q contracts tests scripts`: PASS.
- `python -m pytest -q tests/test_merit_circuit.py`: 42 passed.
- `python -m pytest -q tests/direct/`: 6 passed with `genlayer-test 0.29.2`, `genlayer-py 0.16.3`, GenVM runner `v0.2.16`; tests exercise independent verifier re-evaluation.
- `python -m pytest -q`: 54 passed.
- `python scripts/live_studionet.py --verify-only`: confirmed effective RPC `https://studio.genlayer.com/api`, alias `studionet`, actual chain ID `61999`.
- `python scripts/preflight.py --final`: FAILS on the intentionally absent ranking hash for the required three-candidate selection. No result was fabricated to satisfy this gate.

Current stable Studionet deployments: MeritCircuit `0x0dA56CfDDc73442247456C095A368187a557F446` (deployment tx `0xff52ae69df8126211893bb33e2a25f7d3104b6b1a8358ab1829d48487766d1c4`) and MeritAwardGate `0x74cFFb3AECD829C6280bb7647E7Fc17Ef560aEF2` (deployment tx `0x703801fda192f72c4f50d15657da3c97c2ea0a25ac60da36ead4076de6b6f859`). The deployed MeritCircuit source corresponds to commit `147c74c89fad7f4f99aa753160911f6ca6a30f28`.

Selection 1 is the required three-candidate selection, sealed at definition hash `98188e8cf9b721d1a8f514700e23c34fc797b7dd8c1bcf011bb97042d379a656`. Two of three pairs finalized: 1–2 at +100 and 2–3 at −100. Pair 1–3 criterion 2 returned `INDETERMINATE` on three finalized attempts; the stored reason is `mirrored verdict inconsistency`. One intervening retry transaction was canceled with `NO_MAJORITY` and did not count as a contract assessment. The bounded cap is exhausted; this selection has no complete matrix, ranking hash, or certified winner. Exact transactions, verdicts, and quotes are in `deployments/studionet.json` and `deployments/attempt_5.json` is the archived run state.

A separate, explicitly identified two-candidate scenario uses the same immutable synthetic Alpha/Beta sources and unchanged criteria to demonstrate the consumer path without claiming selection 1 is complete. Selection 2 finalized its only pair at +100, ranking hash `2deec450bc40aa3cb3ab0c8695240c9223ec028f58ea833b9f7347cb9535e426`, strict winner candidate 1, and a real typed MeritAwardGate award. Wrong-definition, wrong-ranking, losing-candidate, replay, and unauthorized-caller actions all finalized with their expected rejection errors. Full evidence is in `deployments/award_scenario.json`.

Earlier deployment and gate probe evidence is retained under `deployments/attempt_1.json` through `attempt_4.json` and `deployments/attempt_4_gate_probe.json`. The user-provided test keys were used only in temporary process environments and are not in the repository; because they were shared in chat, retire those wallets after sweeping remaining funds.

The remaining limitation is selection 1's ambiguous mirrored assessment. Changing its rubric, weights, mirror requirement, retry cap, or recording a winner would violate the protocol. Continue to use stable Studionet only; do not replace missing primary-selection evidence with the successful separate scenario.
