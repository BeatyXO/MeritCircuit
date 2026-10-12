"""Deterministic test double for GenVM APIs.

These tests are OFFLINE PROTOCOL tests, not GenLayer Direct Mode tests and do
not simulate economic finality or substitute for a real validator set.
"""
import hashlib
import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


class FakeStorage(dict):
    @classmethod
    def __class_getitem__(cls, arg):
        return cls


class FakeEvent:
    def __init__(self, *args, **kwargs):
        pass

    def emit(self):
        pass


class UserError(Exception):
    pass


class FakeReturn:
    def __init__(self, calldata):
        self.calldata = calldata


class FakeVM:
    Return = FakeReturn
    UserError = UserError

    def run_nondet_unsafe(self, leader, validator):
        value = leader()
        if not validator(FakeReturn(value)):
            raise UserError("validator rejected leader")
        return value


class ScriptedWeb:
    def __init__(self):
        self.docs = {}
        self.reads = []

    def render(self, url, mode="text"):
        self.reads.append(url)
        return self.docs[url]


class ScriptedLLM:
    def __init__(self, web):
        self.web = web
        self.overrides = []

    def exec_prompt(self, prompt, response_format="json"):
        if self.overrides:
            return self.overrides.pop(0)
        data = json.loads(prompt[prompt.index('{"criterion"'):])
        first = data["first"]["source"].split(":", 1)[0].split(" ", 1)[0]
        second = data["second"]["source"].split(":", 1)[0].split(" ", 1)[0]
        rubric = data["criterion"]
        if rubric == "feasibility":
            ratings = {"Alpha": 3, "Beta": 2, "Gamma": 1}
        else:
            ratings = {"Gamma": 3, "Alpha": 2, "Beta": 1}
        verdict = "LEFT" if ratings[first] > ratings[second] else "RIGHT" if ratings[second] > ratings[first] else "TIE"
        return json.dumps({"verdict": verdict, "reason": "grounded in provided material",
                           "left_quote": data["first"]["source"][:32],
                           "right_quote": data["second"]["source"][:32]})


@pytest.fixture
def env(monkeypatch):
    mod = types.ModuleType("genlayer")
    class Public:
        @staticmethod
        def write(fn):
            return fn
        @staticmethod
        def view(fn):
            return fn
    class Contract:
        pass
    class GL:
        pass
    gl = GL()
    gl.Contract = Contract
    gl.public = Public
    gl.Event = FakeEvent
    gl.contract_interface = lambda cls: cls
    gl.vm = FakeVM()
    gl.message = types.SimpleNamespace(sender_address="owner")
    web = ScriptedWeb()
    llm = ScriptedLLM(web)
    gl.nondet = types.SimpleNamespace(web=web, exec_prompt=llm.exec_prompt)
    mod.gl = gl
    mod.Address = str
    mod.TreeMap = FakeStorage
    mod.DynArray = list
    mod.allow_storage = lambda cls: cls
    mod.u8 = int
    mod.u32 = int
    mod.u256 = int
    mod.i32 = int
    mod.Keccak256 = lambda b: hashlib.sha3_256(b)
    # Event subclasses refer to gl.Event, __init__ in base is inherited.
    monkeypatch.setitem(sys.modules, "genlayer", mod)
    for name, file in [("merit_circuit", "merit_circuit.py"), ("merit_award_gate", "merit_award_gate.py")]:
        spec = importlib.util.spec_from_file_location(name, ROOT / "contracts" / file)
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, name, module)
        spec.loader.exec_module(module)
        if name == "merit_circuit":
            merit_mod = module
        else:
            gate_mod = module
    contract = merit_mod.MeritCircuit()
    for attr in ("selections", "candidates", "criteria", "comparisons", "assessment_history", "pairs", "rank_slots"):
        setattr(contract, attr, FakeStorage())
    for name in ("Alpha", "Beta", "Gamma"):
        web.docs[f"https://raw.githubusercontent.com/example/merit-demo/abcdef/{name}.md"] = (
            f"{name}: public and independently retrievable substantive record. "
            f"Detailed review evidence for the selection rubric and quantitative project context."
        )
    return types.SimpleNamespace(contract=contract, merit=merit_mod, gate=gate_mod, gl=gl, web=web, llm=llm)


@pytest.fixture
def selection(env):
    c = env.contract
    sid = c.create_selection("Technical grants", "Compare feasible useful open source proposals",
                              "raw.githubusercontent.com")
    c.add_criterion(sid, "feasibility", "Evaluate feasibility using published technical proof", 60)
    c.add_criterion(sid, "impact", "Evaluate tangible expected ecosystem usefulness", 40)
    for name in ("Alpha", "Beta", "Gamma"):
        c.add_candidate(sid, name, f"{name} proposes an ecosystem tool",
                        f"https://raw.githubusercontent.com/example/merit-demo/abcdef/{name}.md")
    h = c.seal_selection(sid)
    return sid, h
