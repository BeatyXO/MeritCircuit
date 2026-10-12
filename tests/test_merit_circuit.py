import json
import pytest


def complete_all(env, sid, definition):
    c = env.contract
    for a, b in [(1, 2), (1, 3), (2, 3)]:
        for crit in (1, 2):
            assert c.assess_pair_criterion(sid, a, b, crit, definition) in (1, 2, 3)
        c.finalize_pair(sid, a, b, definition)


def test_lifecycle_and_deterministic_ranking(env, selection):
    sid, h = selection
    c = env.contract
    assert len(h) == 64
    complete_all(env, sid, h)
    rank_hash = c.finalize_ranking(sid, h)
    result = c.get_result(sid)
    assert result["ordered_candidate_ids"] == [1, 2, 3]
    assert c.is_ranked_winner(sid, 1, h, rank_hash)
    assert not c.is_ranked_winner(sid, 2, h, rank_hash)
    assert not c.is_ranked_winner(sid, 1, "0" * 64, rank_hash)
    assert not c.is_ranked_winner(sid, 1, h, "0" * 64)
    with pytest.raises(Exception, match="not sealed"):
        c.finalize_ranking(sid, h)
    assert len(env.web.reads) >= 24  # independent validator rerenders + mirrored checks


def test_creation_and_seal_preconditions(env):
    c = env.contract
    sid = c.create_selection("A", "B", "raw.githubusercontent.com")
    with pytest.raises(Exception, match="need 2"):
        c.seal_selection(sid)
    with pytest.raises(Exception, match="source host mismatch"):
        c.add_candidate(sid, "Name", "Summary", "https://malicious.example/path")
    with pytest.raises(Exception, match="invalid weight"):
        c.add_criterion(sid, "P", "Rubric", 101)
    c.add_criterion(sid, "P", "Rubric", 99)
    for i in range(2):
        c.add_candidate(sid, f"Name{i}", "Summary", "https://raw.githubusercontent.com/x/y/blob")
    with pytest.raises(Exception, match="exactly 100"):
        c.seal_selection(sid)
    c.add_criterion(sid, "Q", "Rubric", 1)
    h = c.seal_selection(sid)
    assert len(h) == 64
    with pytest.raises(Exception, match="closed"):
        c.add_candidate(sid, "Other", "Other", "https://raw.githubusercontent.com/x/y/new")


def test_owner_isolation(env):
    c = env.contract
    sid = c.create_selection("A", "B", "raw.githubusercontent.com")
    env.gl.message.sender_address = "intruder"
    with pytest.raises(Exception, match="only selection owner"):
        c.add_criterion(sid, "P", "Rubric", 100)


def test_fail_closed_before_completeness(env, selection):
    sid, h = selection
    c = env.contract
    with pytest.raises(Exception, match="matrix incomplete"):
        c.finalize_ranking(sid, h)
    with pytest.raises(Exception, match="missing comparison"):
        c.finalize_pair(sid, 1, 2, h)
    with pytest.raises(Exception, match="definition mismatch"):
        c.assess_pair_criterion(sid, 1, 2, 1, "f" * 64)
    with pytest.raises(Exception, match="invalid ordered pair"):
        c.assess_pair_criterion(sid, 2, 1, 1, h)
    assert c.assess_pair_criterion(sid, 1, 2, 1, h) == 1
    with pytest.raises(Exception, match="already decisive"):
        c.assess_pair_criterion(sid, 1, 2, 1, h)


def test_reject_forged_leader_and_unsupported_quotes(env, selection):
    sid, h = selection
    c = env.contract
    # Both direct and mirror replies claim evidence they did not fetch.
    forged = json.dumps({"verdict": "LEFT", "reason": "fictional", "left_quote": "FAKE PROOF", "right_quote": "NOT IN SOURCE"})
    env.llm.overrides = [forged, forged]
    with pytest.raises(Exception, match="validator rejected leader"):
        c.assess_pair_criterion(sid, 1, 2, 1, h)
    assert c.assess_pair_criterion(sid, 1, 2, 1, h) == 1
    assert c.get_comparison(sid, 1, 2, 1)["attempts"] == 1


