# Reviewer demo — acceptance criteria

1. Inspect `contracts/merit_circuit.py` and `contracts/merit_award_gate.py`. The former must contain the semantic comparison function and *pure* deterministic Ranked Pairs. No frontend.
2. Run static preflight and offline harness. Check owner, sealing, source namespace, malformed-model and order-bias behaviors.
3. Run the pinned GenLayer Direct Mode tests. The suite explicitly runs the captured verifier again with `run_validator()` and adversarial leader data. Direct Mode has no address-based contract-to-contract support, so require the separate Studionet gate evidence below.
4. Verify first pushed GitHub commit containing `fixtures/`. Pin `demo/selection.json` to its exact 40-hex SHA and push the pin. Check raw URLs resolve.
5. Run `python scripts/live_studionet.py --verify-only`, then deploy MeritCircuit and MeritAwardGate on **studionet 61999** with finalized transaction receipts.
6. Create example selection, add two weighted criteria (60/40), three candidates, seal; record definition hash.
7. For all **3 candidate pairs × 2 criteria = 6 semantic assessments**, demonstrate consensus with real web renders and two-way quote grounding. An assessment may be INDETERMINATE; do not forge a positive result. Finalize all 3 pair rows.
8. Finalize ranking and record the ranking hash plus winner-certification result. The sample documents do not guarantee a strict winner under independent LLM evaluation; adjust *new legitimate example data* if required, do not force a model output.
9. For a strict winner, demonstrate gate approving the winner with both expected hashes; wrong definition, wrong ranking, wrong candidate and action replay must fail. If no strict winner, demonstrate the refusal honestly and create a separate fully grounded successful case.
10. Record real addresses, transactions, all successful and rejected calls, test commands and limitations in `deployments/studionet.json` and `DEPLOYMENT.md`.

Do not claim live verification from mocked Python tests.
