#!/usr/bin/env python3
"""Run a separate, source-grounded two-candidate gate demonstration.

This scenario uses the already pinned Alpha/Beta synthetic source documents and
the unchanged criteria. It does not replace or claim completion of selection 1,
whose three-candidate matrix contains a bounded INDETERMINATE result.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.live_studionet as live

STATE_PATH = ROOT / "deployments" / "award_scenario.json"
INDETERMINATE = 4


def initial_state(active):
    return {
        "network": live.ALIAS,
        "chain_id": live.CHAIN_ID,
        "rpc": live.RPC,
        "sdk": "genlayer-py==0.16.3",
        "status": "IN_PROGRESS",
        "scenario": "two-candidate positive typed gate demonstration",
        "source_fixture_commit": "233fdf7a1f4f3a5f8a03d0eccc33fc54f0972ef5",
        "merit_circuit_address": active["merit_circuit_address"],
        "merit_award_gate_address": active["merit_award_gate_address"],
        "selection_id": 2,
        "transactions": {},
        "pending_transactions": {},
        "canceled_transactions": [],
    }


def action_hash(label, sid, definition, ranking, candidate):
    payload = f"MeritCircuit:{label}:{sid}:{candidate}:{definition}:{ranking}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main():
    owner_key = os.environ.get("GENLAYER_PRIVATE_KEY")
    unauthorized_key = os.environ.get("GENLAYER_UNAUTHORIZED_PRIVATE_KEY")
    if not owner_key or not unauthorized_key:
        raise SystemExit("Both authorized test-wallet keys must be process environment variables")
    from genlayer_py import create_account

    owner = create_account(owner_key)
    unauthorized = create_account(unauthorized_key)
    client = live.make_client(owner)
    live.confirm_network(client)
    active = live.load_json(live.MANIFEST_PATH)
    if active.get("status") not in ("INDETERMINATE", "IN_PROGRESS"):
        raise RuntimeError("expected original selection evidence to remain visibly incomplete")

    live.MANIFEST_PATH = STATE_PATH
    state = live.load_json(STATE_PATH) if STATE_PATH.exists() else initial_state(active)
    if state.get("selection_id") != 2:
        raise RuntimeError("separate scenario must use expected next selection id 2")
    live.save_manifest(state)
    demo = live.load_json(live.DEMO_PATH)
    sid = 2
    merit = state["merit_circuit_address"]
    gate = state["merit_award_gate_address"]

    live.write_once(client, state, "selection_create", merit, "create_selection",
                    ["Synthetic two-candidate gate demonstration",
                     "Separate typed consumer proof using only the registered public synthetic evidence",
                     demo["source_host"]], owner)
    for criterion_id, criterion in enumerate(demo["criteria"], 1):
        live.write_once(client, state, f"criterion_{criterion_id}", merit, "add_criterion",
                        [sid, criterion["name"], criterion["rubric"], criterion["weight"]], owner)
    for candidate_id, candidate in enumerate(demo["candidates"][:2], 1):
        live.write_once(client, state, f"candidate_{candidate_id}", merit, "add_candidate",
                        [sid, candidate["name"], candidate["summary"], candidate["evidence_url"]], owner)
    live.write_once(client, state, "seal_selection", merit, "seal_selection", [sid], owner)
    selection = live.read(client, merit, "get_selection", [sid])
    definition = selection["definition_hash"]
    state["definition_hash"] = definition
    state["candidate_names"] = [candidate["name"] for candidate in demo["candidates"][:2]]
    state["criterion_names"] = [criterion["name"] for criterion in demo["criteria"]]
    live.save_manifest(state)

    for criterion_id in range(1, len(demo["criteria"]) + 1):
        try:
            comparison = live.read(client, merit, "get_comparison", [sid, 1, 2, criterion_id])
        except Exception:
            comparison = None
        while True:
            attempt = int(comparison.get("attempts", 0)) if comparison else 0
            verdict = int(comparison.get("verdict", INDETERMINATE)) if comparison else INDETERMINATE
            if verdict != INDETERMINATE:
                break
            if attempt >= 3:
                state["status"] = "INDETERMINATE"
                state["incomplete_reason"] = f"retry cap for criterion {criterion_id}"
                live.save_manifest(state)
                raise RuntimeError(state["incomplete_reason"])
            label = f"assessment_1_2_{criterion_id}_{attempt + 1}"
            live.write_once(client, state, label, merit, "assess_pair_criterion",
                            [sid, 1, 2, criterion_id, definition], owner)
            comparison = live.read(client, merit, "get_comparison", [sid, 1, 2, criterion_id])
    live.write_once(client, state, "pair_1_2", merit, "finalize_pair",
                    [sid, 1, 2, definition], owner)
    pair = live.read(client, merit, "get_pair", [sid, 1, 2])
    live.write_once(client, state, "ranking_finalize", merit, "finalize_ranking",
                    [sid, definition], owner)
    result = live.read(client, merit, "get_result", [sid])
    state.update({
        "assessment_count": live.assessment_tx_count(state),
        "pair_margin": pair,
        "ranking_hash": result["ranking_hash"],
        "winner_candidate_id": result["winner"],
        "winner_certified": result["winner_certified"],
        "ordered_candidate_ids": result["ordered_candidate_ids"],
    })
    if not result["winner_certified"]:
        state["status"] = "NO_CERTIFIED_WINNER"
        live.save_manifest(state)
        raise RuntimeError("separate scenario ranked but did not certify a strict Condorcet winner")

    winner = int(result["winner"])
    action = action_hash("positive", sid, definition, result["ranking_hash"], winner)
    live.write_once(client, state, "award_success", gate, "issue_award",
                    [sid, winner, definition, result["ranking_hash"], action], owner)
    state["award_success_tx"] = state["transactions"]["award_success"]["hash"]
    state["award_record"] = live.read(client, gate, "get_award", [1])

    probes = [
        ("replay_rejection", owner, winner, definition, result["ranking_hash"], action),
        ("wrong_definition_rejection", owner, winner, "0" * 64, result["ranking_hash"],
         action_hash("wrong-definition", sid, definition, result["ranking_hash"], winner)),
        ("wrong_ranking_rejection", owner, winner, definition, "0" * 64,
         action_hash("wrong-ranking", sid, definition, result["ranking_hash"], winner)),
        ("losing_candidate_rejection", owner, 2 if winner == 1 else 1, definition,
         result["ranking_hash"], action_hash("loser", sid, definition,
                                             result["ranking_hash"], 2 if winner == 1 else 1)),
        ("unauthorized_caller_rejection", unauthorized, winner, definition,
         result["ranking_hash"], action_hash("unauthorized", sid, definition,
                                             result["ranking_hash"], winner)),
    ]
    for label, caller, candidate_id, def_hash, rank_hash, used_action in probes:
        receipt = live.write_once(client, state, label, gate, "issue_award",
                                  [sid, candidate_id, def_hash, rank_hash, used_action],
                                  caller, expect_success=False)
        state.setdefault("rejections", {})[label] = {
            "tx_hash": state["transactions"][label]["hash"],
            "execution": state["transactions"][label]["execution"],
            "leader_error": live.leader_error(receipt),
        }
        live.save_manifest(state)

    state["status"] = "VERIFIED"
    state["explorer_evidence"] = {
        name: f"{live.EXPLORER}/tx/{record['hash']}"
        for name, record in state["transactions"].items()
    }
    live.save_manifest(state)
    print(json.dumps({key: state[key] for key in (
        "selection_id", "definition_hash", "ranking_hash", "winner_candidate_id",
        "winner_certified", "ordered_candidate_ids", "pair_margin", "award_success_tx",
        "rejections",
    )}, indent=2))


if __name__ == "__main__":
    main()
