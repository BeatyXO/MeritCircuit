# Build status (2026-10-13)

**Implementation and local tests complete; stable Studionet lifecycle not deployed.** The requested repository is pushed to `https://github.com/BeatyXO/MeritCircuit` on `main`. The fixture-containing commit is `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5`; its three raw GitHub URLs returned HTTP 200. The demo selection now pins those immutable commit URLs, committed in `5c6ac8114fd41bcc4865476dafaa19b36b3bddbc`.

Observed results:

- `python scripts/preflight.py`: **PASS** (static handoff checks).
- `python -m compileall -q contracts tests scripts`: **PASS**.
- `python -m pytest -q tests/test_merit_circuit.py`: **39 passed**.
- `python -m pytest -q tests/direct/`: **6 passed** using `genlayer-test 0.29.2`, `genlayer-py 0.16.3`, and GenVM runner `v0.2.16`. Direct Mode independently re-evaluated the verifier and rejected altered semantic results and forged leader evidence.
- `python -m pytest -q`: **45 passed**.
- `python scripts/live_studionet.py --verify-only`: **PASS**, stable SDK confirmed effective RPC `https://studio.genlayer.com/api` and actual chain ID `61999`. Read-only; no transaction was signed or broadcast.
- `python scripts/preflight.py --final`: **FAIL**, correctly, because live deployment addresses and finalized lifecycle evidence are absent.

No contract has been deployed and no live lifecycle, consensus comparison, ranking, typed cross-contract consumer call, rejection transaction, or explorer evidence is claimed. `GENLAYER_PRIVATE_KEY` and `GENLAYER_UNAUTHORIZED_PRIVATE_KEY` were both absent, so live writes were not attempted. The pinned stable SDK also lacks `estimate_transaction_fees`; deployment instructions use its stable transaction API rather than switching networks or SDK channels.

The complete live acceptance criteria remain in `MERITCIRCUIT_AGENT_PROMPT.md` and `DEPLOYMENT.md`. Do not change the required stable Studionet identity or populate the evidence manifest with unobserved results.
