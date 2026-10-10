"""T03 exact 03+08 evidence-gate tests. No native owner is invoked."""
import copy
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from corvan_t03_signature_admission import admit_t03, SOURCES, REGISTRY_ID, L0_ID
from corvan_cognitive_bridges_v03 import cog02


@pytest.fixture
def d():
    sources = {
        k: {"doc_id": doc_id, "revision": "rev-" + k,
            "family_home": "L_SHARED_CONTRACTS"}
        for k, doc_id in SOURCES.items()
    }
    registry = {"doc_id": REGISTRY_ID, "revision": "reg-r1"}
    l0 = {"doc_id": L0_ID, "revision": "l0-r1"}
    cards = {
        k: {"doc_id": SOURCES[k], "source_revision": "rev-" + k,
            "registry_revision": "reg-r1",
            "function_signature": {"03": "message_event_contract", "08": "failure_retry_policy"}[k],
            "q_op": "bounded operational question from source",
            "a_op": "typed answer proposal from source", "owner_id": "contracts:" + k,
            "primary_home": "L_SHARED_CONTRACTS",
            "search_route": "current Home via L0", "output_schema": "typed packet"}
        for k in SOURCES
    }
    bindings = {
        k: {"doc_id": SOURCES[k], "source_revision": "rev-" + k,
            "registry_revision": "reg-r1", "l0_revision": "l0-r1",
            "function_signature": cards[k]["function_signature"],
            "owner_id": cards[k]["owner_id"], "home": "L_SHARED_CONTRACTS",
            "interface": "mock-only:route:" + k,
            "return_expectation": "mock:ACK",
            "current": True, "authority": "REFERENCE_ONLY"}
        for k in SOURCES
    }
    candidate = {"status": "CANDIDATE_ONLY", "mission_id": "m", "correlation_id": "c",
                 "source_refs": list(SOURCES.values())}
    return {"source_docs": sources, "registry_cards": cards, "l0_bindings": bindings,
            "candidate": candidate, "registry_document": registry, "l0_document": l0,
            "observed_revisions": {"03": "rev-03", "08": "rev-08"}}


def run(d):
    return admit_t03(**d)


def test_real_document_ids_but_missing_701_and_l0_are_not_routable(d):
    d["registry_cards"] = None
    d["l0_bindings"] = None
    r = run(d)
    assert r["status"] == "HOLD_701_QOP_AOP_SIGNATURE"
    assert sorted(r["missing"]) == ["03_701_CARD", "08_701_CARD"]
    assert r["route_dispatched"] is False
    assert r["native_execution"] is False


def test_general_protocols_card_cannot_pass_as_source_specific_701(d):
    d["registry_cards"] = {"PROTOCOLS": {"function_signature": "general_protocols"}}
    assert run(d)["status"] == "HOLD_701_QOP_AOP_SIGNATURE"


def test_only_one_contract_card_blocks(d):
    d["registry_cards"].pop("08")
    assert run(d)["missing"] == ["08_701_CARD"]


@pytest.mark.parametrize("field,value", [
    ("q_op", ""), ("a_op", ""), ("search_route", ""), ("output_schema", ""),
    ("function_signature", ""), ("owner_id", ""), ("source_revision", "old-rev"),
    ("registry_revision", "old-reg"), ("primary_home", "OUTSIDE_FAMILY"),
])
def test_unsigned_or_misbound_701_fields_block(d, field, value):
    d["registry_cards"]["03"][field] = value
    assert run(d)["status"] == "HOLD_701_QOP_AOP_SIGNATURE"


def test_701_duplicate_function_signature_blocks(d):
    d["registry_cards"]["08"]["function_signature"] = (
        d["registry_cards"]["03"]["function_signature"]
    )
    assert "701_DUPLICATE_FUNCTION_SIGNATURE" in run(d)["missing"]


def test_source_revision_drift_blocks_before_registry(d):
    d["source_docs"]["03"]["revision"] = "old"
    assert run(d)["status"] == "HOLD_SOURCE_REVISION"


@pytest.mark.parametrize("corruption", ["missing_08", "wrong_03_id", "bad_home", "missing_revision"])
def test_source_identity_and_home_must_be_grounded(d, corruption):
    if corruption == "missing_08":
        d["source_docs"].pop("08")
    elif corruption == "wrong_03_id":
        d["source_docs"]["03"]["doc_id"] = "NEXUS-local-03"
    elif corruption == "bad_home":
        d["source_docs"]["08"]["family_home"] = "NEXUS"
    else:
        d["source_docs"]["03"]["revision"] = ""
    assert run(d)["status"] == "HOLD_SOURCE_BINDING"


@pytest.mark.parametrize("field,value", [
    ("interface", ""), ("return_expectation", ""), ("owner_id", "fake"),
    ("source_revision", "old"), ("registry_revision", "old"),
    ("l0_revision", "old"), ("home", "NEXUS"),
    ("current", False), ("authority", "EXECUTOR"),
])
def test_l0_owner_interface_and_currentness_gates(d, field, value):
    d["l0_bindings"]["08"][field] = value
    assert run(d)["status"] == "HOLD_L0_INTERFACE"


def test_no_l0_rev_blocks(d):
    d["l0_document"] = None
    assert run(d)["status"] == "HOLD_L0_INTERFACE"


