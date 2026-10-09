"""CORVAN COG01-03 deterministic proposal packet adapters, v0.3.
Laboratory fixtures only; not native Crown, Nexus, 705, or 4411.
Based on COG01/02/03 v0.2, adds fail-closed shape and range controls.
"""
from __future__ import annotations
from math import isfinite
from functools import wraps


def _base(p):
    return {"mission_id": p.get("mission_id"), "correlation_id": p.get("correlation_id"),
            "source_refs": list(p.get("source_refs") or []),
            "authority_ceiling": "PROPOSAL_ONLY", "native_execution": False}


def _fail(p, status, why, next_owner):
    return dict(_base(p), status=status, reason=why, next_owner=next_owner,
                authorized_execution=False)


def cog01(p):
    """Research finding -> bounded candidate. Neither proof nor probe execution."""
    if not p.get("mission_id") or not p.get("correlation_id"):
        return _fail(p, "HOLD_IDENTITY", "mission/correlation missing", "L0")
    if not p.get("mother_question"):
        return _fail(p, "HOLD_QUESTION", "question not defined", "L2/CF2")
    if not p.get("source_refs"):
        return _fail(p, "HOLD_SOURCE", "source missing", "RESEARCH")
    if p.get("source_state") != "CURRENT":
        return _fail(p, "HOLD_CURRENTNESS", "source not current", "RESEARCH/L6")
    if p.get("claim_class") not in {"OBSERVED", "SOURCED", "HYPOTHESIS", "UNKNOWN"}:
        return _fail(p, "HOLD_CLASSIFICATION", "claim unsupported", "L3/CF3")
    if not p.get("observations"):
        return _fail(p, "HOLD_OBSERVATION", "no observable basis", "RESEARCH")
    if not p.get("trigger") or not p.get("transformation") or not p.get("expected_delta"):
        return _fail(p, "HOLD_FUNCTIONAL_DNA", "functional DNA incomplete", "METHODS")
    views = p.get("views") or []
    if len(views) < 2 and p.get("ambiguity", False):
        return _fail(p, "HOLD_REPRESENTATION", "alternate view required", "CF2")
    alternatives = p.get("alternatives") or []
    if p.get("contradiction") and len(alternatives) < 2:
        return _fail(p, "HOLD_RIVAL", "two live rivals required", "CF3")
    viable = [x for x in (p.get("probes") or []) if x.get("legal")
              and x.get("discriminates") and x.get("cost", 999) <= p.get("probe_budget", 0)]
    viable.sort(key=lambda x: (-x.get("estimated_gain", 0) / (1 + x.get("cost", 0)),
                               x.get("name", "")))
    probe = viable[0]["name"] if viable else None
    if p.get("contradiction") and not probe:
        return _fail(p, "HOLD_DISCRIMINATOR", "no admissible probe", "RESEARCH/4002_D")
    return dict(_base(p), status="CANDIDATE_ONLY",
                functional_dna={k: p[k] for k in ("trigger", "transformation", "expected_delta")},
                claim_class=p["claim_class"],
                hypothesis_only=p["claim_class"] in {"HYPOTHESIS", "UNKNOWN"},
                views=views, alternatives=alternatives,
                counterevidence=p.get("counterevidence") or [],
                probe_request=probe, next_owner="701/713/L0",
                authorized_execution=False)


def cog02(p):
    """Candidate -> owner-bound route request. Real route remains 705's decision."""
    if p.get("status") != "CANDIDATE_ONLY":
        return _fail(p, "HOLD_UPSTREAM", "candidate not admitted", "COG01")
    if not p.get("source_refs") or not p.get("mission_id") or not p.get("correlation_id"):
        return _fail(p, "HOLD_LINEAGE", "incomplete source lineage", "COG01")
    owners = p.get("function_owners") or []
    if not owners:
        return _fail(p, "HOLD_OWNER", "no function owners", "701/L0")
    if len(set(o.get("function") for o in owners)) != len(owners):
        return _fail(p, "HOLD_COLLISION", "duplicate functional claims", "701/L0")
    if any(not o.get("owner_id") or not o.get("interface") for o in owners):
        return _fail(p, "HOLD_INTERFACE", "missing owner or interface", "L0")
    if any(o.get("current") is not True for o in owners):
        return _fail(p, "HOLD_OWNER_STALE", "owner not current", "L0")
    if any(o.get("authority") != "REFERENCE_ONLY" for o in owners):
        return _fail(p, "BLOCKED_AUTHORITY", "authority transfer claim", "L3")
    if p.get("execute", False) or p.get("routed", False) or p.get("receipt_observed", False):
        return _fail(p, "BLOCKED_FALSE_EXECUTION", "request not executed", "705/4411")
    if any(m.get("surface_similarity") and not m.get("relation_map")
           for m in (p.get("analogies") or [])):
        return _fail(p, "HOLD_FALSE_ANALOGY", "superficial analogy", "CF2/CF3")
    edges = [{"function": o["function"], "owner_id": o["owner_id"],
              "interface": o["interface"]} for o in owners]
    return dict(_base(p), status="ROUTE_REQUEST_ONLY", owner_bound_edges=edges,
                route_owner="705", handoff_owners=["3729", "4411"],
                retained_alternatives=p.get("alternatives") or [],
                trace_kind="PROPOSED_NOT_EXECUTED", authorized_execution=False)


