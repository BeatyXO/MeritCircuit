# Submission readiness

**Implementation and adversarial live tests verified; live submission evidence remains incomplete because one pair exhausted its bounded retries.** Repository: [BeatyXO/MeritCircuit](https://github.com/BeatyXO/MeritCircuit), branch `main`.

The reusable pairwise qualitative ranking Intelligent Contract performs consensus-backed, source-grounded criterion comparisons, constructs the complete weighted margin matrix, applies deterministic Ranked Pairs with cycle detection, and produces a hash-pinned result. `MeritAwardGate` is a typed, replay-protected downstream consumer. There is no frontend, native token payout, or offchain ranking service.

The implementation and fixtures were pushed. Fixture commit: `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5`. The demo pins all three evidence URLs to that commit. The pinned-reference commit is `5c6ac8114fd41bcc4865476dafaa19b36b3bddbc`.

Verified locally: 39 offline protocol tests, 6 GenLayer Direct Mode tests, 52 total pytest tests, Python compilation, and static preflight. Direct Mode independently re-evaluates adversarial leader outputs. The stable SDK read-only check confirmed `studionet`, RPC `https://studio.genlayer.com/api`, and actual chain ID `61999`.

Earlier Studionet attempts are archived in `deployments/attempt_1.json` through `attempt_3.json`. The current contracts are MeritCircuit `0x2e3bda43a3E0e983D365B92A5387368Cf93233b0` and MeritAwardGate `0x47a70B6828c1465612cE008bdE7E2Ec04Ac6512C`. Selection 1 is sealed with definition hash `98188e8cf9b721d1a8f514700e23c34fc797b7dd8c1bcf011bb97042d379a656`. One of three pairs finalized at +100; pair 1–3 criterion 1 returned `INDETERMINATE` / `unparseable classification` in three attempts. There is no complete matrix, ranking, strict winner, or successful award. Real typed gate transactions rejected an uncertified candidate and unauthorized caller; the evidence is in `deployments/gate_probe.json`. Wrong-definition, wrong-ranking, losing-candidate, and replay rejection remain unproven because no ranking was finalized. `python scripts/preflight.py --final` correctly fails until the lifecycle has complete evidence. Do not report a winner or successful award.

See `docs/REVIEWER_DEMO.md`, `DEPLOYMENT.md`, and `BUILD_STATUS.md` for commands, current evidence, and outstanding live acceptance criteria.
