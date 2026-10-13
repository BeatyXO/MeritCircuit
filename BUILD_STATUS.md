# Build status (2026-10-13)

**Implementation, tests, and a fresh three-candidate live lifecycle are verified on stable Studionet. The original selection 1 remains honestly archived as incomplete. Latest publication is blocked by GitHub HTTP 403 write permission.** Repository: [BeatyXO/MeritCircuit](https://github.com/BeatyXO/MeritCircuit), branch `main`. Immutable fixture commit: `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5`; pinned fixture URLs were previously verified HTTP 200.

Local verification:

- `python scripts/preflight.py`: PASS.
- `python -m compileall -q contracts tests scripts`: PASS.
- `python -m pytest -q tests/test_merit_circuit.py`: 42 passed.
- `python -m pytest -q tests/direct/`: 6 passed with `genlayer-test 0.29.2`, `genlayer-py 0.16.3`, GenVM runner `v0.2.16`; tests exercise independent verifier re-evaluation.
- `python -m pytest -q`: 54 passed.
- `python scripts/live_studionet.py --verify-only`: confirmed effective RPC `https://studio.genlayer.com/api`, alias `studionet`, actual chain ID `61999`.
- `python scripts/preflight.py --final`: PASS (static manifest and repository checks; it does not itself verify chain receipts).

Current stable Studionet deployments: MeritCircuit `0x0dA56CfDDc73442247456C095A368187a557F446` (deployment tx `0xff52ae69df8126211893bb33e2a25f7d3104b6b1a8358ab1829d48487766d1c4`) and MeritAwardGate `0x74cFFb3AECD829C6280bb7647E7Fc17Ef560aEF2` (deployment tx `0x703801fda192f72c4f50d15657da3c97c2ea0a25ac60da36ead4076de6b6f859`). The deployed MeritCircuit source corresponds to commit `147c74c89fad7f4f99aa753160911f6ca6a30f28`.

Selection 1 is preserved in `deployments/attempt_5.json` at definition hash `98188e8cf9b721d1a8f514700e23c34fc797b7dd8c1bcf011bb97042d379a656`. Two of three pairs finalized; pair 1–3 criterion 2 returned `INDETERMINATE` on three finalized attempts with `mirrored verdict inconsistency`. One intervening retry transaction was canceled with `NO_MAJORITY` and did not count as an assessment. That selection has no complete matrix, ranking hash, or certified winner and was not retried or modified.

Fresh selection 3 uses all three immutable synthetic sources with a focused implementation/integration-evidence rubric. It finalized three actual consensus assessments and all three pairs, then ranked `[3, 1, 2]`. Pair margins are 1–2 `+100`, 1–3 `−100`, and 2–3 `−100`; candidate 3 is the strict Condorcet winner. Its definition hash is `20b2e6e358dac1f2af68cb48a28126bfa81f144a320af4a1efbd49d8246495c5` and ranking hash is `f307162ec17b9465e31e63d7fbec3d395ae5564c88000d1705af8871b44d9cd6`. Typed award success and all five expected rejection probes finalized. See the complete evidence in `deployments/studionet.json`; the reproducible runner is `scripts/run_studionet_full_lifecycle.py`. Selection 2 remains an additional two-candidate consumer demonstration in `deployments/award_scenario.json`.

Earlier deployment and gate probe evidence is retained under `deployments/attempt_1.json` through `attempt_4.json` and `deployments/attempt_4_gate_probe.json`. The user-provided test keys were used only in temporary process environments and are not in the repository; because they were shared in chat, retire those wallets after sweeping remaining funds.

The live protocol was not blocked by GenLayer: the first selection reached its required fail-closed result, while a fresh three-candidate selection completed and demonstrated the lifecycle. The remaining blocker is publishing the latest local commit: GitHub returned HTTP 403, `Permission to BeatyXO/MeritCircuit.git denied to Ifem1`. The repository owner must grant that identity write access or provide an authenticated account with access. The supplied test-wallet keys were used only through temporary process environments and should be retired after funds are swept.