def cog03(p):
    """Observed/QA-bounded result -> request, never actual output or learning."""
    if not p.get("mission_id") or not p.get("correlation_id"):
        return _fail(p, "HOLD_IDENTITY", "no correlation", "L0")
    if not p.get("source_refs") or p.get("source_state") != "CURRENT":
        return _fail(p, "HOLD_SOURCE", "current sources required", "RESEARCH/L6")
    if not p.get("return_receipt_ref") or p.get("return_kind") != "OBSERVED":
        return _fail(p, "HOLD_NO_RECEIPT", "not observed", "4411/L6")
    if not p.get("qa_ref") or p.get("qa_status") != "PASS":
        return _fail(p, "HOLD_QA", "independent QA required", "QA/L5")
    if p.get("claim_rank", 9) > p.get("evidence_rank", -1):
        return _fail(p, "BLOCKED_TRUTH_INFLATION", "unsupported certainty", "L3/CF3")
    if p.get("executed_by") == "COG03" or p.get("canon", False):
        return _fail(p, "BLOCKED_AUTHORITY", "cannot execute/canonize", "L4/L7")
    episodes = p.get("episodes") or []
    eligible = {x.get("case_id") for x in episodes if x.get("observed") and x.get("qa_pass")}
    return dict(_base(p), status="OUTPUT_REQUEST_ONLY",
                result_ref=p["return_receipt_ref"], qa_ref=p["qa_ref"],
                output_owner="05_OUT", output_chain=["05_OUT", "3739_OUT", "03_OUT"],
                semantic_ceiling=p["evidence_rank"], uncertainty=p.get("uncertainty") or [],
                learning_note="CF8_REVIEW_CANDIDATE" if len(eligible) >= 2
                else "NO_PROCEDURAL_LEARNING", authorized_execution=False)


def _text(v):
    return isinstance(v, str) and bool(v.strip())


def _texts(v):
    return isinstance(v, list) and all(_text(x) for x in v)


def _number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and isfinite(v) and v >= 0


def _schema_error(p, stage):
    if not isinstance(p, dict):
        return "packet must be object"
    for key in ("mission_id", "correlation_id"):
        if key in p and p[key] not in ("", None) and not _text(p[key]):
            return key + " invalid"
    if "source_refs" in p and not _texts(p["source_refs"]):
        return "source_refs invalid"
    if stage == 1:
        for key in ("mother_question", "trigger", "transformation", "expected_delta"):
            if key in p and p[key] not in ("", None) and not _text(p[key]):
                return key + " invalid"
        for key in ("observations", "views", "alternatives"):
            if key in p and not _texts(p[key]):
                return key + " invalid"
        if "probe_budget" in p and not _number(p["probe_budget"]):
            return "probe_budget invalid"
        if "probes" in p:
            if not isinstance(p["probes"], list):
                return "probes invalid"
            for probe in p["probes"]:
                if not isinstance(probe, dict) or not _text(probe.get("name")):
                    return "probe entry invalid"
                if type(probe.get("legal")) is not bool or type(probe.get("discriminates")) is not bool:
                    return "probe flags invalid"
                if not _number(probe.get("cost")) or not _number(probe.get("estimated_gain", 0)):
                    return "probe cost/gain invalid"
    elif stage == 2:
        if "function_owners" in p:
            if not isinstance(p["function_owners"], list):
                return "owners invalid"
            for owner in p["function_owners"]:
                if not isinstance(owner, dict):
                    return "owner entry invalid"
                if not _text(owner.get("function")):
                    return "owner function invalid"
                for key in ("owner_id", "interface"):
                    if owner.get(key) not in ("", None) and not _text(owner.get(key)):
                        return key + " invalid"
        if "analogies" in p:
            if not isinstance(p["analogies"], list) or any(not isinstance(x, dict) for x in p["analogies"]):
                return "analogies invalid"
        if "alternatives" in p and not _texts(p["alternatives"]):
            return "alternatives invalid"
    elif stage == 3:
        for key in ("claim_rank", "evidence_rank"):
            if key in p and not _number(p[key]):
                return key + " invalid"
        for key in ("return_receipt_ref", "qa_ref"):
            if key in p and p[key] not in ("", None) and not _text(p[key]):
                return key + " invalid"
        if "episodes" in p:
            if not isinstance(p["episodes"], list):
                return "episodes invalid"
            for ep in p["episodes"]:
                if not isinstance(ep, dict) or not _text(ep.get("case_id")):
                    return "episode invalid"
                if type(ep.get("observed")) is not bool or type(ep.get("qa_pass")) is not bool:
                    return "episode flags invalid"
    return None


def _guard(stage):
    def attach(fn):
        @wraps(fn)
        def safe(p):
            invalid = _schema_error(p, stage)
            if invalid:
                q = p if isinstance(p, dict) else {}
                return {"status": "HOLD_SCHEMA", "reason": invalid,
                        "mission_id": q.get("mission_id") if _text(q.get("mission_id")) else None,
                        "correlation_id": q.get("correlation_id") if _text(q.get("correlation_id")) else None,
                        "source_refs": q.get("source_refs") if _texts(q.get("source_refs")) else [],
                        "authority_ceiling": "PROPOSAL_ONLY", "native_execution": False,
                        "authorized_execution": False, "next_owner": "INPUT_VALIDATION"}
            try:
                return fn(p)
            except (TypeError, ValueError, KeyError, ZeroDivisionError, AttributeError):
                return {"status": "HOLD_SCHEMA", "reason": "invalid bounded packet",
                        "authority_ceiling": "PROPOSAL_ONLY", "native_execution": False,
                        "authorized_execution": False, "next_owner": "INPUT_VALIDATION"}
        return safe
    return attach


cog01 = _guard(1)(cog01)
cog02 = _guard(2)(cog02)
cog03 = _guard(3)(cog03)
