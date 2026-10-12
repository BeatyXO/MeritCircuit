# Submission readiness

**Implementation and local tests verified; live submission evidence remains incomplete.** Repository: [BeatyXO/MeritCircuit](https://github.com/BeatyXO/MeritCircuit), branch `main`.

The reusable pairwise qualitative ranking Intelligent Contract performs consensus-backed, source-grounded criterion comparisons, constructs the complete weighted margin matrix, applies deterministic Ranked Pairs with cycle detection, and produces a hash-pinned result. `MeritAwardGate` is a typed, replay-protected downstream consumer. There is no frontend, native token payout, or offchain ranking service.

The implementation and fixtures were pushed. Fixture commit: `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5`. The demo pins all three evidence URLs to that commit. The pinned-reference commit is `5c6ac8114fd41bcc4865476dafaa19b36b3bddbc`.

Verified locally: 39 offline protocol tests, 6 GenLayer Direct Mode tests, 45 total pytest tests, Python compilation, and static preflight. Direct Mode independently re-evaluates adversarial leader outputs. The stable SDK read-only check confirmed `studionet`, RPC `https://studio.genlayer.com/api`, and actual chain ID `61999`.

Two actual Studionet attempts are archived in `deployments/attempt_1.json` and `deployments/attempt_2.json`. The first found an event-topic runtime error; the second deployed the corrected event schema and typed gate, then correctly stopped after three `INDETERMINATE` results for one criterion. No pair matrix or ranking was finalized. The latest safe prompt diagnostics require a fresh immutable contract deployment. There is no certified winner, typed onchain award success, or complete rejection evidence. `python scripts/preflight.py --final` correctly fails until the lifecycle completes. Do not report a winner or successful award until then.

See `docs/REVIEWER_DEMO.md`, `DEPLOYMENT.md`, and `BUILD_STATUS.md` for commands, current evidence, and outstanding live acceptance criteria.
