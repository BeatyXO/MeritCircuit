# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""A typed, replay-protected downstream consumer of MeritCircuit.

No tokens or funds are transferred. An award record represents one approved action.
"""
from genlayer import *
from dataclasses import dataclass


@gl.contract_interface
class IMeritCircuit:
    class View:
        def is_ranked_winner(self, selection_id: u256, candidate_id: u32,
                             expected_definition_hash: str, expected_ranking_hash: str) -> bool: ...
        def get_result(self, selection_id: u256) -> dict: ...

    class Write:
        pass


@allow_storage
@dataclass
class Award:
    selection_id: u256
    candidate_id: u32
    action_hash: str
    definition_hash: str
    ranking_hash: str
    operator: Address


class MeritAwardGate(gl.Contract):
    merit_circuit_address: Address
    owner: Address
    award_count: u256
    used_actions: TreeMap[str, bool]
    awards: TreeMap[u256, Award]

    def __init__(self, merit_circuit_address: Address):
        self.merit_circuit_address = merit_circuit_address
        self.owner = gl.message.sender_address
        self.award_count = u256(0)

    @gl.public.write
    def issue_award(self, selection_id: u256, candidate_id: u32,
                    expected_definition_hash: str, expected_ranking_hash: str,
                    action_hash: str) -> u256:
        if gl.message.sender_address != self.owner:
            raise gl.vm.UserError("only gate owner may issue an award")
        if len(action_hash) != 64 or any(c not in "0123456789abcdef" for c in action_hash):
            raise gl.vm.UserError("action hash must be lowercase 32-byte hex")
        if action_hash in self.used_actions and self.used_actions[action_hash]:
            raise gl.vm.UserError("action replay")
        merit = IMeritCircuit(self.merit_circuit_address)
        if not merit.view().is_ranked_winner(selection_id, candidate_id,
                                            expected_definition_hash, expected_ranking_hash):
            raise gl.vm.UserError("pinned ranking does not authorize this candidate")
        award_id = u256(int(self.award_count) + 1)
        self.used_actions[action_hash] = True
        self.awards[award_id] = Award(selection_id, candidate_id, action_hash,
                                      expected_definition_hash, expected_ranking_hash,
                                      gl.message.sender_address)
        self.award_count = award_id
        return award_id

    @gl.public.view
    def get_award(self, award_id: u256) -> dict:
        if not 0 < int(award_id) <= int(self.award_count):
            raise gl.vm.UserError("unknown award")
        a = self.awards[award_id]
        return {"selection_id": int(a.selection_id), "candidate_id": int(a.candidate_id),
                "action_hash": a.action_hash, "definition_hash": a.definition_hash,
                "ranking_hash": a.ranking_hash, "operator": str(a.operator)}
