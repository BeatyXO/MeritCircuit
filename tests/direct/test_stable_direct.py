"""GenLayer Testing Suite Direct Mode. Requires pinned genlayer-test dependency.

These checks MUST be run by the takeover agent with GenLayer's real Direct Mode.
The independent offline harness in ../test_merit_circuit.py is not a substitute.
"""
import json

CONTRACT = "contracts/merit_circuit.py"
GENVM_VERSION = "v0.2.16"  # Stable runner containing the contract's pinned py-genlayer bundle.
H = "raw.githubusercontent.com"
URL_A = "https://raw.githubusercontent.com/example/merit-demo/abc123/alpha.md"
URL_B = "https://raw.githubusercontent.com/example/merit-demo/abc123/beta.md"
DOC_A = "Alpha project evidence: stable technical architecture, maintained implementation, measured scope."
DOC_B = "Beta project evidence: experimental technical architecture, incomplete integration, narrower scope."


def make(direct_vm, direct_deploy):
    c = direct_deploy(CONTRACT, sdk_version=GENVM_VERSION)
    sid = c.create_selection("Grants", "Compare technical maturity for open projects", H)
    c.add_criterion(sid, "Feasibility", "Choose the solution with the best documented feasibility", 100)
    c.add_candidate(sid, "Alpha", "Published documentation of mature project", URL_A)
    c.add_candidate(sid, "Beta", "Published documentation of experimental project", URL_B)
    return c, sid


def test_sealing_and_owner_lock(direct_vm, direct_deploy):
    c, sid = make(direct_vm, direct_deploy)
    h = c.seal_selection(sid)
    assert len(h) == 64
    with direct_vm.expect_revert("sealed"):
        c.add_criterion(sid, "Extra", "Attempt post seal rubric change", 1)
    with direct_vm.expect_revert("matrix incomplete"):
        c.finalize_ranking(sid, h)


def test_bad_source_rejected(direct_vm, direct_deploy):
    c = direct_deploy(CONTRACT, sdk_version=GENVM_VERSION)
    sid = c.create_selection("Grants", "Compare candidate grants", H)
    with direct_vm.expect_revert("source host mismatch"):
        c.add_candidate(sid, "Injected", "Other", "https://example.com/malicious")


def test_matrix_requires_all_consensus_criteria(direct_vm, direct_deploy):
    c, sid = make(direct_vm, direct_deploy)
    h = c.seal_selection(sid)
    with direct_vm.expect_revert("missing comparison"):
        c.finalize_pair(sid, 1, 2, h)
    with direct_vm.expect_revert("definition mismatch"):
        c.assess_pair_criterion(sid, 1, 2, 1, "a" * 64)


def test_grounded_comparison_and_ranking(direct_vm, direct_deploy):
    c, sid = make(direct_vm, direct_deploy)
    h = c.seal_selection(sid)
    direct_vm.mock_web(r"alpha\.md", {"status": 200, "body": DOC_A})
    direct_vm.mock_web(r"beta\.md", {"status": 200, "body": DOC_B})
    direct = json.dumps({"verdict": "LEFT", "reason": "Alpha feasibility is established",
                         "left_quote": "Alpha project evidence", "right_quote": "Beta project evidence"})
    reverse = json.dumps({"verdict": "RIGHT", "reason": "Alpha feasibility is established",
                          "left_quote": "Beta project evidence", "right_quote": "Alpha project evidence"})
    direct_vm.mock_llm(r'"mirrored_check":false', direct)
    direct_vm.mock_llm(r'"mirrored_check":true', reverse)
    verdict = c.assess_pair_criterion(sid, 1, 2, 1, h)
    assert verdict == 1
    assert direct_vm.run_validator() is True
    c.finalize_pair(sid, 1, 2, h)
    r = c.finalize_ranking(sid, h)
    assert len(r) == 64
    assert c.is_ranked_winner(sid, 1, h, r)
    assert not c.is_ranked_winner(sid, 2, h, r)


def test_validator_independently_rejects_different_semantic_result(direct_vm, direct_deploy):
    c, sid = make(direct_vm, direct_deploy)
    h = c.seal_selection(sid)
    direct_vm.mock_web(r"alpha\.md", {"status": 200, "body": DOC_A})
    direct_vm.mock_web(r"beta\.md", {"status": 200, "body": DOC_B})
    direct_vm.mock_llm(r'"mirrored_check":false', json.dumps(
        {"verdict": "LEFT", "reason": "Alpha has completed architecture", "left_quote": "Alpha project evidence",
         "right_quote": "Beta project evidence"}))
    direct_vm.mock_llm(r'"mirrored_check":true', json.dumps(
        {"verdict": "RIGHT", "reason": "Beta comparison mirror", "left_quote": "Beta project evidence",
         "right_quote": "Alpha project evidence"}))
    assert c.assess_pair_criterion(sid, 1, 2, 1, h) == 1

    # The validator independently fetches both sources and invokes its own
    # mirrored model judgments. Replace its model answers with the opposite
    # normalized decision and ensure it rejects the leader's calldata.
    direct_vm.clear_mocks()
    direct_vm.mock_web(r"alpha\.md", {"status": 200, "body": DOC_A})
    direct_vm.mock_web(r"beta\.md", {"status": 200, "body": DOC_B})
    direct_vm.mock_llm(r'"mirrored_check":false', json.dumps(
        {"verdict": "RIGHT", "reason": "contradict leader", "left_quote": "Alpha project evidence",
         "right_quote": "Beta project evidence"}))
    direct_vm.mock_llm(r'"mirrored_check":true', json.dumps(
        {"verdict": "LEFT", "reason": "mirrored contradiction", "left_quote": "Beta project evidence",
         "right_quote": "Alpha project evidence"}))
    assert direct_vm.run_validator() is False


def test_validator_rejects_forged_leader_quotes(direct_vm, direct_deploy):
    c, sid = make(direct_vm, direct_deploy)
    h = c.seal_selection(sid)
    direct_vm.mock_web(r"alpha\.md", {"status": 200, "body": DOC_A})
    direct_vm.mock_web(r"beta\.md", {"status": 200, "body": DOC_B})
    forged = json.dumps({"verdict": "LEFT", "reason": "invented evidence",
                         "left_quote": "FABRICATED ALPHA PROOF", "right_quote": "FABRICATED BETA PROOF"})
    direct_vm.mock_llm(r'"mirrored_check":false', forged)
    direct_vm.mock_llm(r'"mirrored_check":true', forged)
    assert c.assess_pair_criterion(sid, 1, 2, 1, h) == 4
    # Challenge the captured verifier with a forged decisive leader payload.
    # It must re-evaluate and reject both the decision and unsupported spans.
    assert direct_vm.run_validator(leader_result={
        "verdict": 1, "reason": "invented evidence",
        "left_quote": "FABRICATED ALPHA PROOF", "right_quote": "FABRICATED BETA PROOF",
    }) is False
