# MeritCircuit — Consensus-grounded pairwise ranking primitive

**Standalone GenLayer Intelligent Contract. No frontend.**

MeritCircuit certifies bounded, qualitative comparison tournaments. It does **not** ask an LLM to rank candidates or pick an award recipient. Validators independently obtain each candidate's frozen source, judge a **single pair / single criterion** in both display orders, check exact grounding quotes, and agree on an enum. The contract aggregates the judgments deterministically using weighted margins and Ranked Pairs, with cycle handling and identity-bound result hashes.

The user-facing metaphor: five grant proposals cannot be reliably ordered from a single unconstrained language-model ranking. MeritCircuit instead creates a frozen rubric and all required pair comparisons; the final ordering follows code, not an LLM.

## What is implemented

- `contracts/merit_circuit.py`: sealed candidate/criterion lifecycle; score-budget invariants; source-host pinning; custom leader/validator independent source reads; mirrored-prompt check; bounded retries; immutable audit attempts; weighted pair summaries; cycle-safe Ranked Pairs; pinned result certificate; strict-Condorcet-winner eligibility.
- `contracts/merit_award_gate.py`: a **real typed interface** to another Intelligent Contract and owner-only, replay-protected award records (no fund transfers).
- `tests/test_merit_circuit.py`: self-contained deterministic offline protocol tests with simulated GenLayer APIs, **not real Direct Mode**.
- `tests/direct/test_stable_direct.py`: GenLayer Testing Suite Direct Mode checks for contract behavior and independent validator re-evaluation.
- `fixtures/`: clearly marked **synthetic** example proposals; the live selections reference immutable raw GitHub URLs pinned to a commit.
- `scripts/`: static preflight, immutable fixture pinning, read-only network probes, and checkpointed stable-SDK lifecycle runners.
- `docs/`, `DEPLOYMENT.md`, `SUBMISSION.md`, `deployments/studionet.json`: architecture, adversarial model, and honest evidence requirements.

## Network is non-negotiable

**Stable Studionet**: `studionet`, chain ID **61999**, RPC **https://studio.genlayer.com/api**. Never substitute the release-candidate preview. First verify the effective chain before *every* live deployment or write.

## Contract lifecycle

1. `create_selection(title,purpose,source_host)` called by selection owner.
2. `add_criterion(selection_id,name,rubric,weight)` — 1–6 criteria; weights must total **100**.
3. `add_candidate(selection_id,name,summary,evidence_url)` — 2–8 candidates, HTTPS evidence from the chosen host.
4. `seal_selection(selection_id)` — freezes the complete description, rubric, weights, candidate identities and URLs into `definition_hash`.
5. `assess_pair_criterion(selection_id,left_id,right_id,criterion_id,expected_definition_hash)` — permissionless, only `left_id < right_id`; consensus on **LEFT/RIGHT/TIE/INDETERMINATE**; 3-attempt cap only for inconclusive outcomes.
6. `finalize_pair(...)` — requires every criterion on that pair to be decisive (LEFT/RIGHT/TIE), aggregates weights to signed integer margin.
7. `finalize_ranking(selection_id,expected_definition_hash)` — requires all `n(n−1)/2` pairs complete, creates immutable `ranking_hash`, and the deterministic ranking.
8. Consumer calls `is_ranked_winner(selection_id,candidate_id,definition_hash,ranking_hash)`; award gate enforces the proof and replay protections.

The final ranking is **always deterministic** after the matrix is complete, including cycles or exact pair ties. However, a consumer may only treat the top candidate as **award-certifiable** if that candidate **strictly wins every head-to-head weighted comparison** (Condorcet winner). Cycles, zero margins and tied top rankings can still have a deterministic ordering but do **not** grant award eligibility. `get_result()` includes `winner_certified`.

## Deterministic scoring

For pair (A,B), criterion j weight `w_j` (integer percentage):

