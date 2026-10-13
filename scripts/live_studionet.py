#!/usr/bin/env python3
"""Reproducible stable Studionet deployment and first-selection lifecycle.

This script is intentionally explicit: --verify-only performs a read-only SDK
chain check; --run is the only mode that signs or broadcasts transactions. It
uses only py-genlayer 0.16.3's stable client interface and never changes chain.
"""
import argparse
import importlib.metadata
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RPC = "https://studio.genlayer.com/api"
CHAIN_ID = 61999
ALIAS = "studionet"
EXPLORER = "https://explorer-studio.genlayer.com"
MANIFEST_PATH = ROOT / "deployments" / "studionet.json"
DEMO_PATH = ROOT / "demo" / "selection.json"
FIXTURES = ("alpha.md", "beta.md", "gamma.md")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(state):
    tmp = MANIFEST_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(MANIFEST_PATH)


def as_text(value):
    return getattr(value, "value", value)


def json_safe(value):
    if isinstance(value, bytes):
        return "0x" + value.hex()
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    value = as_text(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def make_client(account=None):
    from genlayer_py import create_client
    from genlayer_py.chains import studionet

    if studionet.id != CHAIN_ID:
        raise RuntimeError(f"SDK studionet chain definition mismatch: {studionet.id}")
    rpc_urls = studionet.rpc_urls.get("default", {}).get("http", [])
    if rpc_urls != [RPC]:
        raise RuntimeError(f"SDK studionet RPC mismatch: {rpc_urls!r}")
    return create_client(chain=studionet, account=account)


def confirm_network(client):
    """Re-read the effective RPC and actual chain ID immediately before writes."""
    url = getattr(client.provider, "url", None)
    if url != RPC:
        raise RuntimeError(f"effective SDK RPC mismatch: {url!r}")
    actual = int(client.w3.eth.chain_id)
    if actual != CHAIN_ID:
        raise RuntimeError(f"actual chain ID mismatch: expected {CHAIN_ID}, got {actual}")
    print(f"Confirmed alias={ALIAS} rpc={url} actual_chain_id={actual}", flush=True)


def tx_hash_text(tx_hash):
    return tx_hash.hex() if hasattr(tx_hash, "hex") else str(tx_hash)


def wait_finalized(client, tx_hash):
    from genlayer_py.types.transactions import TransactionStatus

    receipt = client.wait_for_transaction_receipt(
        tx_hash, status=TransactionStatus.FINALIZED, interval=5000, retries=120,
        full_transaction=True,
    )
    if as_text(receipt.get("status_name")) != "FINALIZED":
        raise RuntimeError(f"transaction did not finalize: {receipt!r}")
    return receipt


def execution_result(receipt):
    """Normalize the stable SDK receipt shape without guessing success.

    Recent RPCs expose ``tx_execution_result_name`` directly. The stable
    Studionet RPC currently used here returns the consensus transaction view
    instead: ``result_name`` plus a ``consensus_data.leader_receipt`` list.
    Require finalized majority agreement and a successful leader return in
    that shape; a finalized status alone is never sufficient.
    """
    direct = as_text(receipt.get("tx_execution_result_name"))
    if direct:
        return direct
    if as_text(receipt.get("result_name")) != "MAJORITY_AGREE":
        return None
    consensus = receipt.get("consensus_data")
    if not isinstance(consensus, dict):
        return None
    leaders = consensus.get("leader_receipt")
    if not isinstance(leaders, list):
        return None
    leader = next((item for item in leaders
                   if isinstance(item, dict) and item.get("mode") == "leader"), None)
    if leader is None:
        return None
    outcome = as_text(leader.get("execution_result"))
    leader_result = leader.get("result")
    result_status = as_text(leader_result.get("status")) if isinstance(leader_result, dict) else None
    if outcome == "SUCCESS" and result_status == "return":
        return "FINISHED_WITH_RETURN"
    if outcome == "ERROR" and result_status in ("contract_error", "error", "rollback"):
        return "FINISHED_WITH_ERROR"
    return None


def receipt_summary(receipt):
    """Keep lifecycle errors useful without dumping full contract source."""
    return {key: receipt.get(key) for key in
            ("hash", "status_name", "tx_execution_result_name", "result_name", "recipient")
            if key in receipt}


def leader_error(transaction):
    """Extract only the leader's concise GenVM error text from an RPC view."""
    consensus = transaction.get("consensus_data")
    if not isinstance(consensus, dict):
        return ""
    receipts = consensus.get("leader_receipt")
    if not isinstance(receipts, list):
        return ""
    leader = next((item for item in receipts
                   if isinstance(item, dict) and item.get("mode") == "leader"), None)
    if leader is None:
        return ""
    result = leader.get("genvm_result")
    if isinstance(result, dict):
        stderr = result.get("stderr")
        if stderr:
            return str(stderr)
    leader_result = leader.get("result")
    if isinstance(leader_result, dict) and isinstance(leader_result.get("payload"), str):
        return leader_result["payload"]
    return ""


def assessment_tx_count(state):
    """Count finalized assessment transactions once, including retries."""
    return sum(label.startswith("assessment_")
               for label in state.get("transactions", {}))


def write_once(client, state, label, address, function_name, args, account=None,
               expect_success=True):
    """Submit once, persist the hash immediately, resume pending receipts safely."""
    transactions = state.setdefault("transactions", {})
    pending = state.setdefault("pending_transactions", {})
    if label in transactions:
        return transactions[label]["receipt"]
    if label in pending:
        tx_hash = pending[label]["hash"]
    else:
        confirm_network(client)
        tx_hash = tx_hash_text(client.write_contract(
            address=address, function_name=function_name, args=args, account=account,
        ))
        pending[label] = {"hash": tx_hash, "function": function_name}
        save_manifest(state)
    receipt = wait_finalized(client, tx_hash)
    execution = execution_result(receipt)
    succeeded = execution == "FINISHED_WITH_RETURN"
    if succeeded != expect_success:
        if execution == "FINISHED_WITH_ERROR" and expect_success:
            state["status"] = "CONTRACT_ERROR"
            state["incomplete_reason"] = f"{label} finalized with a contract error"
            save_manifest(state)
        raise RuntimeError(
            f"{label} finalized with unexpected execution result {execution!r}; "
            f"receipt={receipt_summary(receipt)!r}"
        )
    record = {"hash": tx_hash, "status": as_text(receipt.get("status_name")),
              "execution": execution, "receipt": json_safe(dict(receipt))}
    transactions[label] = record
    pending.pop(label, None)
    save_manifest(state)
    return receipt


def deploy_once(client, state, contract_key, source_path, args=None):
    address_field = f"{contract_key}_address"
    if state.get(address_field):
        return state[address_field]
    label = f"deploy_{contract_key}"
    pending = state.setdefault("pending_transactions", {})
    if label in pending:
        receipt = wait_finalized(client, pending[label]["hash"])
        execution = execution_result(receipt)
        if execution != "FINISHED_WITH_RETURN":
            # A finalized contract error cannot be repaired by polling the
            # same transaction. Preserve the evidence, clear the checkpoint,
            # and submit one corrected deployment below.
            failed = state.setdefault("failed_transactions", {}).setdefault(label, [])
            failed.append({"hash": pending[label]["hash"], "status": "FINALIZED",
                           "execution": execution,
                           "receipt": receipt_summary(receipt)})
            pending.pop(label)
            save_manifest(state)
            receipt = None
    else:
        receipt = None
    if receipt is None:
        confirm_network(client)
        code = source_path.read_bytes()
        tx_hash = tx_hash_text(client.deploy_contract(code=code, args=args or []))
        pending[label] = {"hash": tx_hash, "contract": str(source_path.relative_to(ROOT))}
        save_manifest(state)
        receipt = wait_finalized(client, tx_hash)
    execution = execution_result(receipt)
    if execution != "FINISHED_WITH_RETURN":
        raise RuntimeError(
            f"{label} finalized unsuccessfully: execution={execution!r}, "
            f"receipt={receipt_summary(receipt)!r}"
        )
    address = receipt.get("recipient")
    decoded = receipt.get("tx_data_decoded") or {}
    if not address:
        address = decoded.get("contractAddress") or decoded.get("contract_address")
    if not address:
        raise RuntimeError(f"finalized deployment receipt has no contract address: {receipt!r}")
    state[address_field] = str(address)
    state[f"{contract_key}_deploy_tx"] = pending[label]["hash"]
    state.setdefault("transactions", {})[label] = {
        "hash": pending[label]["hash"], "status": as_text(receipt.get("status_name")),
        "execution": execution, "receipt": json_safe(dict(receipt)),
    }
    pending.pop(label, None)
    save_manifest(state)
    return str(address)


def read(client, address, function_name, args):
    return client.read_contract(address=address, function_name=function_name, args=args)


def run_lifecycle(client, account, state):
    demo = load_json(DEMO_PATH)
    if any("FIXTURE_COMMIT_PLACEHOLDER" in c["evidence_url"] for c in demo["candidates"]):
        raise RuntimeError("demo URLs are not pinned to a pushed fixture commit")
    for filename in FIXTURES:
        if filename not in " ".join(c["evidence_url"] for c in demo["candidates"]):
            raise RuntimeError(f"demo is missing immutable fixture URL {filename}")

    merit = deploy_once(client, state, "merit_circuit", ROOT / "contracts" / "merit_circuit.py")
    from genlayer_py.types.calldata import CalldataAddress
    gate = deploy_once(client, state, "merit_award_gate", ROOT / "contracts" / "merit_award_gate.py",
                       args=[CalldataAddress(merit)])

    # The first contract created by this clean deployment is selection 1.
    sid = int(state.get("selection_id") or 1)
    if not state.get("selection_id"):
        write_once(client, state, "selection_create", merit, "create_selection",
                   [demo["title"], demo["purpose"], demo["source_host"]], account)
        state["selection_id"] = sid
        save_manifest(state)

    for index, criterion in enumerate(demo["criteria"], 1):
        write_once(client, state, f"criterion_{index}", merit, "add_criterion",
                   [sid, criterion["name"], criterion["rubric"], criterion["weight"]], account)
    for index, candidate in enumerate(demo["candidates"], 1):
        write_once(client, state, f"candidate_{index}", merit, "add_candidate",
                   [sid, candidate["name"], candidate["summary"], candidate["evidence_url"]], account)

    selection = read(client, merit, "get_selection", [sid])
    definition = selection.get("definition_hash")
    if not definition:
        write_once(client, state, "seal_selection", merit, "seal_selection", [sid], account)
        selection = read(client, merit, "get_selection", [sid])
        definition = selection["definition_hash"]
    if len(definition) != 64:
        raise RuntimeError(f"invalid onchain definition hash: {definition!r}")
    state["definition_hash"] = definition
    save_manifest(state)

    assessment_count = 0
    pair_margins = []
    for left in range(1, len(demo["candidates"]) + 1):
        for right in range(left + 1, len(demo["candidates"]) + 1):
            for criterion_id in range(1, len(demo["criteria"]) + 1):
                attempt = sum(
                    f"assessment_{left}_{right}_{criterion_id}_{n}" in state.get("transactions", {})
                    for n in range(1, 4)
                )
                comparison = None
                if attempt:
                    comparison = read(client, merit, "get_comparison", [sid, left, right, criterion_id])
                while attempt < 3 and (comparison is None or int(comparison.get("verdict", 4)) == 4):
                    label = f"assessment_{left}_{right}_{criterion_id}_{attempt + 1}"
                    write_once(client, state, label, merit, "assess_pair_criterion",
                               [sid, left, right, criterion_id, definition], account)
                    assessment_count = assessment_tx_count(state)
                    state["assessment_count"] = assessment_count
                    save_manifest(state)
                    comparison = read(client, merit, "get_comparison", [sid, left, right, criterion_id])
                    attempt = int(comparison.get("attempts", 0))
                if comparison is None or int(comparison.get("verdict", 4)) == 4:
                    state["status"] = "INDETERMINATE"
                    state["incomplete_reason"] = (
                        f"INDETERMINATE retry cap reached for pair {left}/{right}, "
                        f"criterion {criterion_id}"
                    )
                    save_manifest(state)
                    raise RuntimeError(f"INDETERMINATE retry cap reached for {left}/{right}/{criterion_id}")
            assessment_count = assessment_tx_count(state)
            label = f"pair_{left}_{right}"
            if label not in state.get("transactions", {}):
                write_once(client, state, label, merit, "finalize_pair", [sid, left, right, definition], account)
            # get_pair is available only after finalization.
            pair = read(client, merit, "get_pair", [sid, left, right])
            pair_margins.append({"left": left, "right": right, **pair})
    state["assessment_count"] = assessment_tx_count(state)
    state["pair_margins"] = pair_margins
    fixture_shas = {
        match.group(1)
        for candidate in demo["candidates"]
        for match in [re.search(r"/BeatyXO/MeritCircuit/([0-9a-f]{40})/fixtures/", candidate["evidence_url"])]
        if match
    }
    if len(fixture_shas) != 1:
        raise RuntimeError(f"fixture URLs must share one immutable commit SHA: {sorted(fixture_shas)!r}")
    state["fixture_commit_sha"] = fixture_shas.pop()
    txs = state.get("transactions", {})
    state["creation_tx"] = txs["selection_create"]["hash"]
    state["criterion_txs"] = [txs[f"criterion_{i}"]["hash"] for i in range(1, len(demo["criteria"]) + 1)]
    state["candidate_txs"] = [txs[f"candidate_{i}"]["hash"] for i in range(1, len(demo["candidates"]) + 1)]
    state["seal_tx"] = txs["seal_selection"]["hash"]
    state["assessment_txs"] = [v["hash"] for k, v in txs.items() if k.startswith("assessment_")]
    state["pair_txs"] = [txs[f"pair_{a}_{b}"]["hash"]
                          for a in range(1, len(demo["candidates"]) + 1)
                          for b in range(a + 1, len(demo["candidates"]) + 1)]
    save_manifest(state)

    if "ranking_finalize" not in state.get("transactions", {}):
        write_once(client, state, "ranking_finalize", merit, "finalize_ranking", [sid, definition], account)
    result = read(client, merit, "get_result", [sid])
    state.update({"ranking_hash": result["ranking_hash"], "winner_candidate_id": result["winner"],
                  "winner_certified": result["winner_certified"],
                  "ordered_candidate_ids": result["ordered_candidate_ids"]})
    save_manifest(state)

    action = __import__("hashlib").sha256(
        f"MeritCircuit:{sid}:{definition}:{result['ranking_hash']}:{result['winner']}".encode()
    ).hexdigest()
    if result["winner_certified"]:
        write_once(client, state, "award_success", gate, "issue_award",
                   [sid, result["winner"], definition, result["ranking_hash"], action], account)
        state["award_success_tx"] = state["transactions"]["award_success"]["hash"]
        write_once(client, state, "award_replay_rejection", gate, "issue_award",
                   [sid, result["winner"], definition, result["ranking_hash"], action], account,
                   expect_success=False)
        state["replay_rejection_evidence"] = {
            "tx_hash": state["transactions"]["award_replay_rejection"]["hash"],
            "execution": state["transactions"]["award_replay_rejection"]["execution"],
        }
    else:
        # The exact refusal path is useful evidence when the data has no strict
        # Condorcet winner; it never manufactures a successful award.
        write_once(client, state, "uncertified_award_rejection", gate, "issue_award",
                   [sid, result["winner"], definition, result["ranking_hash"], action], account,
                   expect_success=False)
    wrong_definition = "0" * 64 if definition != "0" * 64 else "1" * 64
    wrong_ranking = "0" * 64 if result["ranking_hash"] != "0" * 64 else "1" * 64
    write_once(client, state, "wrong_definition_rejection", gate, "issue_award",
               [sid, result["winner"], wrong_definition, result["ranking_hash"], "1" * 64], account,
               expect_success=False)
    write_once(client, state, "wrong_ranking_rejection", gate, "issue_award",
               [sid, result["winner"], definition, wrong_ranking, "2" * 64], account,
               expect_success=False)
    loser = next(candidate_id for candidate_id in range(1, len(demo["candidates"]) + 1)
                 if candidate_id != result["winner"])
    write_once(client, state, "loser_rejection", gate, "issue_award",
               [sid, loser, definition, result["ranking_hash"], "3" * 64], account,
               expect_success=False)
    unauthorized_key = os.environ.get("GENLAYER_UNAUTHORIZED_PRIVATE_KEY")
    if not unauthorized_key:
        raise RuntimeError("GENLAYER_UNAUTHORIZED_PRIVATE_KEY is required for unauthorized gate rejection proof")
    from genlayer_py import create_account
    unauthorized_account = create_account(unauthorized_key)
    write_once(client, state, "unauthorized_rejection", gate, "issue_award",
               [sid, result["winner"], definition, result["ranking_hash"], "4" * 64],
               unauthorized_account, expect_success=False)
    state["ranking_tx"] = state["transactions"]["ranking_finalize"]["hash"]
    state["gate_negative_evidence"] = {
        label: {"tx_hash": state["transactions"][label]["hash"],
                "execution": state["transactions"][label]["execution"]}
        for label in ("wrong_definition_rejection", "wrong_ranking_rejection",
                      "loser_rejection", "unauthorized_rejection")
    }
    if result["winner_certified"]:
        state["status"] = "VERIFIED"
    else:
        state["status"] = "NO_CERTIFIED_WINNER"
    state["explorer_evidence"] = {
        key: f"{EXPLORER}/tx/{value['hash']}"
        for key, value in state["transactions"].items()
    }
    save_manifest(state)
    print(json.dumps({"selection_id": sid, "definition_hash": definition,
                      "ranking_hash": result["ranking_hash"], "winner": result["winner"],
                      "winner_certified": result["winner_certified"],
                      "ordered_candidate_ids": result["ordered_candidate_ids"],
                      "pair_margins": pair_margins}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify-only", action="store_true", help="read-only SDK RPC and chain check")
    mode.add_argument("--run", action="store_true", help="deploy and execute the pinned complete lifecycle")
    args = parser.parse_args()
    version = importlib.metadata.version("genlayer-py")
    if version != "0.16.3":
        raise SystemExit(f"Expected pinned stable genlayer-py 0.16.3, found {version}")
    account = None
    if args.run:
        private_key = os.environ.get("GENLAYER_PRIVATE_KEY")
        if not private_key:
            raise SystemExit("GENLAYER_PRIVATE_KEY is required for --run; never put it in the manifest")
        from genlayer_py import create_account
        account = create_account(private_key)
        if not os.environ.get("GENLAYER_UNAUTHORIZED_PRIVATE_KEY"):
            raise SystemExit("GENLAYER_UNAUTHORIZED_PRIVATE_KEY is required for full rejection proof")
    client = make_client(account)
    confirm_network(client)
    if args.verify_only:
        print("Read-only Studionet identity confirmed; no transaction was signed or broadcast.")
        return
    state = load_json(MANIFEST_PATH)
    state["status"] = "IN_PROGRESS"
    state.pop("incomplete_reason", None)
    state["network_verification"] = {"alias": ALIAS, "chain_id": CHAIN_ID, "rpc": RPC,
                                     "sdk": "genlayer-py==0.16.3"}
    save_manifest(state)
    run_lifecycle(client, account, state)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"LIVE STUDIONET RUN INCOMPLETE: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
