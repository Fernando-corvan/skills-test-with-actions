"""T03-only documentary admission guard for COG02 v0.3.

Reconciles evidence READ FROM original Casa Google Docs. It is not an
independent 701 registry or L0 interface attestor. No 705 call is made.
Never upgrade file existence, caller-supplied booleans, or test fixtures
into verified native function signatures or callable interfaces.
"""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from corvan_cognitive_bridges_v03 import cog02

# Readback pins obtained from native Drive Docs on 2026-10-09.
# These are *versioned documentary observations*, not runtime attestation.
T03_DOCS = {
    "03": {
        "id": "1v3tRTw01GClNpqC-v25j_HyFED1_FWMqFMRpR-sP6N8",
        "rev": "AHj4eMTc3iWPurGhPbEeuPMswSen83DKRq_O565-AvOTK-tZSTnKqhc61hOSL8jlItCmA6eYygyCvbX5893BJMf726UHutKEf3gAHTrMamQ",
        "functions": ["ClassifyEvent", "ValidateMessageEvent", "RouteEvent", "BuildEventPacket"],
    },
    "08": {
        "id": "1RtFVefDvE5qbEiX8u3QMMmqiguXRxpq5236SWOcu3Ss",
        "rev": "ANLCKQkwLxOm1qdxrYv9nTRKGKsnG74NAOrYPXVD2u7peJE5zBLOW4HxwJLjfxtzJeB-PsH-jwJHXtUOYn14VbxQo-2BbY2Y1crbG-V8Dj8",
        "functions": ["Signature_ClassifyFailure", "Signature_SelectRetryRoute", "Signature_ComputeRecoveryDelay", "Signature_VerifyRecovery"],
    },
}
T03_HOUSE_FAMILY = "L_SHARED_CONTRACTS"
T03_PHYSICAL_PARENT = "1n-Fmnl7wvC_3nQge16xqZktk5gJGSdnH"
T03_701 = {
    "id": "1HZgBtCv4TY1l4R0bSnv-POEhI9LAKq5am8mfDKBLuy4",
    "rev": "AHj4eMQ11OQu5JPla_2OtrCnDrCRig1XOH3hOmzlrHq0XCUefhuguW-IJqYIiACYgadE_OrOZPQRGeeFzoMAGI4tfYh5AvPc65bPYXrKN60",
    "general_protocols_card": True,
    "exact_signed_qop_aop_cards_for_03_08": False,
}
T03_L0 = {
    "id": "1zGQ4t65VG68Y15z5-qHD8TFDhP7X3mVyVx6JnzPF7OU",
    "rev": "AHj4eMS1SOOil11q0IdLBVs3xTtNuAW70pC17xQzC4EguCfJzoiFbM014Fc5Vcr7F0F7KUx8jboiBBD2A5pwu6nOtFbOUV5xqPlVl9wLl4A",
    "owner_home_named": True,
    "exact_callable_interface_and_currentness_for_03_08": False,
}
COG02_REV = "AHj4eMSzNttVa6xWYkpsFVxcUKTzvNRkDx-4kushd6ekZlt2bxEd7I4VpKpBnAZsYD46gAn6_dWjt6zOaVvADVF7QNfBL63RZHR3Z0VYl-M"


def _hold(packet: Any, status: str, next_owner: str, reason: str) -> dict:
    p = packet if isinstance(packet, dict) else {}
    return {
        "status": status,
        "mission_id": p.get("mission_id") if isinstance(p.get("mission_id"), str) else None,
        "correlation_id": p.get("correlation_id") if isinstance(p.get("correlation_id"), str) else None,
        "authority_ceiling": "PROPOSAL_ONLY",
        "native_execution": False,
        "authorized_execution": False,
        "route_dispatched": False,
        "next_owner": next_owner,
        "reason": reason,
        "unresolved_edges": [
            "03->701_EXACT_Q_OP_A_OP", "08->701_EXACT_Q_OP_A_OP",
            "03->L0_NATIVE_INTERFACE", "08->L0_NATIVE_INTERFACE",
        ],
        "source_snapshot": {"03": T03_DOCS["03"]["rev"], "08": T03_DOCS["08"]["rev"],
                            "701": T03_701["rev"], "L0": T03_L0["rev"]},
        "missing_native_evidence": True,
    }


def inspect_t03(packet: Any) -> dict:
    """Evaluate current *observed* readback with no ability to forge a route."""
    if not isinstance(packet, dict):
        return _hold(packet, "HOLD_SCHEMA", "INPUT_VALIDATION", "packet not a dict")
    for k in ("mission_id", "correlation_id"):
        if not isinstance(packet.get(k), str) or not packet[k].strip():
            return _hold(packet, "HOLD_LINEAGE", "COG01", k + " missing")
    if packet.get("status") != "CANDIDATE_ONLY":
        return _hold(packet, "HOLD_UPSTREAM", "COG01", "candidate not admitted")
    pins = packet.get("source_pins")
    if not isinstance(pins, dict) or any(
            pins.get(key) != T03_DOCS[key]["rev"] for key in ("03", "08")):
        return _hold(packet, "HOLD_SOURCE_REVISION", "L0/OWNER",
                     "03/08 revision drift or missing source pin")
    refs = packet.get("source_refs")
    if not isinstance(refs, list) or any(
            not isinstance(x, str) or not x.strip() for x in refs):
        return _hold(packet, "HOLD_LINEAGE", "COG01", "invalid source_refs")
    if not all(T03_DOCS[x]["id"] in refs for x in ("03", "08")):
        return _hold(packet, "HOLD_LINEAGE", "COG01", "missing original source IDs")
    if (packet.get("execute") is True or packet.get("routed") is True
            or packet.get("receipt_observed") is True):
        return _hold(packet, "BLOCKED_FALSE_EXECUTION", "705/4411",
                     "candidate cannot claim execution/receipt")
    # The key difference from raw v0.3: caller-provided owner/current/interface
    # fields CANNOT replace 701's source-registered Q_OP/A_OP cards.
    if not T03_701["exact_signed_qop_aop_cards_for_03_08"]:
        return _hold(packet, "HOLD_701_QOP_AOP_SIGNATURE", "701",
                     "701 only has a generic Protocols card, not per-03/08 source cards")
    if not T03_L0["exact_callable_interface_and_currentness_for_03_08"]:
        return _hold(packet, "HOLD_L0_OWNER_INTERFACE", "4200_L0",
                     "native owner binding/real callable interface not verified")
    # If the hard-coded source snapshot is updated in the future, the owner
    # signatures and source attestation must be independently read again.
    return _hold(packet, "HOLD_NATIVE_ATTESTATION_REQUIRED", "701/L0/QA",
                 "documentary flags alone never authorize a 705 request")


def demonstrate_raw_cog02_risk(packet: dict) -> dict:
    """Diagnostic only: result of existing lab COG02 on untrusted owner claims."""
    return deepcopy(cog02(deepcopy(packet)))