def test_mirrored_order_inconsistency_is_indeterminate(env, selection):
    sid, h = selection
    c = env.contract
    a = env.web.docs["https://raw.githubusercontent.com/example/merit-demo/abcdef/Alpha.md"][:32]
    b = env.web.docs["https://raw.githubusercontent.com/example/merit-demo/abcdef/Beta.md"][:32]
    first = json.dumps({"verdict": "LEFT", "reason": "first", "left_quote": a, "right_quote": b})
    # On mirrored prompt RIGHT should be asserted, so LEFT is inconsistent.
    second = json.dumps({"verdict": "LEFT", "reason": "second", "left_quote": b, "right_quote": a})
    env.llm.overrides = [first, second]
    with pytest.raises(Exception, match="validator rejected leader"):
        c.assess_pair_criterion(sid, 1, 2, 1, h)


def test_mirror_failure_is_diagnosed_without_accepting_biased_vote(env, selection):
    sid, _ = selection
    c = env.contract
    left = c._candidate(sid, 1)
    right = c._candidate(sid, 2)
    criterion = c._criterion(sid, 1)
    left_quote = env.web.docs[left.evidence_url][:32]
    right_quote = env.web.docs[right.evidence_url][:32]
    env.llm.overrides = [
        json.dumps({"verdict": "LEFT", "reason": "left evidence stronger",
                    "left_quote": left_quote, "right_quote": right_quote}),
        json.dumps({"verdict": "LEFT", "reason": "same side after swap",
                    "left_quote": right_quote, "right_quote": left_quote}),
    ]
    result = env.merit.classify_independently(left, right, criterion)
    assert result["verdict"] == env.merit.INDETERMINATE
    assert result["reason"] == "mirrored verdict inconsistency"


def test_retries_bounded_and_history_preserved(env, selection):
    sid, h = selection
    c = env.contract
    # force source outage to get inconclusive without model
    url = c.get_candidate(sid, 1)["url"]
    del env.web.docs[url]
    for attempt in range(1, 4):
        assert c.assess_pair_criterion(sid, 1, 2, 1, h) == 4
        assert c.get_comparison(sid, 1, 2, 1)["attempts"] == attempt
    assert len([k for k in c.assessment_history if k.startswith(f"{sid}:1:2:1:")]) == 3
    with pytest.raises(Exception, match="retry cap"):
        c.assess_pair_criterion(sid, 1, 2, 1, h)


def test_weighted_margins(env, selection):
    sid, h = selection
    c = env.contract
    for cid in (1, 2):
        c.assess_pair_criterion(sid, 1, 3, cid, h)
    assert c.finalize_pair(sid, 1, 3, h) == 20
    p = c.get_pair(sid, 1, 3)
    assert p == {"margin": 20, "left_support": 60, "right_support": 40}
    with pytest.raises(Exception, match="finalized"):
        c.finalize_pair(sid, 1, 3, h)


def test_ranked_pairs_cycle_is_deterministically_broken(env):
    rank = env.merit.ranked_pairs_order(3, [(1, 2, 40, 70, 30),
                                            (1, 3, -40, 30, 70),
                                            (2, 3, 40, 70, 30)])
    assert len(rank["locked"]) == 2
    assert len(rank["skipped"]) == 1
    assert rank["order"] == [1, 2, 3]
    assert rank == env.merit.ranked_pairs_order(3, [(1, 2, 40, 70, 30),
                                                    (1, 3, -40, 30, 70),
                                                    (2, 3, 40, 70, 30)])


def test_all_ties_resolve_by_candidate_id(env):
    rank = env.merit.ranked_pairs_order(3, [(1, 2, 0, 0, 0),
                                            (1, 3, 0, 0, 0),
                                            (2, 3, 0, 0, 0)])
    assert rank["order"] == [1, 2, 3]
    assert not rank["locked"]


