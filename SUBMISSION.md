# Submission readiness

**Code, tests, and a real typed award lifecycle are verified; final acceptance remains conditional because the required three-candidate selection could not complete its matrix.** Repository: [BeatyXO/MeritCircuit](https://github.com/BeatyXO/MeritCircuit), branch `main`.

MeritCircuit is a reusable Intelligent Contract primitive with source-grounded pairwise comparisons, deterministic weighted margins and Ranked Pairs, immutable ranking certificates, and strict Condorcet winner certification. MeritAwardGate makes a typed cross-contract view call and enforces owner authorization, both pinned hashes, candidate eligibility, and replay protection. There is no frontend or token transfer.

The immutable synthetic fixture commit is `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5`. Local checks: 40 offline protocol tests, 6 Direct Mode tests, 54 total pytest tests, Python compilation, and static preflight all pass. Stable Studionet RPC and actual chain ID 61999 were verified.

Selection 1 has three candidates and two criteria. It finalized 2/3 pairs, but pair 1–3 criterion 2 remained `INDETERMINATE` / `mirrored verdict inconsistency` after the three-attempt cap. It has no ranking or winner. The separate selection 2 demonstration is explicitly two-candidate: it has ranking hash `2deec450bc40aa3cb3ab0c8695240c9223ec028f58ea833b9f7347cb9535e426`, certified candidate 1, a successful typed award, and finalized wrong-definition, wrong-ranking, losing-candidate, replay, and unauthorized-caller rejections. These results do not substitute for selection 1's incomplete matrix.

`python scripts/preflight.py --final` remains failing because it requires a complete ranking and consumer proof for the primary three-candidate manifest. Do not claim full submission readiness or a winner for selection 1. See `BUILD_STATUS.md`, `DEPLOYMENT.md`, `deployments/studionet.json`, and `deployments/award_scenario.json` for evidence.
