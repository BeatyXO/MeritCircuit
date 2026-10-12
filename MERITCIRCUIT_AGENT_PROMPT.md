# MeritCircuit — coding agent takeover and finish prompt

You are taking over a **substantially implemented** standalone GenLayer Intelligent Contract repository named **MeritCircuit**. The user has given you its ZIP contents in the existing working folder. **Do not return only a plan, checklist, commentary, mockup, or partial scaffold.** Inspect the *entire* unzipped repository first, then **finish it in place**, test it thoroughly, deploy and verify on the correct live network, and push the completed work to:

**https://github.com/BeatyXO/MeritCircuit.git**

The repository is newly created and initially empty. Do not push to another owner or repo, and do not invent a successful push if authentication or permissions fail. **The final result must be the implemented, tested, audited codebase and an evidence-backed handoff, not prose alone.**

## Product boundary — non-negotiable

MeritCircuit is a **standalone reusable Intelligent Contract primitive**, not a website or full application. **NO FRONTEND.** It manages a fixed, sealed qualitative selection tournament:

- The creator declares the selection purpose and rubric criteria; 1–6 criteria must have positive integer weights totaling exactly 100.
- The creator registers 2–8 candidates and each candidate's bounded description and source URL; HTTPS source host is frozen at selection creation.
- Sealing commits the complete definition to an immutable `definition_hash`.
- For each canonical candidate pair `(a,b)` where `a<b` and each criterion, independent GenLayer validators fetch each candidate's **registered** source and evaluate only that pair against only that rubric.
- Qualitative outcomes are `LEFT`, `RIGHT`, `TIE`, `INDETERMINATE`. **Never** allow the LLM to rank the full set, change weights, rewrite the rubric, select the final winner, invoke contract side effects, or determine certificate validity.
- A decisive semantic result must be grounded by short exact quoted spans in both independently rendered source texts. The validator must **independently re-fetch/re-evaluate** sources and reject a leader's forged quotes or incompatible decision. The model is run in **both candidate display orders** with consistent normalized results; order instability must not be silently accepted.
- Malformed responses, mismatched mirror results, unavailable sources and ambiguous criteria fail closed. At most three **INDETERMINATE** attempts may be made per `(pair,criterion)`; every attempt has immutable history. Definitive results are immutable.
- A pair can finalize only when every criterion has `LEFT/RIGHT/TIE`. Weighted margins and the pair matrix are **deterministic**. Full ranking requires every pair to finalize.
- Compute the ranking with **deterministic Ranked Pairs (Tideman)**: sort wins by descending margin, deterministic secondary support/ID rules; skip cycle-creating edges; topological result with explicit ID tie break. Never reintroduce AI into cycle-breaking or sorting.
- An ordered list is NOT automatically an award certificate. A **strict Condorcet winner** (head-to-head positive margin against every other candidate) must exist for `winner_certified=true` and for a downstream authorized award. Ties and cycles still produce an auditable deterministic ordering but **must not certify a winner without a strict positive head-to-head proof**. Don't weaken this for the demo.
- Freeze `ranking_hash` over the sealed definition, pair rows, rank order, locked/skipped edges, and strict-winner flag.
- `MeritAwardGate` proves actual IC-to-IC reuse: typed view call to `is_ranked_winner(selection_id,candidate_id,expected_definition_hash,expected_ranking_hash)` on the deployed MeritCircuit address. Gate operations must be owner-only, fail on stale/wrong hashes or losing/noncertified candidate, and reject replay of `action_hash`. Gate only records an approved operation; **no token transfer or frontend**.

**Do not collapse MeritCircuit into “AI scores/ranks grants.”** Its reusable protocol is **consensus-grounded pairwise comparative judgments → deterministic weighted tournament → immutable result certificate → strict-winner downstream authorization**. Keep the design architecture unless actual GenVM/runtime failures require narrowly justified change. Resist replacing proper validators with simple self-asserted JSON or mock-only results.

## Network: ABSOLUTELY FIXED

**Stable Studionet ONLY**:

- Alias: `studionet`
- Chain ID: **61999**
- RPC: **https://studio.genlayer.com/api**
- Explorer: **https://explorer-studio.genlayer.com**

