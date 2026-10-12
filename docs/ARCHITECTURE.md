# Architecture — MeritCircuit

## Two contracts, no frontend

**MeritCircuit** is the reusable primitive. **MeritAwardGate** consumes one locked result via a typed `@gl.contract_interface` view call and rejects action replay. Gate records are test demonstrations, not a payment system.

## Trust split

Deterministic: owner permissions, canonical URL policy, definition hash, candidate/criterion limits, frozen weights, pair matrix completeness, criterion attempt counts and audit history, weighted margins, Ranked Pairs sorting, cycle checks, topological ordering, Condorcet certification, ranking hash, consumer authorization and nonce replay.

Nondeterministic (consensus-critical): independent HTTPS render for each candidate's registered URL, two constrained LLM judgments (forward and reversed candidate presentation), quote anchoring to the two independently observed extracts, leader proposal and validator's own refreshed assessment. A validator rejects a leader verdict that doesn't match its own verdict or asserts quotes absent from validator-observed source content. Different quote wording is allowed if the leader's own quotes also occur in validator evidence. The validator uses `gl.vm.run_nondet_unsafe` inside the GenLayer equivalence boundary.

No AI call ever receives the candidate set as a whole or writes the root ranking.

## Phases

`OPEN → SEALED → RANKED` (no backward transition).

A SEALED selection may contain incomplete comparisons. For each pair/criterion, at most three observations are permitted; only INDETERMINATE can be reassessed, and every attempt is stored under a unique attempt key. Every definitive criterion is immutable. Pair completion requires all criteria in {LEFT,RIGHT,TIE}. Ranking completion requires every candidate pair.

## Weighted pair margins

`margin = sum(weights where LEFT) - sum(weights where RIGHT)`; TIE contributes zero. Pair strength is absolute margin. Additional positive support acts only as a deterministic secondary ordering key. Zero-margin pairs add no edge.

## Ranked Pairs mechanics

For each victory sort by (-abs margin, -winner support weight, winner ID, loser ID). Add winner → loser unless the reverse path already exists. Traverse locked DAG by repeatedly choosing the smallest ID among zero-in-degree nodes. Cycle removal and tie handling are fully deterministic. Results are recomputed from sealed state exactly once; there are no offchain rankings.

## Strict winner

A topological winner may have tied or lost a head-to-head pair even if it ranks first. Such a top node cannot authorize a high-consequence award. `winner_certified=true` only if that first candidate has strictly positive margin against every competitor. For two candidates, this is equivalent to margin>0 for the rank-one candidate. For three with a cycle, certification is impossible.

## Hash domains

`MERITCIRCUIT/SELECTION/V1`: canonical sorted-key JSON includes title, purpose, source host, all candidates in ID order and all criteria with weights. `Keccak256` digest is a 64-hex lowercase hash.

`MERITCIRCUIT/RANKING/V1`: canonical sorted-key JSON includes definition hash, all final pair rows, locked/skipped edges, deterministic order and strict-winner flag. Historical assessments have separate domain-bound assessment hashes.

## Explicit boundaries

This is not a marketplace/matcher, rights graph, correction history, permission scheduler, eligibility/exception interpreter, or an AI oracle which simply returns a winner. It is an opinionated deterministic **social-choice aggregation primitive** on top of consensus-backed pairwise semantic edges.