def test_gate_pins_both_hashes_and_replay(env, selection):
    sid, h = selection
    complete_all(env, sid, h)
    ranking_hash = env.contract.finalize_ranking(sid, h)
    env.gl.message.sender_address = "owner"
    gate = env.gate.MeritAwardGate("merit-deployment")
    gate.used_actions = {}
    gate.awards = {}
    # mock typed interface uses the SAME signature as production contract.
    class Adapter:
        def __init__(self, address):
            assert address == "merit-deployment"
        def view(self):
            return env.contract
    env.gate.IMeritCircuit = Adapter
    action = "a" * 64
    with pytest.raises(Exception, match="lowercase 32-byte hex"):
        gate.issue_award(sid, 1, h, ranking_hash, "A" * 64)
    with pytest.raises(Exception, match="lowercase 32-byte hex"):
        gate.issue_award(sid, 1, h, ranking_hash, "g" * 64)
    assert gate.issue_award(sid, 1, h, ranking_hash, action) == 1
    assert gate.get_award(1)["candidate_id"] == 1
    with pytest.raises(Exception, match="replay"):
        gate.issue_award(sid, 1, h, ranking_hash, action)
    with pytest.raises(Exception, match="pinned ranking"):
        gate.issue_award(sid, 1, h, "1" * 64, "b" * 64)
    with pytest.raises(Exception, match="pinned ranking"):
        gate.issue_award(sid, 2, h, ranking_hash, "c" * 64)
    env.gl.message.sender_address = "intruder"
    with pytest.raises(Exception, match="only gate owner"):
        gate.issue_award(sid, 1, h, ranking_hash, "d" * 64)


def test_cycle_ranks_but_never_certifies_award(env):
    c = env.contract
    sid = c.create_selection("Cycle", "The social-choice cycle regression", "raw.githubusercontent.com")
    c.add_criterion(sid, "feasibility", "Compare only feasibility", 100)
    for name in ("Alpha", "Beta", "Gamma"):
        c.add_candidate(sid, name, name + " record", f"https://raw.githubusercontent.com/example/merit-demo/abcdef/{name}.md")
    h = c.seal_selection(sid)
    def cycle_llm(prompt, response_format="json"):
        data = json.loads(prompt[prompt.index('{"criterion"'):])
        a = data["first"]["source"].split(":", 1)[0].split(" ", 1)[0]
        b = data["second"]["source"].split(":", 1)[0].split(" ", 1)[0]
        cyclic = {("Alpha", "Beta"), ("Beta", "Gamma"), ("Gamma", "Alpha")}
        verdict = "LEFT" if (a, b) in cyclic else "RIGHT"
        return json.dumps({"verdict": verdict, "reason": "synthetic cyclic preference",
                           "left_quote": data["first"]["source"][:32],
                           "right_quote": data["second"]["source"][:32]})
    env.gl.nondet.exec_prompt = cycle_llm
    for a, b in ((1, 2), (1, 3), (2, 3)):
        assert c.assess_pair_criterion(sid, a, b, 1, h) != 4
        c.finalize_pair(sid, a, b, h)
    rh = c.finalize_ranking(sid, h)
    result = c.get_result(sid)
    assert not result["winner_certified"]
    assert not c.is_ranked_winner(sid, result["winner"], h, rh)


def test_equal_pairs_rank_but_no_award(env):
    c = env.contract
    sid = c.create_selection("Tie", "Pairwise tie regression", "raw.githubusercontent.com")
    c.add_criterion(sid, "feasibility", "Compare only feasibility", 100)
    for name in ("Alpha", "Beta"):
        c.add_candidate(sid, name, name + " record", f"https://raw.githubusercontent.com/example/merit-demo/abcdef/{name}.md")
    h = c.seal_selection(sid)
    def tie_llm(prompt, response_format="json"):
        data = json.loads(prompt[prompt.index('{"criterion"'):])
        return json.dumps({"verdict": "TIE", "reason": "same qualitative class",
                           "left_quote": data["first"]["source"][:32],
                           "right_quote": data["second"]["source"][:32]})
    env.gl.nondet.exec_prompt = tie_llm
    c.assess_pair_criterion(sid, 1, 2, 1, h)
    assert c.finalize_pair(sid, 1, 2, h) == 0
    rh = c.finalize_ranking(sid, h)
    assert c.get_result(sid)["ordered_candidate_ids"] == [1, 2]
    assert c.get_result(sid)["winner_certified"] is False
    assert not c.is_ranked_winner(sid, 1, h, rh)