Do not deploy on development preview, Studio-dev, Asimov, localnet, or a remapped chain ID and claim the target was reached. For each live deployment or write workflow, confirm the **effective** network RPC and the **actual** chain ID with a supported stable SDK/CLI operation before broadcasting. If the read-only probe `scripts/check_studionet.py` is unsupported by the endpoint, check with the stable SDK and explicitly document the working verification method. If RPC/fees/provider/authentication block verification, report the blocker; never switch networks or fabricate receipts.

## Required work, in order

1. List the entire repository tree and **read every file**: README, SUBMISSION, DEPLOYMENT, docs/, all contracts, tests, fixtures, scripts, CI, manifests and this prompt. Record any build assumptions and evidence gaps, then continue working rather than stopping after a plan.
2. Immediately run `python scripts/preflight.py` and `python -m compileall -q contracts tests scripts`. Install the pinned stable test tooling in `requirements-test.txt`; do not silently swap in release-candidate libraries.
3. Run the offline protocol tests: `python -m pytest -q tests/test_merit_circuit.py`. These simulate GenLayer APIs; **they are not genuine GenLayer Direct Mode**. Run actual GenLayer `Direct Mode` tests: `python -m pytest -q tests/direct/` with installed `genlayer-test` (currently seeded in `tests/direct/test_stable_direct.py`). Expand/fix Direct Mode tests until **all tests that should run actually execute and pass**, without skip-based fakery or weakening assertions. Use current stable SDK syntax if it differs from the initial handoff. Verify storage `TreeMap`/`@allow_storage` dataclasses, event syntax, `gl.nondet.web.render`, `gl.nondet.exec_prompt`, custom `gl.vm.run_nondet_unsafe`, `Keccak256`, result calldata and typed contract interface.
4. Deep-audit the protocol for source URL security, untrusted web instructions, leading candidate/position bias, mirrored presentation normalization, malformed JSON, anchored source quotes, leader/validator independence, bounded reads, and source namespace freeze. No transaction-supplied replacement URL may override the sealed candidate URL. Ensure validator checks the **leader's decisive quoted spans against validator-fetched content**, not just its own quotes. Preserve `INDETERMINATE` rather than guessing.
5. Deep-audit deterministic logic: integer weights and ranges; sum=100; immutable sealed definition; canonical `a<b` pair identity; array/mapping storage persistence; no double pair completion; complete matrix required; correct signed margin; ranked-pairs strength sorting; no cycles in locked graph; deterministic topological ordering; winner certification only when strictly beating **all** opponents; domain-separated hashes; never trust caller-supplied winner/ranking. Verify no integer overflow or unbounded loops within 8×6 caps.
6. Deep-audit authorization, cross-contract semantics and replay protections. Run actual Direct Mode typed IC-to-IC consumer tests (not only a local fake adapter). Verify a correct award succeeds and each invalid form fails. Check that replay protection is written atomically with award issuance and cannot be bypassed by wrong action hash formatting.
7. Add adversarial tests beyond the supplied baseline: owner spoofing, invalid candidate counts, 0/negative/overflow weights, total=99/101, source-host/URL tricks including credentials and ports, source substitution post-seal, stale `definition_hash`, forged leader enum, fake leader quote, validator disagreement, prompt injection in source, swapped-order conflict, source outage, malformed/fenced JSON, retry exhaustion/history, tied criterion, zero-margin pair, pairwise cycle, incomplete pair matrix, double-finalization, wrong selection/ranking hash, no Condorcet winner, rejected loser, replay, and offchain source changes. Demonstrate verifier independence using actual validator execution where supported.
8. Retain the readable, deterministic API for reuse. Update docs and tests when required by real fixes. Avoid gratuitous rewrite and avoid introducing unrelated features, payments, a full SaaS app, or a frontend.

## GitHub and immutable public fixtures

Remote is precisely **BeatyXO/MeritCircuit**. The initial example URLs in `demo/selection.json` intentionally contain `FIXTURE_COMMIT_PLACEHOLDER`. They are **not live evidence** until pinned.

