"""T03 evidence gate: exact real Drive revisions + synthetic positive cards.

Actual Drive 701 has NO T03 individual Q_OP/A_OP cards; actual L0 has NO
T03 callable interface mappings. The real-state fixture MUST HOLD.
Positive test only proves the adapter accepts well-formed SUPPLIED FIXTURES.
"""
from copy import deepcopy
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from corvan_t03_701_l0_evidence_gate import (
    CONTRACTS_HOME_ID, T03_FUNCTIONS, REGISTRY_701_ID, L0_ID, evaluate_t03
)

R03 = "AHj4eMTc3iWPurGhPbEeuPMswSen83DKRq_O565-AvOTK-tZSTnKqhc61hOSL8jlItCmA6eYygyCvbX5893BJMf726UHutKEf3gAHTrMamQ"
# 08 revision exact sourced from Drive; tests never infer currentness automatically.
R08 = "ANLCKQkwLxOm1qdxrYv9nTRKGKsnG74NAOrYPXVD2u7peJE5zBLOW4HxwJLjfxtzJeB-PsH-jwJHXtUOYn14VbxQo-2BbY2Y1crbG-V8Dj8"
R701 = "ANLCKQm7hENC4zpox2ZHGnMsXG99dIXRvT0Tg0f_lLYPU65BSu6p2vPfY043BaM-n2l4ZVMd2hZNvjnl5ZgpRCRAoOskNYqpdJgMiujfIl8"
RL0 = "AHj4eMS1SOOil11q0IdLBVs3xTtNuAW70pC17xQzC4EguCfJzoiFbM014Fc5Vcr7F0F7KUx8jboiBBD2A5pwu6nOtFbOUV5xqPlVl9wLl4A"


def fixture():
    sources = {}
    cards, bindings = [], []
    for function, docid in T03_FUNCTIONS.items():
        rev = R03 if function.startswith("03") else R08
        sources[function] = {"doc_id": docid, "revision": rev, "parent_id": CONTRACTS_HOME_ID}
        owner = "contract-owner:" + function
        interface = "interface:" + function
        entry = "701-fixture:" + function
        cards.append({
            "function_id": function, "source_document_id": docid, "source_revision": rev,
            "q_op": "LAB ONLY: what does " + function + " decide?",
            "a_op": "LAB ONLY: bounded typed packet " + function,
            "output_schema": "schema:fixture:" + function,
            "registry_entry_ref": entry, "owner_id": owner,
            "primary_home_id": CONTRACTS_HOME_ID, "interface_contract": interface,
            "admission": "VERIFIED_BY_701", "authority": "REFERENCE_ONLY"
        })
        bindings.append({
            "function_id": function, "source_document_id": docid, "source_revision": rev,
            "parent_id": CONTRACTS_HOME_ID, "owner_id": owner,
            "registry_entry_ref": entry, "interface_id": interface,
            "interface_readback_ref": "l0-fixture-readback:" + function,
            "current": True, "status": "VERIFIED_BY_L0"
        })
    return sources, {"document_id": REGISTRY_701_ID, "revision": R701, "cards": cards}, {
        "document_id": L0_ID, "revision": RL0, "bindings": bindings}


def check(v, mission_id="M-T03", correlation_id="C-T03"):
    return evaluate_t03(*v, mission_id=mission_id, correlation_id=correlation_id)


def test_real_701_and_l0_doc_readback_without_cards_stays_blocked():
    sources, registry, l0 = fixture()
    registry["cards"] = []  # This is the actual observed registry state.
    l0["bindings"] = []  # This is the actual observed L0 state.
    got = check((sources, registry, l0))
    assert got["status"] == "HOLD_701_QOP_AOP_SIGNATURE"
    assert got["route_sent"] is False
    assert got["native_execution"] is False


def test_independent_l0_missing_even_with_hypothetical_701_is_hold():
    sources, registry, l0 = fixture()
    l0["bindings"] = []
    assert check((sources, registry, l0))["status"] == "HOLD_L0_INTERFACE"


def test_hypothetical_complete_owner_inputs_make_lab_request_not_route():
    x = check(fixture())
    assert x["status"] == "LAB_ROUTE_REQUEST_ONLY"
    assert x["route_owner"] == "705"
    assert x["trace_kind"] == "PROPOSED_NOT_EXECUTED"
    assert x["authorized_execution"] is False
    assert x["native_execution"] is False
    assert x["route_sent"] is False
    assert x["evidence_status"] == "SUPPLIED_FIXTURE_NOT_AUTHENTICATED"
    assert len(x["owner_bound_edges"]) == 2
    assert "VERIFY_701_CARDS_AGAINST_LIVE_DOC" in x["verification_next"]


@pytest.mark.parametrize("bad", [None, [], {}, 5, ""])
def test_invalid_mission_identity_blocks(bad):
    assert check(fixture(), mission_id=bad)["status"] == "HOLD_MISSION"


