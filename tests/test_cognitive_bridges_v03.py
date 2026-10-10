"""Bounded tests for GitHub laboratory adapters (NOT native Casa organs)."""
import os
import sys
from copy import deepcopy
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from corvan_cognitive_bridges_v03 import cog01, cog02, cog03  # noqa: E402


def p1():
    return {"mission_id": "M1", "correlation_id": "C1", "mother_question": "Why?",
            "source_refs": ["src:r1"], "source_state": "CURRENT",
            "claim_class": "OBSERVED", "observations": ["o1"],
            "trigger": "x", "transformation": "extract", "expected_delta": "d",
            "views": ["a", "b"], "ambiguity": True, "probes": [
                {"name": "probe", "legal": True, "discriminates": True,
                 "cost": 1, "estimated_gain": 5}], "probe_budget": 2}


def p2():
    return {"status": "CANDIDATE_ONLY", "mission_id": "M1",
            "correlation_id": "C1", "source_refs": ["src:r1"],
            "function_owners": [{"function": "COGNITIVE_CANDIDATE_GATE",
                                 "owner_id": "owner:01", "interface": "iface:01",
                                 "current": True, "authority": "REFERENCE_ONLY"}]}


def p3():
    return {"mission_id": "M1", "correlation_id": "C1",
            "source_refs": ["src:r1"], "source_state": "CURRENT",
            "return_receipt_ref": "receipt:01", "return_kind": "OBSERVED",
            "qa_ref": "qa:01", "qa_status": "PASS", "claim_rank": 1,
            "evidence_rank": 2}


@pytest.mark.parametrize("mutate,expected", [
    ({"mission_id": ""}, "HOLD_IDENTITY"),
    ({"correlation_id": ""}, "HOLD_IDENTITY"),
    ({"mother_question": ""}, "HOLD_QUESTION"),
    ({"source_refs": []}, "HOLD_SOURCE"),
    ({"source_state": "STALE"}, "HOLD_CURRENTNESS"),
    ({"observations": []}, "HOLD_OBSERVATION"),
    ({"claim_class": "MAGIC"}, "HOLD_CLASSIFICATION"),
    ({"transformation": ""}, "HOLD_FUNCTIONAL_DNA"),
    ({"views": ["only one"]}, "HOLD_REPRESENTATION"),
    ({"contradiction": True, "alternatives": ["one"]}, "HOLD_RIVAL"),
    ({"contradiction": True, "alternatives": ["a", "b"], "probes": []},
     "HOLD_DISCRIMINATOR"),
    ({"source_refs": "not-a-list"}, "HOLD_SCHEMA"),
    ({"probe_budget": "bad"}, "HOLD_SCHEMA"),
    ({"probes": ["not-an-object"]}, "HOLD_SCHEMA"),
    ({"probes": [{"name": "negative", "legal": True,
                   "discriminates": True, "cost": -1, "estimated_gain": 1}]},
     "HOLD_SCHEMA"),
    ({"probes": [{"name": "nan", "legal": True,
                   "discriminates": True, "cost": float("nan"),
                   "estimated_gain": 1}]}, "HOLD_SCHEMA"),
])
def test_cog01_negative(mutate, expected):
    assert cog01(dict(p1(), **mutate))["status"] == expected


