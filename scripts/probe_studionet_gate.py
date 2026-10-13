#!/usr/bin/env python3
"""Exercise only independently identifiable negative MeritAwardGate paths.

Requires deployed addresses in deployments/studionet.json and the two funded
test-wallet environment variables. Every write checks the effective Studionet
RPC and actual chain ID immediately beforehand and records its hash before
waiting. It never makes a successful award or treats an incomplete ranking as
certified.
"""
import hashlib
import json
import os
from pathlib import Path

from genlayer_py import create_account

from live_studionet import (
    ROOT, as_text, confirm_network, execution_result, leader_error, tx_hash_text,
    load_json, make_client, receipt_summary, save_manifest, wait_finalized,
)


PROBE_PATH = ROOT / "deployments" / "gate_probe.json"


def main():
    deployer_key = os.environ.get("GENLAYER_PRIVATE_KEY")
    unauthorized_key = os.environ.get("GENLAYER_UNAUTHORIZED_PRIVATE_KEY")
    if not deployer_key or not unauthorized_key:
        raise SystemExit("Both test-wallet keys must be set in the process environment")
    deployer = create_account(deployer_key)
    unauthorized = create_account(unauthorized_key)
    client = make_client(deployer)
    confirm_network(client)

    state = load_json(ROOT / "deployments" / "studionet.json")
    gate = state.get("merit_award_gate_address")
    circuit = state.get("merit_circuit_address")
    sid = int(state.get("selection_id") or 0)
    definition = state.get("definition_hash")
    if not gate or not circuit or not sid or not definition:
        raise RuntimeError("active deployment and sealed selection evidence are required")
    selection = client.read_contract(address=circuit, function_name="get_selection", args=[sid])
    if selection.get("definition_hash") != definition:
        raise RuntimeError("onchain definition does not match the recorded selection hash")
    if int(selection.get("phase", 0)) == 3:
        raise RuntimeError("selection is already ranked; use the complete lifecycle path")

    if PROBE_PATH.exists():
        evidence = load_json(PROBE_PATH)
        if evidence.get("gate_address") != gate or evidence.get("selection_id") != sid:
            raise RuntimeError("existing gate probe belongs to a different deployment")
    else:
        evidence = {"network": "studionet", "chain_id": 61999,
                    "rpc": "https://studio.genlayer.com/api", "gate_address": gate,
                    "merit_circuit_address": circuit, "selection_id": sid,
                    "definition_hash": definition, "probes": {}}
        PROBE_PATH.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    probes = evidence.setdefault("probes", {})

    def submit(label, account, args, expected_error):
        if label in probes and probes[label].get("execution") == "FINISHED_WITH_ERROR":
            return
        action_hash = args[-1]
        if label in state.get("pending_transactions", {}):
            tx_hash = state["pending_transactions"][label]["hash"]
        else:
            confirm_network(client)
            tx_hash = tx_hash_text(client.write_contract(address=gate, function_name="issue_award",
                                                         args=args, account=account))
            state.setdefault("pending_transactions", {})[label] = {"hash": tx_hash,
                                                                  "function": "issue_award"}
            save_manifest(state)
            evidence["pending"] = {"label": label, "hash": tx_hash}
            PROBE_PATH.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        receipt = wait_finalized(client, tx_hash)
        execution = execution_result(receipt)
        if execution != "FINISHED_WITH_ERROR":
            raise RuntimeError(f"{label} had unexpected execution={execution!r}")
        transaction = client.get_transaction(tx_hash)
        error = leader_error(transaction)
        if expected_error not in error:
            raise RuntimeError(f"{label} did not fail for the expected reason: {error[:400]!r}")
        probes[label] = {"tx_hash": tx_hash, "status": as_text(receipt.get("status_name")),
                         "execution": execution, "leader_error": expected_error,
                         "action_hash": action_hash}
        evidence.pop("pending", None)
        state.setdefault("negative_probe_transactions", {})[label] = tx_hash
        state.setdefault("gate_probe_transactions", {})[label] = tx_hash
        state["pending_transactions"].pop(label, None)
        save_manifest(state)
        PROBE_PATH.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    uncertified_action = hashlib.sha256(
        f"MeritCircuit:uncertified:{sid}:{definition}".encode()
    ).hexdigest()
    submit("uncertified_candidate", deployer,
           [sid, 1, definition, "0" * 64, uncertified_action],
           "pinned ranking does not authorize this candidate")

    unauthorized_action = hashlib.sha256(
        f"MeritCircuit:unauthorized:{sid}:{definition}".encode()
    ).hexdigest()
    submit("unauthorized_caller", unauthorized,
           [sid, 1, definition, "0" * 64, unauthorized_action],
           "only gate owner may issue an award")

    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
