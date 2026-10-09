"""Proof of fail-closed discovery for random requested opcode 50.

These test the locator and authority gates ONLY, not hypothetical opcode 50.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from corvan_opcode_source_discovery_gate import assess_opcode_primary_source  # noqa: E402


def candidate(**changes):
    base = {"title": "50_C_CORVAN_TEST_FIXTURE", "document_id": "fixture-doc",
            "revision": "fixture-revision", "primary_body_readback": True,
            "owner": "fixture-owner", "contract_ref": "fixture-contract"}
    base.update(changes)
    return base


def test_random_50_not_discovered_in_recovered_source_candidates():
    # The names below were observed in early archival lookup; none is opcode 50.
    observed_names = [
        "40_C_CORVAN_EXECUTABLE_INSTALL_TRUTH_HARNESS_STALE_HUMAN_LABEL_NO_DEGRADE_GATE_v1_0",
        "56_CORVAN_WINSTON_REPRESENTATION_STORY_CLARITY_ENGINE_LIVING_OPCODE_v1.0",
        "58_CORVAN_ANALYTIC_FRACTURE_CORE_FUNCTIONAL_INTELLIGENCE_OPCODE_v1.0",
        "3507_S_CORVAN_BLIND_FULL_CYCLE_MULTI_BRANCH_FORENSIC_CONSENSUS_NOISE_FILTER",
        "701_C_CORVAN_BROTHER_OPERATIONAL_INVENTORY",
        "M50_EXPLAINABLE_MATCH_TRACE_BUILDER",
    ]
    result = assess_opcode_primary_source(50, [{"title": x} for x in observed_names])
    assert result["status"] == "HOLD_SOURCE_NOT_LOCATED"
    assert result["tested_original"] is False


def test_empty_source_set_does_not_prove_slot_free():
    result = assess_opcode_primary_source(50, [])
    assert result["status"] == "HOLD_SOURCE_NOT_LOCATED"
    assert "FREE" not in result["status"]


@pytest.mark.parametrize("value", [None, "50", True, -1, 10000, 50.0])
def test_invalid_number_never_accepted(value):
    result = assess_opcode_primary_source(value, [])
    assert result["status"] == "BLOCKED_INVALID_NUMBER"


@pytest.mark.parametrize("value", [None, "not-list", {"title": "50_CORVAN_X"}, [None]])
def test_malformed_candidates_fail_closed(value):
    result = assess_opcode_primary_source(50, value)
    assert result["status"] == "HOLD_DISCOVERY_INPUT"


@pytest.mark.parametrize("name", [
    "150_C_CORVAN_OTHER", "3507_S_CORVAN_NOT_50", "M50_CORVAN_MODULE",
    "701_M50_EXPLAINABLE_MATCH_TRACE_BUILDER", "50 is mentioned somewhere",
    "40_C_CORVAN_REPORT_M50", "056_CORVAN_DIFFERENT"
])
def test_wrong_titles_do_not_alias_number_50(name):
    result = assess_opcode_primary_source(50, [{"title": name}])
    assert result["status"] == "HOLD_SOURCE_NOT_LOCATED"


def test_multiple_matching_historic_sources_are_collision_not_certainty():
    result = assess_opcode_primary_source(50, [
        candidate(title="50_C_CORVAN_ALPHA"),
        candidate(title="50_O_CORVAN_BETA"),
    ])
    assert result["status"] == "HOLD_NUMERIC_COLLISION"
    assert result["matches"] == 2


@pytest.mark.parametrize("patch,expected", [
    ({"document_id": None}, "HOLD_SOURCE_IDENTITY"),
    ({"revision": None}, "HOLD_SOURCE_IDENTITY"),
    ({"primary_body_readback": False}, "HOLD_PRIMARY_BODY"),
    ({"owner": None}, "HOLD_OWNER_OR_CONTRACT"),
    ({"contract_ref": None}, "HOLD_OWNER_OR_CONTRACT"),
])
def test_title_alone_is_insufficient(patch, expected):
    assert assess_opcode_primary_source(50, [candidate(**patch)])["status"] == expected


def test_synthetic_full_source_only_reaches_test_design():
    result = assess_opcode_primary_source(50, [candidate()])
    assert result["status"] == "READY_TO_DESIGN_FUNCTIONAL_TESTS"
    assert result["tested_original"] is False
    assert "not yet exercised" in result["claim"]


def test_zero_padded_historic_number_is_distinct_from_neighbor():
    r = assess_opcode_primary_source(50, [candidate(title="0050_C_CORVAN_TEST_FIXTURE")])
    assert r["status"] == "READY_TO_DESIGN_FUNCTIONAL_TESTS"
    assert r["tested_original"] is False
