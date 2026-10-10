"""T03 Contracts 03/08 -> 701/L0 -> COG02, *laboratory-only* admission.

This guard never calls 701, L0, 705 or original Casa organs. It checks
caller-supplied records against pinned documentary identities and refuses
to treat plausible text, source titles or fixture booleans as authenticated
owner attestations. A positive fixture is never a real routing clearance.
"""
from __future__ import annotations

from corvan_cognitive_bridges_v03 import cog02

SOURCES = {
    "03": "1v3tRTw01GClNpqC-v25j_HyFED1_FWMqFMRpR-sP6N8",
    "08": "1RtFVefDvE5qbEiX8u3QMMmqiguXRxpq5236SWOcu3Ss",
}
REGISTRY_ID = "1HZgBtCv4TY1l4R0bSnv-POEhI9LAKq5am8mfDKBLuy4"
L0_ID = "1zGQ4t65VG68Y15z5-qHD8TFDhP7X3mVyVx6JnzPF7OU"
FAMILY = "L_SHARED_CONTRACTS"


def _txt(v):
    return isinstance(v, str) and bool(v.strip())


def _hold(status, step, missing, sources=None, *, mission_id=None, correlation_id=None):
    return {
        "status": status, "step": step, "missing": sorted(set(missing)),
        "source_refs": [SOURCES[k] for k in SOURCES],
        "source_revisions": {
            k: sources.get(k, {}).get("revision")
            for k in SOURCES
        } if isinstance(sources, dict) else {},
        "mission_id": mission_id if _txt(mission_id) else None,
        "correlation_id": correlation_id if _txt(correlation_id) else None,
        "next_owner": "701" if step == "701" else ("4200_L0" if step == "L0" else "SOURCE_REVIEW"),
        "authority_ceiling": "PROPOSAL_ONLY", "native_execution": False,
        "authorized_execution": False, "route_dispatched": False,
        "evidence_class": "LAB_CHECK_OF_SUPPLIED_RECORDS_NOT_AUTHENTICATED",
    }


