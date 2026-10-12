# Submission readiness

**Implementation and local tests verified; live submission evidence remains incomplete.** Repository: [BeatyXO/MeritCircuit](https://github.com/BeatyXO/MeritCircuit), branch `main`.

The reusable pairwise qualitative ranking Intelligent Contract performs consensus-backed, source-grounded criterion comparisons, constructs the complete weighted margin matrix, applies deterministic Ranked Pairs with cycle detection, and produces a hash-pinned result. `MeritAwardGate` is a typed, replay-protected downstream consumer. There is no frontend, native token payout, or offchain ranking service.

The implementation and fixtures were pushed. Fixture commit: `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5`. The demo pins all three evidence URLs to that commit. The pinned-reference commit is `5c6ac8114fd41bcc4865476dafaa19b36b3bddbc`.

Verified locally: 39 offline protocol tests, 6 GenLayer Direct Mode tests, 45 total pytest tests, Python compilation, and static preflight. Direct Mode independently re-evaluates adversarial leader outputs. The stable SDK read-only check confirmed `studionet`, RPC `https://studio.genlayer.com/api`, and actual chain ID `61999`.

An initial Studionet attempt deployed both contracts and created/sealed a selection, but the first comparison reverted during event emission. Those actual hashes and addresses are recorded as a superseded attempt in `deployments/attempt_1.json`; the contract event schema and SDK receipt handling have since been fixed, and the corrected immutable contracts are being deployed. There is not yet a corrected-version ranking, certified winner, typed onchain award success, or complete rejection evidence. `python scripts/preflight.py --final` correctly fails until the lifecycle completes. Do not report a winner or successful award until then.

See `docs/REVIEWER_DEMO.md`, `DEPLOYMENT.md`, and `BUILD_STATUS.md` for commands, current evidence, and outstanding live acceptance criteria.
