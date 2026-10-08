"""Tests for the CORVAN test-evidence classifier organ fixture."""
import os
import sys
from copy import deepcopy
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from corvan_test_evidence import TestEvidenceBlocked, classify  # noqa: E402


def base():
    return {
        "test_id": "TE-001",
        "test_class": "M",
        "target_function": "METACOGNITIVE_CONTROL",
        "mechanism_under_test": "SPARSE_STATE_PROBE",
        "owner": "NEXUS",
        "dependencies": [],
        "preconditions": ["event trigger exists"],
        "expected_observable": "state inspection occurs only at the declared event",
        "fail_condition": "continuous polling or missing event-gate",
        "forbidden_inference": [
            "mechanism pass does not prove the complete cognitive function",
            "mechanism pass does not prove CORVAN as a whole",
        ],
        "result": "PASS",
        "evidence_level": "OBSERVED",
        "evidence_refs": ["pytest:test_mechanism"],
        "currentness": "2026-10-08",
        "scope_claim": "bounded mechanism behavior observed in GitHub fixture",
        "does_not_prove": ["Casa runtime", "complete cognitive function"],
        "interface_endpoints": [],
        "perturbation": None,
        "preserved_invariant": None,
        "system_components": [],
        "control_target": None,
    }


def test_mechanism_is_bounded_and_cannot_self_promote():
    receipt = base()
    out = classify(receipt)
    assert out["classification"] == "M/OBSERVED/PASS"

    inflated = deepcopy(receipt)
    inflated["scope_claim"] = "complete cognitive function proven"
    with pytest.raises(TestEvidenceBlocked, match="scope_inflation:m_to_cf"):
        classify(inflated)


def test_cognitive_function_requires_function_and_support():
    receipt = base()
    receipt.update(
        test_id="TE-CF",
        test_class="CF",
        mechanism_under_test=None,
        dependencies=["M-01", "M-02"],
        evidence_level="OBSERVED",
        scope_claim="bounded cognitive function behavior observed",
        forbidden_inference=["function pass does not prove system behavior"],
    )
    assert classify(receipt)["classification"] == "CF/OBSERVED/PASS"

    receipt["dependencies"] = []
    with pytest.raises(TestEvidenceBlocked, match="cf_requires_supporting"):
        classify(receipt)


def test_interface_requires_two_endpoints_and_cross_component_evidence():
    receipt = base()
    receipt.update(
        test_id="TE-IF",
        test_class="IF",
        mechanism_under_test=None,
        target_function=None,
        interface_endpoints=["sender:3768", "receiver:705"],
        evidence_level="CROSS_COMPONENT",
        scope_claim="typed handoff accepted by both local endpoints",
        forbidden_inference=["interface pass does not prove Casa runtime"],
    )
    assert classify(receipt)["classification"] == "IF/CROSS_COMPONENT/PASS"

    broken = deepcopy(receipt)
    broken["interface_endpoints"] = ["sender:3768"]
    with pytest.raises(TestEvidenceBlocked, match="if_requires_two_endpoints"):
        classify(broken)


def test_control_requires_explicit_control_target():
    receipt = base()
    receipt.update(
        test_id="TE-CTRL",
        test_class="CTRL",
        mechanism_under_test=None,
        target_function=None,
        control_target="fail_closed_output_gate",
        scope_claim="gate blocks invalid release",
        forbidden_inference=["control pass does not prove system mission success"],
    )
    assert classify(receipt)["classification"] == "CTRL/OBSERVED/PASS"

    receipt["control_target"] = None
    with pytest.raises(TestEvidenceBlocked, match="missing:control_target"):
        classify(receipt)


def test_system_requires_multiple_components_and_cross_component_evidence():
    receipt = base()
    receipt.update(
        test_id="TE-SYS",
        test_class="SYS",
        mechanism_under_test=None,
        target_function=None,
        system_components=["3768", "705", "4208", "QA"],
        evidence_level="CROSS_COMPONENT",
        scope_claim="bounded multi-component chain behavior observed",
        forbidden_inference=["system fixture pass does not prove CORVAN as a whole"],
    )
    assert classify(receipt)["classification"] == "SYS/CROSS_COMPONENT/PASS"

    receipt["evidence_level"] = "OBSERVED"
    with pytest.raises(TestEvidenceBlocked, match="sys_requires_cross_component"):
        classify(receipt)


def test_adaptation_requires_perturbation_and_preserved_invariant():
    receipt = base()
    receipt.update(
        test_id="TE-ADAPT",
        test_class="ADAPT",
        mechanism_under_test=None,
        target_function=None,
        perturbation="route invalidated",
        preserved_invariant="mission identity",
        scope_claim="route changed after perturbation while mission identity was preserved",
        forbidden_inference=["adaptive fixture pass does not prove general autonomous adaptation"],
    )
    assert classify(receipt)["classification"] == "ADAPT/OBSERVED/PASS"

    receipt["preserved_invariant"] = None
    with pytest.raises(TestEvidenceBlocked, match="missing:preserved_invariant"):
        classify(receipt)


@pytest.mark.parametrize("field", [
    "test_id", "test_class", "owner", "expected_observable",
    "fail_condition", "currentness", "scope_claim",
])
def test_missing_material_field_blocks(field):
    receipt = base()
    receipt.pop(field)
    with pytest.raises(TestEvidenceBlocked, match="missing_field:" + field):
        classify(receipt)
