"""Adversarial contract tests for contextual hydration and external artifacts."""
from dataclasses import replace
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from corvan_external_context import (  # noqa: E402
    AUDIENCE, CONTEXT, EFFECT, FACTS, LANGUAGE, NUMERIC, READBACK,
    TECHNICAL, Capability, ContextBlocked, Mission, plan, review_artifact,
)


def catalog():
    return [
        Capability(CONTEXT, "ContextHydration"),
        Capability(FACTS, "L3"),
        Capability(AUDIENCE, "AudienceOutput"),
        Capability(LANGUAGE, "LanguageReview"),
        Capability(NUMERIC, "MathQA"),
        Capability(TECHNICAL, "EngineeringQA"),
        Capability(EFFECT, "L4"),
        Capability(READBACK, "L6"),
        Capability("UNRELATED_CAPABILITY", "Unused"),
    ]


def signal(**kwargs):
    s = Mission(
        purpose="Respond to the specific task",
        consumption="third_party",
        operation="prepare",
        artifact_kind="prose",
        audience="Academic administrator",
        protected_facts=("reference 26/MI/165",),
    )
    return replace(s, **kwargs)


def test_internal_chat_is_not_an_external_artifact():
    p = plan(signal(purpose="Explain what Gmail is", consumption="self",
                    operation="discuss", artifact_kind="none", audience=""), catalog())
    assert p.mode == "INTERNAL"
    assert p.route == ()
    assert p.profile == "INTERNAL_CONVERSATION"
    assert p.action_permitted


def test_app_name_does_not_trigger_external_routing():
    a = plan(signal(purpose="Discuss WhatsApp", consumption="self",
                    operation="discuss", artifact_kind="none", audience=""), catalog())
    b = plan(signal(purpose="Discuss a notebook", consumption="self",
                    operation="discuss", artifact_kind="none", audience=""), catalog())
    assert a.route == b.route == ()
    assert a.mode == b.mode == "INTERNAL"


def test_external_prose_requires_context_not_just_brand_trigger():
    p = plan(signal(purpose="Create an institution-facing note"), catalog())
    assert p.mode == "EXTERNAL_ARTIFACT"
    assert p.route == (CONTEXT, FACTS, AUDIENCE, LANGUAGE)
    assert "UNRELATED_CAPABILITY" not in p.route
    assert p.profile == "NATURAL_AUDIENCE_APPROPRIATE"


def test_academic_artifact_selects_academic_profile():
    p = plan(signal(artifact_kind="academic",
                    audience="Social sciences faculty examiner"), catalog())
    assert p.profile == "DISCIPLINE_APPROPRIATE_ACADEMIC"
    assert p.route[-1] == LANGUAGE


def test_maths_for_self_uses_only_numeric_review():
    p = plan(signal(consumption="self", audience="",
                    artifact_kind="math", purpose="Compute an integral"), catalog())
    assert p.route == (NUMERIC,)
    assert LANGUAGE not in p.route


def test_external_mathematical_report_is_audience_bound_not_prose():
    p = plan(signal(artifact_kind="math", audience="Audit committee"), catalog())
    assert p.route == (CONTEXT, FACTS, AUDIENCE, NUMERIC)
    assert p.profile == "AUDITABLE_MATHEMATICAL"
    assert LANGUAGE not in p.route


@pytest.mark.parametrize("kind,profile", [
    ("technical", "REPRODUCIBLE_TECHNICAL"),
    ("code", "MAINTAINABLE_CODE_DOCUMENTATION"),
])
def test_technical_external_outputs_are_not_processed_like_emails(kind, profile):
    p = plan(signal(artifact_kind=kind, audience="Engineering maintainers"), catalog())
    assert p.route == (CONTEXT, FACTS, AUDIENCE, TECHNICAL)
    assert p.profile == profile


def test_mixed_task_keeps_external_reader_context():
    p = plan(signal(consumption="mixed", audience="Workshop participants"), catalog())
    assert p.mode == "MIXED"
    assert CONTEXT in p.route


def test_external_context_missing_audience_is_blocked():
    with pytest.raises(ContextBlocked, match="missing_external_audience"):
        plan(signal(audience="  "), catalog())


def test_missing_purpose_rejected():
    with pytest.raises(ContextBlocked, match="missing_purpose"):
        plan(signal(purpose=""), catalog())


@pytest.mark.parametrize("field,value,error", [
    ("consumption", "company", "invalid_consumption"),
    ("operation", "auto_send", "invalid_operation"),
    ("artifact_kind", "unknown", "invalid_artifact_kind"),
])
def test_invalid_input_contract_is_blocked(field, value, error):
    with pytest.raises(ContextBlocked, match=error):
        plan(replace(signal(), **{field: value}), catalog())