@pytest.mark.parametrize("mutate,expected", [
    ({"status": "HOLD_SOURCE"}, "HOLD_UPSTREAM"),
    ({"function_owners": []}, "HOLD_OWNER"),
    ({"function_owners": ["bad"]}, "HOLD_SCHEMA"),
    ({"function_owners": [{"function": [], "owner_id": "o",
                           "interface": "i", "current": True,
                           "authority": "REFERENCE_ONLY"}]}, "HOLD_SCHEMA"),
    ({"function_owners": [{"function": "F", "owner_id": "O",
                           "interface": "", "current": True,
                           "authority": "REFERENCE_ONLY"}]}, "HOLD_INTERFACE"),
    ({"function_owners": [{"function": "F", "owner_id": "O",
                           "interface": "I", "current": False,
                           "authority": "REFERENCE_ONLY"}]}, "HOLD_OWNER_STALE"),
    ({"function_owners": [{"function": "F", "owner_id": "O",
                           "interface": "I", "current": True,
                           "authority": "EXECUTOR"}]}, "BLOCKED_AUTHORITY"),
    ({"function_owners": [p2()["function_owners"][0],
                           p2()["function_owners"][0]]}, "HOLD_COLLISION"),
    ({"execute": True}, "BLOCKED_FALSE_EXECUTION"),
    ({"receipt_observed": True}, "BLOCKED_FALSE_EXECUTION"),
    ({"analogies": ["fake"]}, "HOLD_SCHEMA"),
    ({"analogies": [{"surface_similarity": True}]}, "HOLD_FALSE_ANALOGY"),
])
def test_cog02_negative(mutate, expected):
    assert cog02(dict(p2(), **mutate))["status"] == expected


@pytest.mark.parametrize("mutate,expected", [
    ({"return_receipt_ref": None}, "HOLD_NO_RECEIPT"),
    ({"return_kind": "SIMULATED"}, "HOLD_NO_RECEIPT"),
    ({"qa_ref": None}, "HOLD_QA"),
    ({"qa_status": "FAIL"}, "HOLD_QA"),
    ({"source_state": "STALE"}, "HOLD_SOURCE"),
    ({"claim_rank": 5, "evidence_rank": 1}, "BLOCKED_TRUTH_INFLATION"),
    ({"claim_rank": "high"}, "HOLD_SCHEMA"),
    ({"canon": True}, "BLOCKED_AUTHORITY"),
    ({"executed_by": "COG03"}, "BLOCKED_AUTHORITY"),
    ({"episodes": ["bad"]}, "HOLD_SCHEMA"),
    ({"episodes": [{"case_id": "c", "observed": "yes",
                    "qa_pass": True}]}, "HOLD_SCHEMA"),
])
def test_cog03_negative(mutate, expected):
    assert cog03(dict(p3(), **mutate))["status"] == expected


def test_valid_chain_bounded():
    one = cog01(p1())
    assert one["status"] == "CANDIDATE_ONLY"
    assert one["probe_request"] == "probe"
    two = cog02(dict(p2(), status=one["status"], source_refs=one["source_refs"]))
    assert two["status"] == "ROUTE_REQUEST_ONLY"
    assert two["route_owner"] == "705"
    assert two["trace_kind"] == "PROPOSED_NOT_EXECUTED"
    three = cog03(p3())
    assert three["status"] == "OUTPUT_REQUEST_ONLY"
    assert three["output_owner"] == "05_OUT"
    for result in (one, two, three):
        assert result["native_execution"] is False
        assert result["authorized_execution"] is False


def test_no_procedural_promotion_from_one_episode():
    p = p3()
    p["episodes"] = [{"case_id": "same", "observed": True, "qa_pass": True}]
    assert cog03(p)["learning_note"] == "NO_PROCEDURAL_LEARNING"


def test_learning_review_not_authorization():
    p = p3()
    p["episodes"] = [{"case_id": "case-A", "observed": True, "qa_pass": True},
                     {"case_id": "case-B", "observed": True, "qa_pass": True}]
    result = cog03(p)
    assert result["learning_note"] == "CF8_REVIEW_CANDIDATE"
    assert result["authorized_execution"] is False


def test_untrusted_packet_never_mutated():
    p = p1()
    before = deepcopy(p)
    cog01(p)
    assert p == before


@pytest.mark.parametrize("fn", [cog01, cog02, cog03])
def test_non_mapping_blocked(fn):
    result = fn(None)
    assert result["status"] == "HOLD_SCHEMA"
    assert result["native_execution"] is False