def admit_t03(
    source_docs, registry_cards, l0_bindings, candidate,
    *, registry_document=None, l0_document=None, observed_revisions=None
):
    """Check the 03+08 pair and return either a precise HOLD or a lab proposal.

    All inputs (including positive attestations) are unauthenticated here.
    In production, native owners must independently sign/read back 701/L0
    records before a route request can leave staging. This lab cannot do so.
    """
    mission = candidate.get("mission_id") if isinstance(candidate, dict) else None
    correlation = candidate.get("correlation_id") if isinstance(candidate, dict) else None

    if not isinstance(source_docs, dict):
        return _hold("HOLD_SOURCE_SCHEMA", "SOURCE", ["03", "08"])
    missing = []
    for key, expected in SOURCES.items():
        item = source_docs.get(key)
        if not isinstance(item, dict) or item.get("doc_id") != expected:
            missing.append(key + "_DOC_ID")
        elif not _txt(item.get("revision")):
            missing.append(key + "_REVISION")
        elif item.get("family_home") != FAMILY:
            missing.append(key + "_HOME")
    if missing:
        return _hold("HOLD_SOURCE_BINDING", "SOURCE", missing, source_docs,
                     mission_id=mission, correlation_id=correlation)
    if observed_revisions is not None:
        if not isinstance(observed_revisions, dict):
            return _hold("HOLD_SOURCE_SCHEMA", "SOURCE", ["CURRENT_REVISION_SNAPSHOT"], source_docs,
                         mission_id=mission, correlation_id=correlation)
        wrong = [k + "_REVISION_DRIFT" for k in SOURCES
                 if source_docs[k]["revision"] != observed_revisions.get(k)]
        if wrong:
            return _hold("HOLD_SOURCE_REVISION", "SOURCE", wrong, source_docs,
                         mission_id=mission, correlation_id=correlation)

    if not isinstance(candidate, dict) or candidate.get("status") != "CANDIDATE_ONLY":
        return _hold("HOLD_UPSTREAM", "SOURCE", ["COG01_CANDIDATE"],
                     source_docs, mission_id=mission, correlation_id=correlation)
    refs = candidate.get("source_refs")
    if (not _txt(mission) or not _txt(correlation) or
            not isinstance(refs, list) or
            not all(_txt(r) for r in refs) or
            not set(SOURCES.values()).issubset(set(refs))):
        return _hold("HOLD_LINEAGE", "SOURCE", ["MISSION_AND_EXACT_SOURCE_REFS"],
                     source_docs, mission_id=mission, correlation_id=correlation)
    if any(candidate.get(k) is True for k in ("execute", "routed", "receipt_observed")):
        return _hold("BLOCKED_FALSE_EXECUTION", "SOURCE", ["NO_EXECUTION_CLAIM"],
                     source_docs, mission_id=mission, correlation_id=correlation)

    # 701's general PROTOCOLS function card is not a card for either 03 or 08.
    if not isinstance(registry_document, dict) or (
            registry_document.get("doc_id") != REGISTRY_ID or
            not _txt(registry_document.get("revision"))):
        return _hold("HOLD_701_QOP_AOP_SIGNATURE", "701", ["701_REGISTRY_REVISION"],
                     source_docs, mission_id=mission, correlation_id=correlation)
    if not isinstance(registry_cards, dict):
        registry_cards = {}
    unresolved = []
    signatures = {}
    required_card_fields = ("doc_id", "source_revision", "registry_revision",
                            "function_signature", "q_op", "a_op", "owner_id",
                            "primary_home", "search_route", "output_schema")
    for key in SOURCES:
        card = registry_cards.get(key)
        if not isinstance(card, dict):
            unresolved.append(key + "_701_CARD")
            continue
        if (card.get("doc_id") != SOURCES[key] or
                card.get("source_revision") != source_docs[key]["revision"] or
                card.get("registry_revision") != registry_document["revision"] or
                any(not _txt(card.get(f)) for f in required_card_fields)):
            unresolved.append(key + "_701_QOP_AOP_CURRENT_SIGNATURE")
        elif card.get("primary_home") != FAMILY:
            unresolved.append(key + "_701_HOME")
        else:
            signatures[key] = card
    if len({c["function_signature"] for c in signatures.values()}) != len(signatures):
        unresolved.append("701_DUPLICATE_FUNCTION_SIGNATURE")
    if unresolved:
        return _hold("HOLD_701_QOP_AOP_SIGNATURE", "701", unresolved,
                     source_docs, mission_id=mission, correlation_id=correlation)

    if not isinstance(l0_document, dict) or (
            l0_document.get("doc_id") != L0_ID or
            not _txt(l0_document.get("revision"))):
        return _hold("HOLD_L0_INTERFACE", "L0", ["L0_CURRENT_REVISION"],
                     source_docs, mission_id=mission, correlation_id=correlation)
    if not isinstance(l0_bindings, dict):
        l0_bindings = {}
    missing = []
    owners = []
    for key, card in signatures.items():
        bind = l0_bindings.get(key)
        if not isinstance(bind, dict):
            missing.append(key + "_L0_RESOLUTION")
            continue
        expected = {
            "doc_id": SOURCES[key],
            "source_revision": source_docs[key]["revision"],
            "registry_revision": registry_document["revision"],
            "l0_revision": l0_document["revision"],
            "function_signature": card["function_signature"],
            "owner_id": card["owner_id"],
            "home": card["primary_home"],
        }
        if any(bind.get(field) != value for field, value in expected.items()):
            missing.append(key + "_L0_OWNER_CURRENTNESS_BIND")
        elif not _txt(bind.get("interface")) or not _txt(bind.get("return_expectation")):
            missing.append(key + "_L0_CALLABLE_INTERFACE")
        elif bind.get("current") is not True:
            missing.append(key + "_L0_NOT_CURRENT")
        elif bind.get("authority") != "REFERENCE_ONLY":
            missing.append(key + "_L0_AUTHORITY")
        else:
            owners.append({"function": card["function_signature"],
                           "owner_id": card["owner_id"],
                           "interface": bind["interface"],
                           "current": True, "authority": "REFERENCE_ONLY"})
    if missing:
        return _hold("HOLD_L0_INTERFACE", "L0", missing, source_docs,
                     mission_id=mission, correlation_id=correlation)
    request = dict(candidate, function_owners=owners)
    result = cog02(request)
    if result.get("status") != "ROUTE_REQUEST_ONLY":
        return _hold(result.get("status", "HOLD_COG02"), "COG02",
                     ["COG02_VALIDATION"], source_docs,
                     mission_id=mission, correlation_id=correlation)
    result.update(
        status="LAB_ROUTE_REQUEST_ONLY",
        evidence_class="CONTROLLED_FIXTURE_SCHEMA_CONSISTENCY_NOT_AUTHENTICATED",
        source_revisions={key: source_docs[key]["revision"] for key in SOURCES},
        registry_revision=registry_document["revision"],
        l0_revision=l0_document["revision"],
        unresolved_edges=[],
        route_dispatched=False, authorized_execution=False, native_execution=False,
        next_owner="701_4200_L0_NATIVE_ATTESTATION_BEFORE_705",
    )
    return result
