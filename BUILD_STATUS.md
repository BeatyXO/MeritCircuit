# Build status (2026-10-13)

**Implementation and adversarial live testing are complete; the live lifecycle is intentionally incomplete.** Repository: `https://github.com/BeatyXO/MeritCircuit`, branch `main`. Fixture commit: `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5`; all three raw GitHub URLs returned HTTP 200.

Observed results:

- `python scripts/preflight.py`: **PASS** (static handoff checks).
- `python -m compileall -q contracts tests scripts`: **PASS**.
- `python -m pytest -q tests/test_merit_circuit.py`: **39 passed**.
- `python -m pytest -q tests/direct/`: **6 passed** using `genlayer-test 0.29.2`, `genlayer-py 0.16.3`, and GenVM runner `v0.2.16`. Direct Mode independently re-evaluated the verifier and rejected altered semantic results and forged leader evidence.
- `python -m pytest -q`: **52 passed**, including stable-SDK receipt, mirror-failure diagnostic, and whitespace-only anchoring checks.
- `python scripts/live_studionet.py --verify-only`: **PASS**, stable SDK confirmed effective RPC `https://studio.genlayer.com/api` and actual chain ID `61999`. Read-only; no transaction was signed or broadcast.
- Earlier failed deployments and comparison attempts remain in `deployments/attempt_1.json` through `attempt_3.json`.
- Current deployed MeritCircuit `0x2e3bda43a3E0e983D365B92A5387368Cf93233b0` and MeritAwardGate `0x47a70B6828c1465612cE008bdE7E2Ec04Ac6512C` were deployed on Studionet 61999. Selection 1 was created and sealed with definition hash `98188e8cf9b721d1a8f514700e23c34fc797b7dd8c1bcf011bb97042d379a656`.
- Pair 1–2 finalized at margin +100 (A support 100, B support 0). Pair 1–3 criterion 1 returned `INDETERMINATE` with `unparseable classification` in all three allowed attempts. The complete matrix, ranking hash, and certified winner do not exist; further retries would violate the bounded protocol.
- Real typed gate calls rejected an uncertified candidate (`0xf1e775d7e872549fa8d4a8656517afc653de0d2b439efa027d4e8612217e1272`) and an unauthorized caller (`0x2b252f7c8cb7ead4d123c3f6b7e0b5607480f39e75d944056f0204cf508a7646`). Details and errors are preserved in `deployments/gate_probe.json`. There is no observed positive award, replay rejection, wrong-definition rejection, wrong-ranking rejection, or losing-candidate rejection because no ranking was finalized.
- `python scripts/preflight.py --final`: remains **FAIL** until a corrected deployment produces a complete matrix, ranking, and required consumer evidence.

No winner or successful award is claimed. The user authorized funded test wallets; key material was used only in process environment variables and was not written into the repository. The pinned stable SDK lacks `estimate_transaction_fees`; deployment instructions use its stable transaction API rather than switching networks or SDK channels.

The complete live acceptance criteria remain in `MERITCIRCUIT_AGENT_PROMPT.md` and `DEPLOYMENT.md`. Do not change the required stable Studionet identity or populate the evidence manifest with unobserved results.
