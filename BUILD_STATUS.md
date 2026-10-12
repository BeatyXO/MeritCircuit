# Handoff build status (2026-10-12)

**Status: IMPLEMENTED AND TESTED LOCALLY — NOT DEPLOYED OR PUSHED.**

At ZIP creation, the package contains two Intelligent Contracts, a bounded deterministic pairwise tournament, custom independently grounded validator function, synthetic public-web fixture inputs (requiring immutable Git commit pinning), unit tests, a real GenLayer Direct Mode test module requiring optional `gltest`, CI, configuration, and a strict live-evidence manifest.

Observed in the local build environment:

- `python scripts/preflight.py`: **PASS** (static preflight only).
- `python -m compileall -q contracts tests scripts`: **PASS**.
- `python -m pytest -q tests/test_merit_circuit.py`: **39 passed**. These offline protocol tests use a mock GenLayer harness.
- `python -m pytest -q tests/direct/`: **6 passed** with `genlayer-test 0.29.2`, `genlayer-py 0.16.3`, and stable GenVM runner `v0.2.16`. These are Direct Mode tests, not multi-validator network consensus.
- Direct Mode independently re-ran the verifier and rejected a changed semantic result and forged leader evidence.
- `python -m compileall -q contracts tests scripts`: **PASS**.
- `python scripts/preflight.py`: **PASS (static handoff checks only)**.
- `python scripts/preflight.py --final`: **FAIL (expected)** because immutable public fixture commit SHA has not been pinned and no live deployment evidence exists.
- Stable Studionet chain probe: **BLOCKED** by sandbox network denial (`WinError 10013`); no write was attempted.
- GitHub remote read: **PASS** for `https://github.com/BeatyXO/MeritCircuit.git`; the remote is empty. Initial implementation commit and push remain pending.
- `python scripts/check_studionet.py`: **BLOCKED** by HTTP 403 from the endpoint's direct `eth_chainId` method.
- `python scripts/live_studionet.py --verify-only`: **PASS**; stable SDK confirmed effective RPC `https://studio.genlayer.com/api` and actual chain ID `61999` (read-only, no signed transaction).
- Live writes: **NOT ATTEMPTED**; neither the deployer nor separate unauthorized-account key is present in the environment.
- Direct Mode reported a Windows cleanup defect in `genlayer-test 0.29.2`; `tests/direct/conftest.py` defers those temporary-file unlinks until runner teardown.
- `scripts/live_studionet.py` is implemented against the installed stable SDK API. It has not been run against the RPC and does not constitute deployment evidence.

The agent must run real Direct Mode and Studionet tests before claiming review readiness. Details in `MERITCIRCUIT_AGENT_PROMPT.md`.
