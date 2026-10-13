#!/usr/bin/env python3
"""Run a fresh three-candidate selection on the deployed stable Studionet ICs.

This is a new selection (ID 3), not a retry or rewrite of exhausted selection 1.
It uses immutable fixture URLs and retains the onchain three-attempt cap.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.live_studionet as live

DEMO_PATH = ROOT / "demo" / "selection_live_lifecycle.json"
STATE_PATH = ROOT / "deployments" / "studionet_selection_3.json"
SELECTION_ID = 3
INDETERMINATE = 4


def action_hash(selection_id, definition, ranking, candidate):
    payload = f"MeritCircuit:{selection_id}:{definition}:{ranking}:{candidate}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main():
    owner_key = os.environ.get("GENLAYER_PRIVATE_KEY")
    unauthorized_key = os.environ.get("GENLAYER_UNAUTHORIZED_PRIVATE_KEY")
    if not owner_key or not unauthorized_key:
        raise SystemExit("owner and unauthorized test-wallet keys must be process environment variables")
    from genlayer_py import create_account

    owner = create_account(owner_key)
    unauthorized = create_account(unauthorized_key)
    live.confirm_network(live.make_client(owner))
    active = live.load_json(live.MANIFEST_PATH)
    state = live.load_json(STATE_PATH) if STATE_PATH.exists() else {
        "network": live.ALIAS, "chain_id": live.CHAIN_ID, "rpc": live.RPC,
        "sdk": "genlayer-py==0.16.3", "status": "IN_PROGRESS",
        "selection_id": SELECTION_ID,
        "merit_circuit_address": active["merit_circuit_address"],
        "merit_award_gate_address": active["merit_award_gate_address"],
        "transactions": {}, "pending_transactions": {}, "canceled_transactions": [],
    }
    live.MANIFEST_PATH = STATE_PATH
    if int(state["selection_id"]) != SELECTION_ID:
        raise RuntimeError("recovery lifecycle must use selection ID 3")
    for field in ("merit_circuit_deploy_tx", "merit_award_gate_deploy_tx",
                  "deployed_source_commit", "network_verification"):
        if field in active:
            state[field] = active[field]
    client = live.make_client(owner)
    demo = live.load_json(DEMO_PATH)
    candidates = demo["candidates"]
    fixture_shas = {url.split("/MeritCircuit/")[1].split("/")[0]
                    for url in (candidate["evidence_url"] for candidate in candidates)}
    if len(fixture_shas) != 1 or not all(len(sha) == 40 for sha in fixture_shas):
        raise RuntimeError("candidate sources must share one immutable 40-character fixture commit")
    merit = state["merit_circuit_address"]
    gate = state["merit_award_gate_address"]
    sid = SELECTION_ID

    live.write_once(client, state, "selection_create", merit, "create_selection",
                    [demo["title"], demo["purpose"], demo["source_host"]], owner)
    for criterion_id, criterion in enumerate(demo["criteria"], 1):
        live.write_once(client, state, f"criterion_{criterion_id}", merit, "add_criterion",
                        [sid, criterion["name"], criterion["rubric"], criterion["weight"]], owner)
    for candidate_id, candidate in enumerate(candidates, 1):
        live.write_once(client, state, f"candidate_{candidate_id}", merit, "add_candidate",
                        [sid, candidate["name"], candidate["summary"], candidate["evidence_url"]], owner)
    live.write_once(client, state, "seal_selection", merit, "seal_selection", [sid], owner)
    selection = live.read(client, merit, "get_selection", [sid])
    definition = selection["definition_hash"]
    state.update({"definition_hash": definition, "fixture_commit_sha": next(iter(fixture_shas)),
                  "candidate_names": [candidate["name"] for candidate in candidates],
                  "criterion_names": [criterion["name"] for criterion in demo["criteria"]]})
    live.save_manifest(state)

    state["pair_margins"] = []
    state["comparison_summaries"] = []
    criterion_id = 1
    for left in range(1, len(candidates) + 1):
        for right in range(left + 1, len(candidates) + 1):
            try:
                comparison = live.read(client, merit, "get_comparison",
                                       [sid, left, right, criterion_id])
            except Exception:
                comparison = {"verdict": INDETERMINATE, "attempts": 0}
            while int(comparison.get("verdict", INDETERMINATE)) == INDETERMINATE:
                attempt = int(comparison.get("attempts", 0))
                if attempt >= 3:
                    state["status"] = "INDETERMINATE"
                    state["incomplete_reason"] = f"retry cap reached for pair {left}/{right}/{criterion_id}"
                    live.save_manifest(state)
                    raise RuntimeError(state["incomplete_reason"])
                label = f"assessment_{left}_{right}_{criterion_id}_{attempt + 1}"
                live.write_once(client, state, label, merit, "assess_pair_criterion",
                                [sid, left, right, criterion_id, definition], owner)
                comparison = live.read(client, merit, "get_comparison",
                                       [sid, left, right, criterion_id])
            verdict = int(comparison.get("verdict", INDETERMINATE))
            state["comparison_summaries"].append({
                "left": left, "right": right, "criterion_id": criterion_id,
                "verdict": {1: "LEFT", 2: "RIGHT", 3: "TIE", 4: "INDETERMINATE"}.get(verdict),
                "attempts": int(comparison.get("attempts", 0)),
                "assessment_hash": comparison.get("hash"),
                "left_quote": comparison.get("left_quote"),
                "right_quote": comparison.get("right_quote"),
                "reason": comparison.get("reason"),
            })
            live.save_manifest(state)
            live.write_once(client, state, f"pair_{left}_{right}", merit, "finalize_pair",
                            [sid, left, right, definition], owner)
            pair = live.read(client, merit, "get_pair", [sid, left, right])
            state.setdefault("pair_margins", []).append({"left": left, "right": right, **pair})
            live.save_manifest(state)

    live.write_once(client, state, "ranking_finalize", merit, "finalize_ranking",
                    [sid, definition], owner)
    result = live.read(client, merit, "get_result", [sid])
    state.update({"ranking_hash": result["ranking_hash"],
                  "winner_candidate_id": result["winner"],
                  "winner_certified": result["winner_certified"],
                  "ordered_candidate_ids": result["ordered_candidate_ids"],
                  "status": "RANKED"})
    if result["winner_certified"]:
        winner = int(result["winner"])
        action = action_hash(sid, definition, result["ranking_hash"], winner)
        live.write_once(client, state, "award_success", gate, "issue_award",
                        [sid, winner, definition, result["ranking_hash"], action], owner)
        state["award_success_tx"] = state["transactions"]["award_success"]["hash"]
        live.write_once(client, state, "award_replay_rejection", gate, "issue_award",
                        [sid, winner, definition, result["ranking_hash"], action], owner,
                        expect_success=False)
        replay = state["transactions"]["award_replay_rejection"]
        state["replay_rejection_evidence"] = {
            "tx_hash": replay["hash"], "execution": replay["execution"],
            "leader_error": live.leader_error(replay["receipt"]),
        }
        wrong_definition = "0" * 64 if definition != "0" * 64 else "1" * 64
        wrong_ranking = "0" * 64 if result["ranking_hash"] != "0" * 64 else "1" * 64
        loser = next(cid for cid in range(1, len(candidates) + 1) if cid != winner)
        for label, candidate, def_hash, rank_hash, action_value, account in (
            ("wrong_definition_rejection", winner, wrong_definition, result["ranking_hash"], "1" * 64, owner),
            ("wrong_ranking_rejection", winner, definition, wrong_ranking, "2" * 64, owner),
            ("loser_rejection", loser, definition, result["ranking_hash"], "3" * 64, owner),
            ("unauthorized_rejection", winner, definition, result["ranking_hash"], "4" * 64, unauthorized),
        ):
            live.write_once(client, state, label, gate, "issue_award",
                            [sid, candidate, def_hash, rank_hash, action_value], account,
                            expect_success=False)
        state["gate_negative_evidence"] = {
            label: {"tx_hash": state["transactions"][label]["hash"],
                    "execution": state["transactions"][label]["execution"],
                    "leader_error": live.leader_error(state["transactions"][label]["receipt"])}
            for label in ("wrong_definition_rejection", "wrong_ranking_rejection",
                          "loser_rejection", "unauthorized_rejection")
        }
        award = live.read(client, gate, "get_award", [2])
        if int(award["selection_id"]) != sid or int(award["candidate_id"]) != winner:
            raise RuntimeError(f"typed gate award record does not match this selection: {award!r}")
        state["award_record"] = live.json_safe(award)
        state["status"] = "VERIFIED"
    else:
        state["status"] = "NO_CERTIFIED_WINNER"
    state["assessment_count"] = live.assessment_tx_count(state)
    transactions = state["transactions"]
    state["creation_tx"] = transactions["selection_create"]["hash"]
    state["criterion_txs"] = [transactions["criterion_1"]["hash"]]
    state["candidate_txs"] = [transactions[f"candidate_{cid}"]["hash"]
                              for cid in range(1, len(candidates) + 1)]
    state["seal_tx"] = transactions["seal_selection"]["hash"]
    state["assessment_txs"] = [transactions[key]["hash"] for key in transactions
                               if key.startswith("assessment_")]
    state["pair_txs"] = [transactions[f"pair_{left}_{right}"]["hash"]
                         for left in range(1, len(candidates) + 1)
                         for right in range(left + 1, len(candidates) + 1)]
    state["ranking_tx"] = transactions["ranking_finalize"]["hash"]
    state["explorer_evidence"] = {key: f"{live.EXPLORER}/tx/{value['hash']}"
                                  for key, value in state["transactions"].items()}
    live.save_manifest(state)
    print(json.dumps({key: state.get(key) for key in (
        "selection_id", "definition_hash", "ranking_hash", "winner_candidate_id",
        "winner_certified", "ordered_candidate_ids", "pair_margins", "assessment_count",
        "award_success_tx", "status")}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FRESH STUDIONET LIFECYCLE INCOMPLETE: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
