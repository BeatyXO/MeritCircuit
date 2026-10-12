# Threat model and failure handling

| Threat | Protocol response | Residual risk |
|---|---|---|
| Untrusted source contains prompt injection | Prompt labels data, freezes predeclared evaluation rubric, asks for bounded quote anchors; validator independently re-renders and re-evaluates | LLMs may still be influenced; audit real validators under prompt attacks |
| Leader fabricates decisive quote | Validator independently refetches and checks *leader's* quoted spans | Quotes can be real but misleading; semantic re-evaluation remains necessary |
| Leader fabricates verdict | Validator independently classifies pair, criterion and mirror | Different models can make same mistaken decision |
| Candidate swap/order bias | Canonical pair IDs plus forward and reversed candidate-order assessments | Label/semantic biases can remain; add extra tests |
| Arbitrary off-chain reranking | Ranking engine receives only immutable weighted pair summaries | Algorithm has normative/social-choice tradeoffs |
| Cycle A>B>C>A | Ranked Pairs skips cycle-producing edges; top is not certified without strict Condorcet wins | Cyclic preferences yield no award; users may wish alternate policies |
| Semantic tie exploited via registration order | Deterministic ID tie-break visible in rank proof, **no award certificate** absent strict head-to-head winner | Ranking display still reflects ID order |
| Mutated web source after sealing | Source URLs freeze; live fixtures use commit-addressed GitHub raw URLs | Generic user-defined hosts/URLs may serve mutable content |
| Source substitution | Assessment methods take only indices; sealed URL record is used for web fetch | Host owner may control all data on their chosen domain |
| Network/LLM outage | INDETERMINATE or consensus reject; bounded retries; no fabricated default | Permanent liveness failure if sources remain unreachable |
| Source host SSRF | Requires an exact HTTPS authority, valid ASCII DNS labels, no credentials, port, IP literal or local DNS form | DNS rebinding and redirect defenses depend on GenVM web subsystem; review against live renderer behavior |
| Malformed JSON | Strict schema with bounded fields and duplicate-key rejection; becomes INDETERMINATE | This can exhaust retry cap |
| Forged consumer winner proof | Typed contract read plus definition and ranking hash matches | Consumer must trust exact deployed MeritCircuit address |
| Replay award side effect | Persistent used action digest checked before record creation | Distinct action digest may represent same real-world action; caller defines canonical action IDs |
| Fake live proof | Evidence manifest initially null, final preflight refuses incompleteness | Independent explorer verification still required |

Never classify sample fixture text as independent proof of a real-world project's value. Never treat validator consensus as proof of objectivity. Do not include funded token transfers in this reference gate.
