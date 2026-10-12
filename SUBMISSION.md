# Submission readiness

**Implementation and local tests verified; live submission evidence remains incomplete.** Repository: [BeatyXO/MeritCircuit](https://github.com/BeatyXO/MeritCircuit), branch `main`.

The reusable pairwise qualitative ranking Intelligent Contract performs consensus-backed, source-grounded criterion comparisons, constructs the complete weighted margin matrix, applies deterministic Ranked Pairs with cycle detection, and produces a hash-pinned result. `MeritAwardGate` is a typed, replay-protected downstream consumer. There is no frontend, native token payout, or offchain ranking service.

The implementation and fixtures were pushed. Fixture commit: `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5`. The demo pins all three evidence URLs to that commit. The pinned-reference commit is `5c6ac8114fd41bcc4865476dafaa19b36b3bddbc`.

Verified locally: 39 offline protocol tests, 6 GenLayer Direct Mode tests, 45 total pytest tests, Python compilation, and static preflight. Direct Mode independently re-evaluates adversarial leader outputs. The stable SDK read-only check confirmed `studionet`, RPC `https://studio.genlayer.com/api`, and actual chain ID `61999`.

No Studionet deployments or live writes are recorded. The deployer and separate unauthorized-account signing keys were absent, so there is no actual consensus-backed comparison, certified winner, typed onchain consumer success, rejection evidence, transaction, address, or explorer proof. `python scripts/preflight.py --final` therefore correctly fails until those observations exist. Do not report a live winner or deployment until then.

See `docs/REVIEWER_DEMO.md`, `DEPLOYMENT.md`, and `BUILD_STATUS.md` for commands, current evidence, and outstanding live acceptance criteria.
