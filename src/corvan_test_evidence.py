"""Bounded CORVAN test-evidence classifier fixture.

This module classifies what a test demonstrates. It does not certify Casa runtime,
canonical ontology, or CORVAN as a whole.
"""
from dataclasses import dataclass
from typing import Iterable


class TestEvidenceBlocked(ValueError):
    pass


TEST_CLASSES = {"CF", "M", "IF", "CTRL", "SYS", "ADAPT"}
RESULTS = {"PASS", "PARTIAL", "FAIL", "BLOCKED"}
EVIDENCE_LEVELS = {
    "DECLARED",
    "IMPLEMENTED",
    "EXECUTED",
    "OBSERVED",
    "REPRODUCED",
    "CROSS_COMPONENT",
    "RUNTIME_BOUND",
}


def _nonempty(value, name):
    if not isinstance(value, str) or not value.strip():
        raise TestEvidenceBlocked("missing:" + name)
    return value


def _items(values, name, minimum=0):
    if values is None:
        values = ()
    if not isinstance(values, (list, tuple)):
        raise TestEvidenceBlocked("invalid:" + name)
    if len(values) < minimum:
        raise TestEvidenceBlocked("missing:" + name)
    for value in values:
        _nonempty(value, name)
    return tuple(values)


@dataclass(frozen=True)
class EvidenceReceipt:
    test_id: str
    test_class: str
    target_function: str | None
    mechanism_under_test: str | None
    owner: str
    dependencies: tuple
    preconditions: tuple
    expected_observable: str
    fail_condition: str
    forbidden_inference: tuple
    result: str
    evidence_level: str
    evidence_refs: tuple
    currentness: str
    scope_claim: str
    does_not_prove: tuple
    interface_endpoints: tuple = ()
    perturbation: str | None = None
    preserved_invariant: str | None = None
    system_components: tuple = ()
    control_target: str | None = None


def classify(payload):
    """Validate a test receipt and return a bounded evidence classification."""
    required = (
        "test_id", "test_class", "target_function", "mechanism_under_test",
        "owner", "dependencies", "preconditions", "expected_observable",
        "fail_condition", "forbidden_inference", "result", "evidence_level",
        "evidence_refs", "currentness", "scope_claim", "does_not_prove",
    )
    for key in required:
        if key not in payload:
            raise TestEvidenceBlocked("missing_field:" + key)

    test_class = _nonempty(payload["test_class"], "test_class")
    if test_class not in TEST_CLASSES:
        raise TestEvidenceBlocked("invalid:test_class")

    result = _nonempty(payload["result"], "result")
    if result not in RESULTS:
        raise TestEvidenceBlocked("invalid:result")

    evidence_level = _nonempty(payload["evidence_level"], "evidence_level")
    if evidence_level not in EVIDENCE_LEVELS:
        raise TestEvidenceBlocked("invalid:evidence_level")

    receipt = EvidenceReceipt(
        test_id=_nonempty(payload["test_id"], "test_id"),
        test_class=test_class,
        target_function=payload.get("target_function"),
        mechanism_under_test=payload.get("mechanism_under_test"),
        owner=_nonempty(payload["owner"], "owner"),
        dependencies=_items(payload.get("dependencies"), "dependencies"),
        preconditions=_items(payload.get("preconditions"), "preconditions"),
        expected_observable=_nonempty(payload["expected_observable"], "expected_observable"),
        fail_condition=_nonempty(payload["fail_condition"], "fail_condition"),
        forbidden_inference=_items(payload.get("forbidden_inference"), "forbidden_inference", 1),
        result=result,
        evidence_level=evidence_level,
        evidence_refs=_items(payload.get("evidence_refs"), "evidence_refs"),
        currentness=_nonempty(payload["currentness"], "currentness"),
        scope_claim=_nonempty(payload["scope_claim"], "scope_claim"),
        does_not_prove=_items(payload.get("does_not_prove"), "does_not_prove", 1),
        interface_endpoints=_items(payload.get("interface_endpoints", ()), "interface_endpoints"),
        perturbation=payload.get("perturbation"),
        preserved_invariant=payload.get("preserved_invariant"),
        system_components=_items(payload.get("system_components", ()), "system_components"),
        control_target=payload.get("control_target"),
    )
    _validate_class_contract(receipt)
    _validate_scope(receipt)
    return {
        "test_id": receipt.test_id,
        "classification": f"{receipt.test_class}/{receipt.evidence_level}/{receipt.result}",
        "scope_claim": receipt.scope_claim,
        "does_not_prove": receipt.does_not_prove,
    }


def _validate_class_contract(r):
    if r.test_class == "CF":
        _nonempty(r.target_function, "target_function")
        if not r.mechanism_under_test and not r.dependencies:
            raise TestEvidenceBlocked("cf_requires_supporting_mechanism_or_dependency")

    elif r.test_class == "M":
        _nonempty(r.target_function, "target_function")
        _nonempty(r.mechanism_under_test, "mechanism_under_test")

    elif r.test_class == "IF":
        if len(r.interface_endpoints) < 2:
            raise TestEvidenceBlocked("if_requires_two_endpoints")
        if r.evidence_level not in {"CROSS_COMPONENT", "RUNTIME_BOUND"}:
            raise TestEvidenceBlocked("if_requires_cross_component_evidence")

    elif r.test_class == "CTRL":
        _nonempty(r.control_target, "control_target")

    elif r.test_class == "SYS":
        if len(r.system_components) < 2:
            raise TestEvidenceBlocked("sys_requires_two_components")
        if r.evidence_level not in {"CROSS_COMPONENT", "RUNTIME_BOUND"}:
            raise TestEvidenceBlocked("sys_requires_cross_component_evidence")

    elif r.test_class == "ADAPT":
        _nonempty(r.perturbation, "perturbation")
        _nonempty(r.preserved_invariant, "preserved_invariant")


def _validate_scope(r):
    """Block common scope inflation patterns."""
    claim = r.scope_claim.lower()
    forbidden = " ".join(r.forbidden_inference).lower()

    if r.test_class == "M" and "complete cognitive function" in claim:
        raise TestEvidenceBlocked("scope_inflation:m_to_cf")
    if r.test_class in {"M", "CF", "IF", "CTRL"} and "corvan as a whole" in claim:
        raise TestEvidenceBlocked("scope_inflation:local_to_system")
    if r.evidence_level != "RUNTIME_BOUND" and "casa runtime proven" in claim:
        raise TestEvidenceBlocked("scope_inflation:fixture_to_runtime")
    if r.test_class == "M" and not any(
        token in forbidden for token in ("function", "cognitive", "system", "corvan")
    ):
        raise TestEvidenceBlocked("mechanism_receipt_must_forbid_parent_inference")


def classification_label(payload):
    """Return only the bounded label after full validation."""
    return classify(payload)["classification"]
