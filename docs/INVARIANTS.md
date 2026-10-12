# Protocol invariants

1. Each selection is owned by its creator; only the creator can add criteria/candidates or seal the definition.
2. The candidate set is bounded (2–8) and criterion set bounded (1–6). Weights are strictly positive and sum to exactly 100 at seal time.
3. At seal time, `definition_hash` commits to ordered candidates, URLs, criteria, weights, title, purpose and source namespace. No post-seal modification is permitted.
4. Pair identity is canonical `left < right` and criterion IDs are bounded; unauthorized source swapping via method arguments is impossible.
5. Every semantic assessment uses URLs from sealed candidate records, not a transaction-provided replacement URL.
6. A decisive result must be grounded in exact source quotes, survive mirror-order agreement, and be independently reverified by GenLayer validators. Malformed, unavailable or inconsistent source outputs become INDETERMINATE or cause transaction rejection.
7. Only INDETERMINATE is retryable, at most 3 times, and each retry has an append-only historical record. Definitive judgments are never overwritten.
8. An incomplete, unassessed, or indeterminate pair cannot be finalized. A finalized pair cannot be recomputed or overwritten.
9. Final ranking requires the complete `n*(n-1)/2` pair matrix. Only code produces margins, edge order, cycles and ranking.
10. Post-ranking mutation is prohibited; the definition and result hashes pin the complete accepted tournament.
11. A top-ranked candidate is **not** sufficient for a downstream award. Only a strict pairwise Condorcet winner is certified.
12. MeritAwardGate uses typed IC-to-IC reads, pins both definition and ranking hashes, is callable only by its owner, and rejects all repeated action hashes.
13. No network address, transaction ID or success report is valid until independently observed on stable Studionet, chain 61999.

## Failure states

Insufficient source evidence / model output disagreement / data incompleteness → INDETERMINATE or transaction rejection. Three unresolved attempts → stalled selection (no arbitrary default winner). Pair matrix incomplete → no ranking. Cycle or top tie → ranked order but no **certified winner**. Hash mismatch / unauthorized or replayed consumer action → reject.
