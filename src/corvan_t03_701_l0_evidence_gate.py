"""T03 source-bound companion gate for COG02 (NON-NATIVE LAB).

This module does NOT update 701/L0, invent their signature cards, dispatch
705, or activate/contracts. It only checks independently supplied evidence.
Only the actual owner of 701 may admit a Q_OP/A_OP card; only L0 can bind a
current interface. 'verified' fields on injected fixtures are NOT proof of
authentic provider identity.
"""
from __future__ import annotations

from corvan_cognitive_bridges_v03 import cog02

CONTRACTS_HOME_ID = "1n-Fmnl7wvC_3nQge16xqZktk5gJGSdnH"
REGISTRY_701_ID = "1HZgBtCv4TY1l4R0bSnv-POEhI9LAKq5am8mfDKBLuy4"
L0_ID = "1zGQ4t65VG68Y15z5-qHD8TFDhP7X3mVyVx6JnzPF7OU"
T03_FUNCTIONS = {
    "03_MESSAGE_EVENT": "1v3tRTw01GClNpqC-v25j_HyFED1_FWMqFMRpR-sP6N8",
    "08_FAILURE_RETRY": "1RtFVefDvE5qbEiX8u3QMMmqiguXRxpq5236SWOcu3Ss",
}


def _text(v):
    return isinstance(v, str) and bool(v.strip())


def _stop(status, detail):
    return {"status": status, "detail": detail,
            "stage": "COG02_T03_PRE_ROUTE",
            "route_sent": False, "authorized_execution": False,
            "native_execution": False, "provenance_scope": "LAB_ONLY"}


def _unique_by(items, attr):
    return len(items) == len({x.get(attr) for x in items})


def evaluate_t03(source_locks, registry701, resolution_l0, *, mission_id, correlation_id):
    """Return a route-request *proposal* only for fully bound supplied records.

    Missing/stale live 701 or L0 data MUST produce HOLD. No verification of
    provenance against providers occurs inside this pure Python function.
    """
    if not _text(mission_id) or not _text(correlation_id):
        return _stop("HOLD_MISSION", "mission/correlation identity missing")
    if not isinstance(source_locks, dict) or set(source_locks) != set(T03_FUNCTIONS):
        return _stop("HOLD_SOURCE_LOCK", "source lock set is incomplete")
    for function, docid in T03_FUNCTIONS.items():
        src = source_locks[function]
        if not isinstance(src, dict):
            return _stop("HOLD_SOURCE_LOCK", function + ": source invalid")
        if src.get("doc_id") != docid or src.get("parent_id") != CONTRACTS_HOME_ID:
            return _stop("HOLD_SOURCE_LOCK", function + ": source home/id mismatch")
        if not _text(src.get("revision")):
            return _stop("HOLD_SOURCE_LOCK", function + ": no pinned revision")
    if not isinstance(registry701, dict) or registry701.get("document_id") != REGISTRY_701_ID:
        return _stop("HOLD_701_QOP_AOP_SIGNATURE", "701 registry source missing")
    if not _text(registry701.get("revision")):
        return _stop("HOLD_701_QOP_AOP_SIGNATURE", "701 revision missing")
    cards = registry701.get("cards")
    if not isinstance(cards, list) or len(cards) != len(T03_FUNCTIONS):
        return _stop("HOLD_701_QOP_AOP_SIGNATURE", "both official cards required")
    if not all(isinstance(c, dict) for c in cards):
        return _stop("HOLD_701_QOP_AOP_SIGNATURE", "malformed signature card")
    if not _unique_by(cards, "function_id"):
        return _stop("HOLD_701_OWNER_COLLISION", "duplicate functional registry cards")
    registry_cards = {}
    for card in cards:
        function = card.get("function_id")
        if function not in T03_FUNCTIONS:
            return _stop("HOLD_701_QOP_AOP_SIGNATURE", "wrong function identifier")
        src = source_locks[function]
        must = ["q_op", "a_op", "output_schema", "registry_entry_ref",
                "owner_id", "primary_home_id", "interface_contract"]
        if any(not _text(card.get(k)) for k in must):
            return _stop("HOLD_701_QOP_AOP_SIGNATURE", function + ": Q_OP/A_OP or proof missing")
        if card.get("admission") != "VERIFIED_BY_701" or card.get("authority") != "REFERENCE_ONLY":
            return _stop("HOLD_701_QOP_AOP_SIGNATURE", function + ": no admitted signature")
        if (card.get("source_document_id") != src["doc_id"]
                or card.get("source_revision") != src["revision"]
                or card.get("primary_home_id") != CONTRACTS_HOME_ID):
            return _stop("HOLD_701_STALE", function + ": revision/home mismatch")
        registry_cards[function] = card
    if not isinstance(resolution_l0, dict) or resolution_l0.get("document_id") != L0_ID:
        return _stop("HOLD_L0_INTERFACE", "L0 source missing")
    if not _text(resolution_l0.get("revision")):
        return _stop("HOLD_L0_INTERFACE", "L0 revision missing")
    bindings = resolution_l0.get("bindings")
    if not isinstance(bindings, list) or len(bindings) != len(T03_FUNCTIONS):
        return _stop("HOLD_L0_INTERFACE", "both independently bound interfaces required")
    if not all(isinstance(b, dict) for b in bindings):
        return _stop("HOLD_L0_INTERFACE", "malformed interface record")
    if not _unique_by(bindings, "function_id"):
        return _stop("HOLD_L0_COLLISION", "duplicate L0 function mapping")
    owners = []
    for binding in bindings:
        function = binding.get("function_id")
        if function not in registry_cards:
            return _stop("HOLD_L0_INTERFACE", "unregistered function mapping")
        card, src = registry_cards[function], source_locks[function]
        if (binding.get("source_document_id") != src["doc_id"]
                or binding.get("source_revision") != src["revision"]
                or binding.get("parent_id") != CONTRACTS_HOME_ID
                or binding.get("owner_id") != card["owner_id"]
                or binding.get("interface_id") != card["interface_contract"]
                or binding.get("registry_entry_ref") != card["registry_entry_ref"]):
            return _stop("HOLD_L0_BINDING_MISMATCH", function + ": mismatch")
        if not _text(binding.get("interface_readback_ref")):
            return _stop("HOLD_L0_INTERFACE", function + ": interface not read back")
        if binding.get("current") is not True or binding.get("status") != "VERIFIED_BY_L0":
            return _stop("HOLD_L0_STALE", function + ": not current")
        owners.append({"function": function, "owner_id": card["owner_id"],
                       "interface": binding["interface_id"], "current": True,
                       "authority": "REFERENCE_ONLY"})
    p = {"status": "CANDIDATE_ONLY", "mission_id": mission_id,
         "correlation_id": correlation_id,
         "source_refs": [f"{src['doc_id']}@{src['revision']}" for src in source_locks.values()],
         "function_owners": owners, "execute": False, "routed": False,
         "receipt_observed": False, "analogies": []}
    result = cog02(p)
    if result.get("status") != "ROUTE_REQUEST_ONLY":
        return _stop("HOLD_COG02", str(result.get("status")))
    result.update(status="LAB_ROUTE_REQUEST_ONLY",
                  route_sent=False, authorized_execution=False, native_execution=False,
                  evidence_status="SUPPLIED_FIXTURE_NOT_AUTHENTICATED",
                  verification_next=["VERIFY_701_CARDS_AGAINST_LIVE_DOC",
                                     "VERIFY_L0_INTERFACE_AGAINST_LIVE_DOC",
                                     "THEN_HUMAN_REVIEW_BEFORE_705"])
    return result