- `LEFT`: +w_j;
- `RIGHT`: −w_j;
- `TIE`: 0;
- `INDETERMINATE`: blocks finalization until retried successfully, up to the fixed cap.

`margin(A,B) = sum_j(+w_j or −w_j or 0)`.

Nonzero weighted margins become directed pairwise victories. Ranked Pairs locks victories in descending **absolute margin**, then descending support weight, then ascending winner/loser IDs. Edges that would create a directed cycle are skipped. A topological traversal returns the order with an ascending-candidate-ID tie break for incomparable nodes. **Candidate ID is not a merit signal**, merely an explicit deterministic tie break. The certificate includes all pair rows, locked/skipped edges and winner-certification flag.

## Local verification

```bash
python scripts/preflight.py
python -m compileall -q contracts tests scripts
python -m pytest -q tests/test_merit_circuit.py
python -m pytest -q tests/direct/
```

The offline suite uses a mock GenLayer harness; Direct Mode executes contract logic in-memory and invokes an independent verifier, but neither establishes network consensus or deployment. The verified local result is 54 passing pytest tests, including 6 Direct Mode tests with independent verifier re-evaluation. On stable Studionet, selection 3 completed all three consensus comparisons, finalized its full matrix and ranking, certified candidate 3, and recorded a successful typed gate award plus finalized wrong-definition, wrong-ranking, losing-candidate, replay, and unauthorized-caller rejections. The original selection 1 remains archived as `INDETERMINATE` after its three-attempt mirrored-verdict cap; it has not been altered or ranked. Selection 2 is a separate two-candidate consumer demonstration. See `deployments/studionet.json`, `deployments/attempt_5.json`, and `deployments/award_scenario.json`.

## Immutable fixture workflow

`demo/selection.json` pins `/fixtures/{alpha,beta,gamma}.md` to the pushed fixture commit `233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5`. Each immutable GitHub raw URL was verified to return HTTP 200. The workflow used to establish this pin was:

```bash
python scripts/pin_fixture_commit.py <FULL_40_HEX_FIXTURE_COMMIT>
```

The pinned demo JSON is committed and pushed. The pinned URLs identify immutable source documents; onchain execution evidence is recorded separately in the deployment manifests. `demo/selection_live_lifecycle.json` is the input used for completed selection 3.

## Limitations explicitly acknowledged

- Qualitative preference is contextual and can be biased despite mirrored order and consensus. A verdict does not establish objective human merit.
- Public web evidence is untrusted. Source text may be adversarial. Domain pinning is not equivalent to cryptographic verification of remote content; use immutable content-addressed URLs where possible.
- A frozen source **URL** is not necessarily a frozen web document. The example uses immutable commit-pinned raw GitHub URLs after first push.
- A maximum of 8 candidates limits costs and makes tournament graph algorithms bounded. The worst-case 8-candidate/6-criterion evaluation requires 168 semantic consensus calls, each with mirrored prompts and independent validator reading: expensive by design. The live demo should use 3 candidates and 2 criteria.
- At creation time the contract owner selects the candidate IDs and tie-break order; an adversarial owner can exploit exact ties, so **no award is certified in the absence of a strict winner**.
- Tests with simulated APIs do not confirm chain behavior. Deployment manifests distinguish finalized onchain results from archived incomplete attempts.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/INVARIANTS.md`](docs/INVARIANTS.md), [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md), [`docs/REVIEWER_DEMO.md`](docs/REVIEWER_DEMO.md).

The completed Studionet lifecycle uses ephemeral test-wallet environment variables; never put keys in the repository. The SDK identity check confirmed the stable alias and actual chain ID, and the lifecycle runner repeats that check immediately before each write. Selection 3 supplies the complete three-candidate matrix, certified winner, and consumer proof. Selection 1's capped INDETERMINATE outcome remains archived without a fabricated ranking. `python scripts/preflight.py --final` passes against the verified selection 3 evidence. The test-wallet keys shared in the task should be swept and retired.