def test_invalid_mission_object_is_blocked():
    with pytest.raises(ContextBlocked, match="invalid_mission"):
        plan({"consumption": "third_party"}, catalog())


def test_publish_not_permitted_even_with_complete_context():
    p = plan(signal(operation="publish", destination="University portal"), catalog())
    assert p.mode == "EXTERNAL_ACTION"
    assert not p.action_permitted
    assert p.status == "HOLD_ACTION_PERMISSION"
    assert p.route[-2:] == (EFFECT, READBACK)


def test_authorization_is_exactly_scoped_and_not_execution_proof():
    p = plan(signal(operation="publish", destination="University portal",
                    authorized_effects=("modify",)), catalog())
    assert not p.action_permitted
    q = plan(signal(operation="publish", destination="University portal",
                    authorized_effects=("publish",)), catalog())
    assert q.action_permitted
    assert q.status == "READY_FOR_ARTIFACT_REVIEW"
    assert q.evidence_ceiling == "DETERMINISTIC_FIXTURE_ONLY"


def test_modify_action_has_own_effect_authorization():
    p = plan(signal(operation="modify", destination="Repository",
                    artifact_kind="code", authorized_effects=("modify",)), catalog())
    assert p.mode == "EXTERNAL_ACTION"
    assert p.action_permitted
    assert TECHNICAL in p.route
    assert LANGUAGE not in p.route


def test_external_action_requires_destination():
    with pytest.raises(ContextBlocked, match="missing_external_destination"):
        plan(signal(operation="publish", destination=""), catalog())


def test_stale_or_missing_owner_cannot_be_hydrated():
    stale = [replace(c, current=False) if c.signature == CONTEXT else c
             for c in catalog()]
    with pytest.raises(ContextBlocked, match="missing_current_function"):
        plan(signal(), stale)
    ownerless = [replace(c, owner="") if c.signature == CONTEXT else c
                 for c in catalog()]
    with pytest.raises(ContextBlocked, match="missing_current_function"):
        plan(signal(), ownerless)


def test_duplicate_current_function_must_not_guess_owner():
    conflicting = catalog() + [Capability(CONTEXT, "ConflictingOwner")]
    with pytest.raises(ContextBlocked, match="ambiguous_function_owner"):
        plan(signal(), conflicting)


def test_external_cognitive_route_changes_when_audience_and_task_change():
    p = plan(signal(audience="Professor", artifact_kind="academic"), catalog())
    q = plan(signal(audience="Engineering team", artifact_kind="code"), catalog())
    assert p.route != q.route
    assert p.audience != q.audience
    assert p.profile != q.profile
    assert p.protected_facts == q.protected_facts


def test_no_artifact_requested_still_binds_external_context():
    p = plan(signal(artifact_kind="none", audience="Municipal officer"), catalog())
    assert p.route == (CONTEXT, FACTS, AUDIENCE)
    assert p.profile == "EXTERNAL_CONTEXT_ORIENTATION"


def test_missing_protected_fact_is_material_defect():
    p = plan(signal(), catalog())
    review = review_artifact(p, "Estimado equipo, solicito una confirmación.")
    assert review["verdict"] == "REPAIR_REQUIRED"
    assert review["missing_protected_facts"] == ("reference 26/MI/165",)


def test_formulaic_phrase_is_a_review_signal_not_human_origin_verdict():
    p = plan(signal(), catalog())
    review = review_artifact(
        p, "En atención a su solicitud, confirmo la reference 26/MI/165."
    )
    assert review["verdict"] == "HUMAN_STYLE_REVIEW_RECOMMENDED"
    assert review["formulaic_signals"]
    assert "human_authorship" in review["not_proven"]


def test_clean_sample_meets_structural_checks_only():
    p = plan(signal(), catalog())
    review = review_artifact(
        p, "Sandra: este es el número que aparece en la reference 26/MI/165."
    )
    assert review["verdict"] == "STRUCTURAL_CHECKS_PASS"
    assert "natural_language_quality" in review["not_proven"]
    assert "external_action" in review["not_proven"]


def test_no_empty_text_and_no_empty_invariant_bypass():
    p = plan(signal(), catalog())
    with pytest.raises(ContextBlocked, match="empty_artifact"):
        review_artifact(p, " ")
    hacked = replace(p, protected_facts=(" ",))
    assert review_artifact(hacked, "Hello")["verdict"] == "REPAIR_REQUIRED"


@pytest.mark.parametrize("phrase", [
    "quedo a su entera disposición",
    "espero que este correo le encuentre bien",
])
def test_other_generic_phrases_are_only_review_flags(phrase):
    p = plan(signal(protected_facts=()), catalog())
    assert review_artifact(p, phrase)["verdict"] == "HUMAN_STYLE_REVIEW_RECOMMENDED"
