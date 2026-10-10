"""T03 negative and ablation tests; no original CORVAN organ calls."""
from copy import deepcopy
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import corvan_t03_source_admission as t03


def packet():
    return {
        "status": "CANDIDATE_ONLY", "mission_id": "T03-lab",
        "correlation_id": "T03-corr",
        "source_refs": [t03.T03_DOCS["03"]["id"], t03.T03_DOCS["08"]["id"]],
        "source_pins": {k: t03.T03_DOCS[k]["rev"] for k in ("03", "08")},
    }


def raw_fake_packet():
    p = packet()
    p["function_owners"] = [
        {"function": "event_validation", "owner_id": "fake-03",
         "interface": "fake://03", "current": True,
         "authority": "REFERENCE_ONLY"},
        {"function": "retry_governor", "owner_id": "fake-08",
         "interface": "fake://08", "current": True,
         "authority": "REFERENCE_ONLY"},
    ]
    return p


def assert_no_dispatch(result):
    assert result["native_execution"] is False
    assert result["authorized_execution"] is False
    assert result["route_dispatched"] is False
    assert result["authority_ceiling"] == "PROPOSAL_ONLY"


def test_real_documentary_snapshot_holds_missing_701_signatures():
    assert not t03.T03_701["exact_signed_qop_aop_cards_for_03_08"]
    assert not t03.T03_L0["exact_callable_interface_and_currentness_for_03_08"]
    result = t03.inspect_t03(packet())
    assert result["status"] == "HOLD_701_QOP_AOP_SIGNATURE"
    assert result["next_owner"] == "701"
    assert len(result["unresolved_edges"]) == 4
    assert_no_dispatch(result)


def test_historical_parent_is_not_an_executable_interface():
    assert t03.T03_HOUSE_FAMILY == "L_SHARED_CONTRACTS"
    assert t03.T03_PHYSICAL_PARENT == "1n-Fmnl7wvC_3nQge16xqZktk5gJGSdnH"
    assert t03.inspect_t03(packet())["status"] != "ROUTE_REQUEST_ONLY"


@pytest.mark.parametrize("mutate,expected", [
    ({"mission_id": ""}, "HOLD_LINEAGE"),
    ({"correlation_id": " "}, "HOLD_LINEAGE"),
    ({"status": "ARCHAEOLOGY_ONLY"}, "HOLD_UPSTREAM"),
    ({"source_refs": []}, "HOLD_LINEAGE"),
    ({"source_refs": "one string"}, "HOLD_LINEAGE"),
    ({"source_refs": [t03.T03_DOCS["03"]["id"]]}, "HOLD_LINEAGE"),
    ({"source_pins": {}}, "HOLD_SOURCE_REVISION"),
    ({"source_pins": {"03": "old", "08": t03.T03_DOCS["08"]["rev"]}},
     "HOLD_SOURCE_REVISION"),
    ({"execute": True}, "BLOCKED_FALSE_EXECUTION"),
    ({"routed": True}, "BLOCKED_FALSE_EXECUTION"),
    ({"receipt_observed": True}, "BLOCKED_FALSE_EXECUTION"),
])
def test_adversarial_source_packets_hold(mutate, expected):
    result = t03.inspect_t03(dict(packet(), **mutate))
    assert result["status"] == expected
    assert_no_dispatch(result)


@pytest.mark.parametrize("broken", [None, [], "bad", 7, True])
def test_wrong_type_holds(broken):
    result = t03.inspect_t03(broken)
    assert result["status"] == "HOLD_SCHEMA"
    assert_no_dispatch(result)


def test_raw_cog02_accepts_fake_typed_claim_but_strict_gate_blocks():
    p = raw_fake_packet()
    old = t03.demonstrate_raw_cog02_risk(p)
    assert old["status"] == "ROUTE_REQUEST_ONLY"
    assert old["native_execution"] is False
    new = t03.inspect_t03(p)
    assert new["status"] == "HOLD_701_QOP_AOP_SIGNATURE"
    assert_no_dispatch(new)


@pytest.mark.parametrize("modified", [
    {"function_owners": raw_fake_packet()["function_owners"]},
    {"owner_signature_verified": True, "l0_interface_verified": True},
    {"signature_authority": "701", "current": True, "callable": True},
    {"native_receipt": "fabricated", "authority_ceiling": "EXECUTOR"},
    {"705_route_requested": True, "route_owner": "705"},
])
def test_caller_self_assertions_cannot_unlock(modified):
    p = dict(packet(), **modified)
    assert t03.inspect_t03(p)["status"] == "HOLD_701_QOP_AOP_SIGNATURE"


def test_even_synthetic_document_flags_require_independent_native_proof(monkeypatch):
    monkeypatch.setitem(t03.T03_701, "exact_signed_qop_aop_cards_for_03_08", True)
    monkeypatch.setitem(t03.T03_L0,
                        "exact_callable_interface_and_currentness_for_03_08", True)
    result = t03.inspect_t03(raw_fake_packet())
    assert result["status"] == "HOLD_NATIVE_ATTESTATION_REQUIRED"
    assert_no_dispatch(result)


def test_when_701_only_becomes_available_l0_still_blocks(monkeypatch):
    monkeypatch.setitem(t03.T03_701, "exact_signed_qop_aop_cards_for_03_08", True)
    result = t03.inspect_t03(packet())
    assert result["status"] == "HOLD_L0_OWNER_INTERFACE"
    assert_no_dispatch(result)


def test_input_not_mutated():
    p = raw_fake_packet()
    before = deepcopy(p)
    t03.inspect_t03(p)
    t03.demonstrate_raw_cog02_risk(p)
    assert p == before


def test_snapshot_pins_both_current_source_revisions():
    p = packet()
    assert p["source_pins"]["03"] == t03.T03_DOCS["03"]["rev"]
    assert p["source_pins"]["08"] == t03.T03_DOCS["08"]["rev"]
    r = t03.inspect_t03(p)
    assert r["source_snapshot"]["701"] == t03.T03_701["rev"]
    assert r["source_snapshot"]["L0"] == t03.T03_L0["rev"]