@pytest.mark.parametrize("field,value", [
    ("execute", True), ("routed", True), ("receipt_observed", True)
])
def test_no_fake_execution_claim(d, field, value):
    d["candidate"][field] = value
    assert run(d)["status"] == "BLOCKED_FALSE_EXECUTION"


@pytest.mark.parametrize("mutation", ["no_03_source", "no_mission", "no_correlation", "bad_refs"])
def test_candidate_lineage_must_name_both_documents(d, mutation):
    if mutation == "no_03_source":
        d["candidate"]["source_refs"].remove(SOURCES["03"])
    elif mutation == "no_mission":
        d["candidate"]["mission_id"] = ""
    elif mutation == "no_correlation":
        d["candidate"]["correlation_id"] = ""
    else:
        d["candidate"]["source_refs"] = "string-not-list"
    assert run(d)["status"] == "HOLD_LINEAGE"


def test_invalid_upstream_blocks(d):
    d["candidate"]["status"] = "UNKNOWN"
    assert run(d)["status"] == "HOLD_UPSTREAM"


def test_missing_registry_revision_blocks(d):
    d["registry_document"]["revision"] = ""
    assert run(d)["status"] == "HOLD_701_QOP_AOP_SIGNATURE"


def test_positive_controlled_fixture_is_explicitly_non_native(d):
    r = run(d)
    assert r["status"] == "LAB_ROUTE_REQUEST_ONLY"
    assert r["route_owner"] == "705"
    assert {x["function"] for x in r["owner_bound_edges"]} == {
        "message_event_contract", "failure_retry_policy",
    }
    assert r["source_revisions"] == {"03": "rev-03", "08": "rev-08"}
    assert r["native_execution"] is False
    assert r["authorized_execution"] is False
    assert r["route_dispatched"] is False
    assert r["next_owner"] == "701_4200_L0_NATIVE_ATTESTATION_BEFORE_705"
    assert "NOT_AUTHENTICATED" in r["evidence_class"]


def test_baseline_cog02_would_trust_unverified_but_well_shaped_owner(d):
    fake = dict(d["candidate"], function_owners=[{
        "function": "invented-function", "owner_id": "made-up-owner",
        "interface": "invented-interface", "current": True,
        "authority": "REFERENCE_ONLY",
    }])
    assert cog02(fake)["status"] == "ROUTE_REQUEST_ONLY"
    d["registry_cards"] = None
    assert run(d)["status"] == "HOLD_701_QOP_AOP_SIGNATURE"


def test_readonly_inputs(d):
    previous = copy.deepcopy(d)
    run(d)
    assert d == previous


def test_untrusted_invalid_packet_fails_closed(d):
    d["source_docs"] = []
    assert run(d)["status"] == "HOLD_SOURCE_SCHEMA"


def test_registry_and_l0_consistency_cannot_replace_authenticated_readback(d):
    r = run(d)
    assert r["status"] == "LAB_ROUTE_REQUEST_ONLY"
    assert r["evidence_class"] == "CONTROLLED_FIXTURE_SCHEMA_CONSISTENCY_NOT_AUTHENTICATED"


# Methods CORVAN P01/P02/BLOCK03/P04: every material T03 admission
# needs a fresh 03+08 source revision snapshot before any 701/L0 admission.
def test_missing_observed_snapshot_blocks_even_if_owner_fixtures_look_valid(d):
    d.pop("observed_revisions")
    r = run(d)
    assert r["status"] == "HOLD_SOURCE_SNAPSHOT_REQUIRED"
    assert r["step"] == "SOURCE"
    assert r["route_dispatched"] is False
    assert r["authorized_execution"] is False


@pytest.mark.parametrize("snapshot", [
    None, {},
    {"03": "rev-03"},
    {"03": "rev-03", "08": ""},
    {"03": "rev-03", "08": " "},
    {"03": "rev-03", "08": True},
    {"03": "rev-03", "08": 17},
])
def test_partial_or_invalid_revision_observation_never_passes(d, snapshot):
    d["observed_revisions"] = snapshot
    assert run(d)["status"] == "HOLD_SOURCE_SNAPSHOT_REQUIRED"


@pytest.mark.parametrize("snapshot", ["rev-08", [], False, 12])
def test_wrong_observation_container_is_schema_hold(d, snapshot):
    d["observed_revisions"] = snapshot
    assert run(d)["status"] == "HOLD_SOURCE_SCHEMA"


def test_old_08_pin_cannot_be_reused_as_current_with_plausible_701_l0(d):
    d["source_docs"]["08"]["revision"] = "rev-08-previous"
    # Real source readback remains at rev-08; source gate runs before 701.
    r = run(d)
    assert r["status"] == "HOLD_SOURCE_REVISION"
    assert "08_REVISION_DRIFT" in r["missing"]
    assert r["step"] == "SOURCE"
    assert r["native_execution"] is False


def test_current_03_08_snapshot_still_needs_two_real_701_cards(d):
    d["registry_cards"] = {}
    r = run(d)
    assert r["status"] == "HOLD_701_QOP_AOP_SIGNATURE"
    assert sorted(r["missing"]) == ["03_701_CARD", "08_701_CARD"]


def test_source_revision_change_invalidates_only_affected_t03_edge(d):
    d["observed_revisions"]["08"] = "rev-08-next"
    r = run(d)
    assert r["status"] == "HOLD_SOURCE_REVISION"
    assert r["missing"] == ["08_REVISION_DRIFT"]
    assert r["source_revisions"]["03"] == "rev-03"
    assert r["route_dispatched"] is False
