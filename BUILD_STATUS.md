# Build status (2026-10-13)

**Implementation and local tests complete; no live lifecycle has completed.** The requested repository is pushed to `https://github.com/BeatyXO/MeritCircuit` on `main`. The fixture-containing commit is `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5`; its three raw GitHub URLs returned HTTP 200. The demo selection pins those immutable commit URLs, first committed in `5c6ac8114fd41bcc4865476dafaa19b36b3bddbc`.

Observed results:

- `python scripts/preflight.py`: **PASS** (static handoff checks).
- `python -m compileall -q contracts tests scripts`: **PASS**.
- `python -m pytest -q tests/test_merit_circuit.py`: **39 passed**.
- `python -m pytest -q tests/direct/`: **6 passed** using `genlayer-test 0.29.2`, `genlayer-py 0.16.3`, and GenVM runner `v0.2.16`. Direct Mode independently re-evaluated the verifier and rejected altered semantic results and forged leader evidence.
- `python -m pytest -q`: **51 passed**, including stable-SDK receipt, mirror-failure diagnostic, and whitespace-only anchoring checks.
- `python scripts/live_studionet.py --verify-only`: **PASS**, stable SDK confirmed effective RPC `https://studio.genlayer.com/api` and actual chain ID `61999`. Read-only; no transaction was signed or broadcast.
- First live attempt deployed both contracts and created/sealed a selection, then failed at comparison event emission with `SystemError: 2: inval`. Stable-runtime trace showed the event exceeded the indexed-topic limit. Evidence is preserved in `deployments/attempt_1.json`.
- The corrected event and typed `CalldataAddress` gate constructor deployed successfully. A second selection was created/sealed and actual consensus-backed comparisons ran. Candidate pair 1–2, criterion 1, produced `INDETERMINATE` on all three bounded attempts; no pair or ranking was finalized. Evidence is preserved in `deployments/attempt_2.json`.
- A third deployment with safe mirror-failure diagnostics produced the specific reason `non-verbatim evidence anchor` after three real attempts. It also stopped without finalizing a pair. Evidence is in `deployments/attempt_3.json`.
- The latest source canonicalizes whitespace only when checking evidence spans (newlines and runs of whitespace), preserving every other character and rejecting paraphrases. Its retry cap remains three. This fix needs a fresh immutable deployment; the active manifest has been reset to `NOT_DEPLOYED` and stores no superseded address as current evidence.
- `python scripts/preflight.py --final`: remains **FAIL** until a corrected deployment produces a complete matrix, ranking, and required consumer evidence.

All deployed instances to date are superseded; no complete ranking or typed cross-contract award lifecycle is proven. No winner or successful award is claimed. The user supplied two funded test wallets and authorized the live lifecycle; key material was used only in process environment variables and was not written into the repository. The pinned stable SDK lacks `estimate_transaction_fees`; deployment instructions use its stable transaction API rather than switching networks or SDK channels.

The complete live acceptance criteria remain in `MERITCIRCUIT_AGENT_PROMPT.md` and `DEPLOYMENT.md`. Do not change the required stable Studionet identity or populate the evidence manifest with unobserved results.
