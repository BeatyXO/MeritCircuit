#!/usr/bin/env python3
"""Finish every still-resolvable pair on the current live selection.

This runner never retries a decisive result or exceeds the contract's three
INDETERMINATE attempts. It continues past a stalled pair so unrelated pair
evidence can still be finalized; it ranks only if the matrix is complete.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scripts.live_studionet as live

INDETERMINATE = 4


def main():
    key = os.environ.get("GENLAYER_PRIVATE_KEY")
    if not key:
        raise SystemExit("GENLAYER_PRIVATE_KEY is required in the process environment")
    from genlayer_py import create_account

    client = live.make_client(create_account(key))
    account = create_account(key)
    live.confirm_network(client)
    state = live.load_json(live.MANIFEST_PATH)
    sid = int(state["selection_id"])
    merit = state["merit_circuit_address"]
    definition = state["definition_hash"]
    demo = live.load_json(live.DEMO_PATH)
    candidate_count = len(demo["candidates"])
    criterion_count = len(demo["criteria"])
    transactions = state.setdefault("transactions", {})

    for left in range(1, candidate_count + 1):
        for right in range(left + 1, candidate_count + 1):
            if f"pair_{left}_{right}" in transactions:
                continue
            pair_complete = True
            for criterion_id in range(1, criterion_count + 1):
                try:
                    comparison = live.read(client, merit, "get_comparison",
                                           [sid, left, right, criterion_id])
                except Exception:
                    comparison = None
                while comparison is None or int(comparison.get("verdict", INDETERMINATE)) == INDETERMINATE:
                    attempt = int(comparison.get("attempts", 0)) if comparison else 0
                    if attempt >= 3:
                        pair_complete = False
                        state.setdefault("stalled_criteria", []).append({
                            "left": left, "right": right, "criterion_id": criterion_id,
                            "attempts": attempt,
                            "reason": comparison.get("reason") if comparison else "assessment missing",
                        })
                        live.save_manifest(state)
                        break
                    label = f"assessment_{left}_{right}_{criterion_id}_{attempt + 1}"
                    live.write_once(client, state, label, merit, "assess_pair_criterion",
                                    [sid, left, right, criterion_id, definition], account)
                    comparison = live.read(client, merit, "get_comparison",
                                           [sid, left, right, criterion_id])
                if not pair_complete:
                    break
            if pair_complete:
                label = f"pair_{left}_{right}"
                live.write_once(client, state, label, merit, "finalize_pair",
                                [sid, left, right, definition], account)
                pair = live.read(client, merit, "get_pair", [sid, left, right])
                state.setdefault("pair_margins", []).append(
                    {"left": left, "right": right, **pair}
                )
                live.save_manifest(state)

    selection = live.read(client, merit, "get_selection", [sid])
    state["finalized_pair_count"] = int(selection["finalized_pairs"])
    state["assessment_count"] = live.assessment_tx_count(state)
    if int(selection["finalized_pairs"]) == int(selection["pair_count"]):
        if "ranking_finalize" not in transactions:
            live.write_once(client, state, "ranking_finalize", merit, "finalize_ranking",
                            [sid, definition], account)
        result = live.read(client, merit, "get_result", [sid])
        state.update({"ranking_hash": result["ranking_hash"],
                      "winner_candidate_id": result["winner"],
                      "winner_certified": result["winner_certified"],
                      "ordered_candidate_ids": result["ordered_candidate_ids"],
                      "status": "RANKED"})
    else:
        state["status"] = "INDETERMINATE"
        state["incomplete_reason"] = "At least one criterion reached the fixed INDETERMINATE retry cap"
    live.save_manifest(state)
    print(json.dumps({"selection_id": sid, "finalized_pairs": state["finalized_pair_count"],
                      "pair_count": int(selection["pair_count"]),
                      "stalled_criteria": state.get("stalled_criteria", []),
                      "pair_margins": state.get("pair_margins", []),
                      "ranking_hash": state.get("ranking_hash")}, indent=2))


if __name__ == "__main__":
    main()
