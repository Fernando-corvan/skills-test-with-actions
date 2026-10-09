"""Bounded fixture: task-aware hydration and external audience fitness.

This is a deterministic contract laboratory, not independent Nexus/Winston,
not a generative language model, and not a connected publishing runtime.
"""
from dataclasses import dataclass
from typing import Tuple


class ContextBlocked(ValueError):
    """Material contract violation that must stop the proposed transition."""


@dataclass(frozen=True)
class Mission:
    purpose: str
    consumption: str  # self | third_party | mixed
    operation: str  # discuss | prepare | publish | modify
    artifact_kind: str  # none | prose | academic | technical | math | code
    audience: str = ""
    destination: str = ""
    protected_facts: Tuple[str, ...] = ()
    authorized_effects: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Capability:
    signature: str
    owner: str
    current: bool = True


@dataclass(frozen=True)
class OutputPlan:
    mode: str
    route: Tuple[str, ...]
    owners: Tuple[str, ...]
    audience: str
    profile: str
    artifact_kind: str
    protected_facts: Tuple[str, ...]
    status: str
    action_permitted: bool
    evidence_ceiling: str = "DETERMINISTIC_FIXTURE_ONLY"


# Signatures are inherited from functional domains; names of applications
# and named organs never activate any capability by themselves.
CONTEXT = "EXTERNAL_CONTEXT_BINDING"
FACTS = "FACT_CONSTRAINT_PRESERVATION"
AUDIENCE = "AUDIENCE_FIT_REVIEW"
LANGUAGE = "LANGUAGE_CLARITY_REVIEW"
NUMERIC = "NUMERIC_CORRECTNESS_REVIEW"
TECHNICAL = "TECHNICAL_CORRECTNESS_REVIEW"
EFFECT = "EXTERNAL_EFFECT_PERMISSION_GATE"
READBACK = "EXTERNAL_EFFECT_READBACK_CONTRACT"


def _mode(mission):
    if mission.consumption not in {"self", "third_party", "mixed"}:
        raise ContextBlocked("invalid_consumption")
    if mission.operation not in {"discuss", "prepare", "publish", "modify"}:
        raise ContextBlocked("invalid_operation")
    if mission.artifact_kind not in {
        "none", "prose", "academic", "technical", "math", "code"
    }:
        raise ContextBlocked("invalid_artifact_kind")
    if mission.operation in {"publish", "modify"}:
        return "EXTERNAL_ACTION"
    if mission.consumption == "mixed":
        return "MIXED"
    if mission.consumption == "third_party":
        return "EXTERNAL_ARTIFACT"
    return "INTERNAL"


def _required(mission, mode):
    external = mode != "INTERNAL"
    signatures = []
    if external:
        signatures += [CONTEXT, FACTS, AUDIENCE]
    if mission.artifact_kind in {"prose", "academic"} and external:
        signatures.append(LANGUAGE)
    if mission.artifact_kind == "math":
        signatures.append(NUMERIC)
    if mission.artifact_kind in {"technical", "code"}:
        signatures.append(TECHNICAL)
    if mode == "EXTERNAL_ACTION":
        signatures += [EFFECT, READBACK]
    # Preserve order of dependencies from need, without duplicating steps.
    return tuple(dict.fromkeys(signatures))


def _profile(mission, mode):
    if mode == "INTERNAL":
        return "INTERNAL_CONVERSATION"
    return {
        "academic": "DISCIPLINE_APPROPRIATE_ACADEMIC",
        "technical": "REPRODUCIBLE_TECHNICAL",
        "code": "MAINTAINABLE_CODE_DOCUMENTATION",
        "math": "AUDITABLE_MATHEMATICAL",
        "prose": "NATURAL_AUDIENCE_APPROPRIATE",
        "none": "EXTERNAL_CONTEXT_ORIENTATION",
    }[mission.artifact_kind]


def plan(mission, capabilities):
    """Build the least sufficient function route and explicit effect state."""
    if not isinstance(mission, Mission):
        raise ContextBlocked("invalid_mission")
    if not mission.purpose.strip():
        raise ContextBlocked("missing_purpose")
    mode = _mode(mission)
    if mode != "INTERNAL" and not mission.audience.strip():
        raise ContextBlocked("missing_external_audience")
    if mode == "EXTERNAL_ACTION" and not mission.destination.strip():
        raise ContextBlocked("missing_external_destination")
    selected = []
    for signature in _required(mission, mode):
        candidates = [
            c for c in capabilities
            if c.signature == signature and c.current and c.owner.strip()
        ]
        if not candidates:
            raise ContextBlocked("missing_current_function:" + signature)
        if len(candidates) != 1:
            raise ContextBlocked("ambiguous_function_owner:" + signature)
        selected.append(candidates[0])
    permitted = mode != "EXTERNAL_ACTION" or (
        mission.operation in mission.authorized_effects
    )
    return OutputPlan(
        mode=mode,
        route=tuple(c.signature for c in selected),
        owners=tuple(c.owner for c in selected),
        audience=mission.audience,
        profile=_profile(mission, mode),
        artifact_kind=mission.artifact_kind,
        protected_facts=mission.protected_facts,
        status=("HOLD_ACTION_PERMISSION" if not permitted
                else "READY_FOR_ARTIFACT_REVIEW"),
        action_permitted=permitted,
    )


# Only surface verifiable, local editorial signals; this list is neither a
# deception filter nor proof that any text was produced by a human.
FORMULAIC_PHRASES = (
    "en atención a su solicitud",
    "quedo a su entera disposición",
    "espero que este correo le encuentre bien",
)


def review_artifact(output_plan, rendered_text):
    """Detect lost facts and formulaic wording; do not generate or publish."""
    if not isinstance(rendered_text, str) or not rendered_text.strip():
        raise ContextBlocked("empty_artifact")
    normalized = rendered_text.casefold()
    lost = tuple(
        fact for fact in output_plan.protected_facts
        if not fact.strip() or fact.casefold() not in normalized
    )
    formulaic = tuple(
        phrase for phrase in FORMULAIC_PHRASES if phrase in normalized
    )
    if lost:
        verdict = "REPAIR_REQUIRED"
    elif formulaic:
        verdict = "HUMAN_STYLE_REVIEW_RECOMMENDED"
    else:
        verdict = "STRUCTURAL_CHECKS_PASS"
    return {
        "verdict": verdict,
        "missing_protected_facts": lost,
        "formulaic_signals": formulaic,
        "audience": output_plan.audience,
        "profile": output_plan.profile,
        "not_proven": (
            "natural_language_quality", "factual_truth",
            "human_authorship", "external_action", "Casa_runtime"
        ),
    }