9. Create the first genuine Git commit containing `fixtures/alpha.md`, `fixtures/beta.md`, `fixtures/gamma.md`, and the rest of the initial implementation; push it to GitHub. Obtain its **real full 40-character commit SHA**. Check GitHub raw URLs for the exact files at that commit. Do not guess a SHA.
10. Run: `python scripts/pin_fixture_commit.py <REAL_40_CHARACTER_FIXTURE_COMMIT_SHA>`.
11. Confirm each URL in `demo/selection.json` resolves to its actual immutable raw GitHub document; commit and push the pinned URL change. No fixture placeholder may remain in final public demo. Ensure the commit used for pinning really contains the fixtures and cannot be a mutable branch ref.
12. If the first push fails due to GitHub authentication or repo access, do not erase the problem or push to another repo. Report exact error and leave a clean local commit/patch for the user.

## Live Studionet proof — mandatory before claiming success

13. Review stable **py-genlayer** documentation/API, pin suitable stable client/tool versions, install and write a reproducible `scripts/live_studionet.py` or equivalent (with read-only resume/verification where appropriate). Handle fee estimation, finalized receipts, and transaction errors using the **actual** stable API. If a deployment/write is not confirmed finalized, do not count it.
14. Validate RPC/chain ID 61999, deploy MeritCircuit, record finalized address and tx. Deploy `MeritAwardGate` with that address, record finalized address and tx.
15. Using immutable public fixture URLs, run an actual selection lifecycle: owner creates selection, adds criteria (positive weights totaling 100), registers candidates, seals; independently query and record 64-hex definition hash. All three candidate pairs across two criteria must be assessed by real consensus-backed executions, not deterministic mocks. Record every actual outcome. If any are legitimately `INDETERMINATE`, retry within limits; never override the result to make a demo green.
16. Finalize each pair and complete ranking; record finalized ranking transaction, 64-hex `ranking_hash`, `winner`, `winner_certified`, all pair margins, cycle handling and final ordered IDs. If no strict Condorcet winner arises from the synthetic documents, report no certified winner and prepare a **separate honest scenario with public grounded evidence** if you need a successful gate demonstration; do not weaken the winner standard or inject leader results.
17. With strict winner proof actually present, demonstrate **real contract-to-contract** `MeritAwardGate.issue_award` and verify resulting onchain award record. Demonstrate wrong-definition-hash rejection, wrong-ranking-hash rejection, loser or uncertified winner rejection, replayed `action_hash` rejection, and unauthorized gate caller rejection. Record hashes/transactions/error receipts where actually visible. No fabricated transaction IDs or pass counts.
18. Complete `deployments/studionet.json` and `DEPLOYMENT.md` **only with evidence actually obtained**: both addresses, both deployment txs, fixture commit SHA, creation/seal/assessment/pair/ranking txs, result hashes, gate positive and negative evidence, test commands and real results. Link exact explorer pages. If negative calls are rejected before broadcast, state that and include exact SDK evidence instead of inventing a failed onchain transaction.

## Final quality gates

19. Confirm `python scripts/preflight.py --final` passes after genuinely verified deployment evidence; all Python compilation and actual Direct Mode tests pass; the correct stable network is used for all live operations; no tracked secrets/private keys/.env/caches/venv/build artifacts; no frontend; non-privileged source input cannot steer contract policy; no ungrounded winner authorization.
20. Inspect `git diff`, `git status`, tracked files, CI checks, **remote branch and final GitHub tree**. Push all final clean commits to `https://github.com/BeatyXO/MeritCircuit.git` on its default branch without force-push. Correct docs to reflect commands that really worked. Do not assume a successful local commit implies a successful remote push.
21. Report the final source and result hashes, exact test counts, build/tool versions, live chain ID and RPC, deployed contract addresses, real deployment/lifecycle/gate transaction evidence, immutable fixture SHA, final 40-character Git commit SHA, and any remaining limitation. **Claim review-ready only if every applicable gate is genuinely passed**. If limited by RPC funding, tooling, finality, or write access, report CONDITIONAL/INCOMPLETE with the precise blocker, rather than fake success.

This project aims at top-tier originality and execution quality, but **do not promise or assert a particular competition/reviewer score**. Correctness and reproducible verification outrank cosmetic claims.