def test_reject_numeric_local_source_host(env):
    c = env.contract
    with pytest.raises(Exception, match="invalid source host"):
        c.create_selection("Bad", "Blocked localhost alias", "127.0.0.1")
    with pytest.raises(Exception, match="invalid source host"):
        c.create_selection("Bad", "Blocked internal hostname", "server.internal")


@pytest.mark.parametrize("host", [
    "127.0.0.1", "10.0.0.1", "2130706433", "0x7f000001", "example..com",
    "-bad.example", "bad-.example", "example.1", "example.localhost",
    "example:443", "example.com.", "例え.テスト",
])
def test_reject_ambiguous_or_nonpublic_source_hosts(env, host):
    with pytest.raises(Exception, match="invalid source host"):
        env.contract.create_selection("Bad", "Reject host ambiguity", host)


@pytest.mark.parametrize("url", [
    "https://user@raw.githubusercontent.com/a/b.md",
    "https://raw.githubusercontent.com:443/a/b.md",
    "https://raw.githubusercontent.com:bad/a/b.md",
    "https://raw.githubusercontent.com./a/b.md",
    "https://raw.githubusercontent.com\\@evil.example/a/b.md",
])
def test_reject_ambiguous_source_authorities(env, url):
    c = env.contract
    sid = c.create_selection("URLs", "Only exact registered authority", "raw.githubusercontent.com")
    with pytest.raises(Exception):
        c.add_candidate(sid, "A", "Summary", url)


def test_duplicate_json_keys_fail_closed(env):
    vote = env.merit.parse_vote(
        '{"verdict":"LEFT","verdict":"RIGHT","reason":"x",'
        '"left_quote":"a","right_quote":"b"}'
    )
    assert vote["verdict"] == env.merit.INDETERMINATE
    fenced = env.merit.parse_vote('```json\n{"verdict":"LEFT"}\n```')
    assert fenced["verdict"] == env.merit.INDETERMINATE


@pytest.mark.parametrize("weight", [-1, 0, 101, 2**32, 2**256 - 1])
def test_reject_nonpositive_overflow_and_out_of_range_weights(env, weight):
    c = env.contract
    sid = c.create_selection("Weights", "Positive bounded integer weights", "raw.githubusercontent.com")
    with pytest.raises(Exception, match="invalid weight"):
        c.add_criterion(sid, "Criterion", "A valid rubric", weight)


def test_candidate_and_criterion_caps_and_sealed_source_freeze(env):
    c = env.contract
    sid = c.create_selection("Bounds", "Fixed size candidate set", "raw.githubusercontent.com")
    c.add_criterion(sid, "C1", "Criterion one", 100)
    for i in range(8):
        c.add_candidate(sid, f"C{i}", "bounded summary",
                        f"https://raw.githubusercontent.com/x/y/{i}.md")
    with pytest.raises(Exception, match="closed or full"):
        c.add_candidate(sid, "C9", "too many", "https://raw.githubusercontent.com/x/y/9.md")
    c.seal_selection(sid)
    with pytest.raises(Exception, match="already sealed"):
        c.add_criterion(sid, "C2", "Post-seal rubric replacement", 1)
    with pytest.raises(Exception, match="closed or full"):
        c.add_candidate(sid, "Replacement", "source substitution", "https://raw.githubusercontent.com/x/y/new.md")
    sid2 = c.create_selection("Criteria", "Fixed rubric count", "raw.githubusercontent.com")
    for i in range(6):
        c.add_criterion(sid2, f"C{i}", "bounded rubric", 1)
    with pytest.raises(Exception, match="too many criteria"):
        c.add_criterion(sid2, "C6", "seventh rubric", 94)


def test_owner_summary_is_not_model_evidence(env, selection):
    sid, _ = selection
    left = env.contract._candidate(sid, 1)
    right = env.contract._candidate(sid, 2)
    criterion = env.contract._criterion(sid, 1)
    prompt = env.merit.prompt_for(left, right, criterion, "source one", "source two", False)
    mirrored = env.merit.prompt_for(right, left, criterion, "source two", "source one", True)
    assert "source one" in prompt and "source two" in prompt
    assert "displayed order is arbitrary" in prompt
    assert "extracts are swapped" in mirrored
    assert left.summary not in prompt and right.summary not in prompt