@pytest.mark.parametrize("bad", [None, [], {}, 5, ""])
def test_invalid_correlation_identity_blocks(bad):
    assert check(fixture(), correlation_id=bad)["status"] == "HOLD_MISSION"


@pytest.mark.parametrize("mut", [
    lambda s: s.pop("03_MESSAGE_EVENT"),
    lambda s: s["03_MESSAGE_EVENT"].update(revision=""),
    lambda s: s["03_MESSAGE_EVENT"].update(revision="stale"),
])
def test_source_lock_incomplete_or_stale_to_registries_holds(mut):
    v = fixture()
    mut(v[0])
    assert check(v)["status"] in ("HOLD_SOURCE_LOCK", "HOLD_701_STALE")


def test_source_home_must_be_exact():
    v = fixture()
    v[0]["03_MESSAGE_EVENT"]["parent_id"] = "some-other-folder"
    assert check(v)["status"] == "HOLD_SOURCE_LOCK"


def test_source_id_cannot_be_swapped():
    v = fixture()
    v[0]["03_MESSAGE_EVENT"]["doc_id"] = T03_FUNCTIONS["08_FAILURE_RETRY"]
    assert check(v)["status"] == "HOLD_SOURCE_LOCK"


@pytest.mark.parametrize("field,value", [
    ("q_op", ""), ("a_op", None), ("output_schema", ""),
    ("registry_entry_ref", None), ("owner_id", 9), ("interface_contract", ""),
])
def test_701_required_fields_fail_closed(field, value):
    v = fixture()
    v[1]["cards"][0][field] = value
    assert check(v)["status"] == "HOLD_701_QOP_AOP_SIGNATURE"


@pytest.mark.parametrize("mut,expected", [
    (lambda v: v[1].update(document_id="other"), "HOLD_701_QOP_AOP_SIGNATURE"),
    (lambda v: v[1].update(revision=None), "HOLD_701_QOP_AOP_SIGNATURE"),
    (lambda v: v[1]["cards"].pop(), "HOLD_701_QOP_AOP_SIGNATURE"),
    (lambda v: v[1]["cards"].append(deepcopy(v[1]["cards"][0])), "HOLD_701_QOP_AOP_SIGNATURE"),
    (lambda v: v[1]["cards"][1].update(function_id="03_MESSAGE_EVENT"), "HOLD_701_OWNER_COLLISION"),
    (lambda v: v[1]["cards"][0].update(admission="DRAFT"), "HOLD_701_QOP_AOP_SIGNATURE"),
    (lambda v: v[1]["cards"][0].update(authority="EXECUTOR"), "HOLD_701_QOP_AOP_SIGNATURE"),
    (lambda v: v[1]["cards"][0].update(source_revision="OLD_REV"), "HOLD_701_STALE"),
    (lambda v: v[1]["cards"][0].update(primary_home_id="NEXUS"), "HOLD_701_STALE"),
])
def test_701_malformed_or_stale(mut, expected):
    v = fixture()
    mut(v)
    assert check(v)["status"] == expected


@pytest.mark.parametrize("mut,expected", [
    (lambda v: v[2].update(document_id="some-other-l0"), "HOLD_L0_INTERFACE"),
    (lambda v: v[2].update(revision=""), "HOLD_L0_INTERFACE"),
    (lambda v: v[2]["bindings"].pop(), "HOLD_L0_INTERFACE"),
    (lambda v: v[2]["bindings"][1].update(function_id="03_MESSAGE_EVENT"), "HOLD_L0_COLLISION"),
    (lambda v: v[2]["bindings"][0].update(owner_id="invented"), "HOLD_L0_BINDING_MISMATCH"),
    (lambda v: v[2]["bindings"][0].update(interface_id="invented"), "HOLD_L0_BINDING_MISMATCH"),
    (lambda v: v[2]["bindings"][0].update(source_revision="old"), "HOLD_L0_BINDING_MISMATCH"),
    (lambda v: v[2]["bindings"][0].update(registry_entry_ref="bogus"), "HOLD_L0_BINDING_MISMATCH"),
    (lambda v: v[2]["bindings"][0].update(interface_readback_ref=""), "HOLD_L0_INTERFACE"),
    (lambda v: v[2]["bindings"][0].update(current=False), "HOLD_L0_STALE"),
    (lambda v: v[2]["bindings"][0].update(current=1), "HOLD_L0_STALE"),
    (lambda v: v[2]["bindings"][0].update(status="PENDING"), "HOLD_L0_STALE"),
])
def test_l0_wrong_or_stale(mut, expected):
    v = fixture()
    mut(v)
    assert check(v)["status"] == expected


def test_no_input_mutation():
    v = fixture()
    baseline = deepcopy(v)
    check(v)
    assert v == baseline


def test_empty_sources_cannot_be_promoted_by_verified_flag():
    v = fixture()
    v[0] = {}
    assert check(v)["status"] == "HOLD_SOURCE_LOCK"
