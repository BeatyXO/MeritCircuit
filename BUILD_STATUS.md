# Build status (2026-10-13)

**Implementation and local tests complete; corrected stable Studionet lifecycle is in progress.** The requested repository is pushed to `https://github.com/BeatyXO/MeritCircuit` on `main`. The fixture-containing commit is `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5`; its three raw GitHub URLs returned HTTP 200. The demo selection pins those immutable commit URLs, first committed in `5c6ac8114fd41bcc4865476dafaa19b36b3bddbc`.

Observed results:

- `python scripts/preflight.py`: **PASS** (static handoff checks).
- `python -m compileall -q contracts tests scripts`: **PASS**.
- `python -m pytest -q tests/test_merit_circuit.py`: **39 passed**.
- `python -m pytest -q tests/direct/`: **6 passed** using `genlayer-test 0.29.2`, `genlayer-py 0.16.3`, and GenVM runner `v0.2.16`. Direct Mode independently re-evaluated the verifier and rejected altered semantic results and forged leader evidence.
- `python -m pytest -q`: **49 passed**, including four stable-SDK receipt normalization checks.
- `python scripts/live_studionet.py --verify-only`: **PASS**, stable SDK confirmed effective RPC `https://studio.genlayer.com/api` and actual chain ID `61999`. Read-only; no transaction was signed or broadcast.
- Initial live attempt deployed MeritCircuit and MeritAwardGate on Studionet, created/sealed a selection, then failed at comparison event emission with `SystemError: 2: inval`. Stable-runtime trace showed `ComparisonRecorded` had four indexed fields plus the event topic. The record is preserved at `deployments/attempt_1.json`; this version is superseded and has no finalized ranking or award.
- Fixed the event to keep three indexed fields and put `criterion_id` in its data blob. Also fixed the stable SDK receipt parser and typed constructor calldata (`CalldataAddress`) after observing actual RPC receipts. The corrected source is being redeployed as a new lifecycle because deployed contract code is immutable.
- `python scripts/preflight.py --final`: remains **FAIL** until corrected deployment and full finalized lifecycle evidence are recorded.

The first deployed contract instances are superseded; no corrected-version ranking or typed cross-contract award lifecycle is yet proven. No winner or successful award is claimed. The user supplied two funded test wallets and authorized the live lifecycle; key material is used only in process environment variables and is not written into the repository. The pinned stable SDK lacks `estimate_transaction_fees`; deployment instructions use its stable transaction API rather than switching networks or SDK channels.

The complete live acceptance criteria remain in `MERITCIRCUIT_AGENT_PROMPT.md` and `DEPLOYMENT.md`. Do not change the required stable Studionet identity or populate the evidence manifest with unobserved results.
