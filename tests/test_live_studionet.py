"""Receipt normalization tests for the pinned stable GenLayer SDK lifecycle."""
from scripts.live_studionet import execution_result


def current_rpc_receipt(leader_outcome, result_status, result_name="MAJORITY_AGREE"):
    return {
        "status_name": "FINALIZED",
        "result_name": result_name,
        "consensus_data": {
            "leader_receipt": [{
                "mode": "leader",
                "execution_result": leader_outcome,
                "result": {"status": result_status, "payload": None},
            }],
        },
    }


def test_normalizes_stable_rpc_success_only_with_majority_and_return():
    assert execution_result(current_rpc_receipt("SUCCESS", "return")) == "FINISHED_WITH_RETURN"


def test_normalizes_stable_rpc_contract_error_for_expected_rejections():
    assert execution_result(current_rpc_receipt("ERROR", "contract_error")) == "FINISHED_WITH_ERROR"


def test_does_not_infer_success_from_finality_or_missing_consensus():
    assert execution_result({"status_name": "FINALIZED"}) is None
    assert execution_result(current_rpc_receipt("SUCCESS", "return", "UNDETERMINED")) is None
    assert execution_result(current_rpc_receipt("SUCCESS", "error")) is None


def test_prefers_explicit_execution_result_when_sdk_provides_one():
    receipt = current_rpc_receipt("ERROR", "contract_error")
    receipt["tx_execution_result_name"] = "FINISHED_WITH_RETURN"
    assert execution_result(receipt) == "FINISHED_WITH_RETURN"
