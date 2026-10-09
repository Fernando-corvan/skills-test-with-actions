"""CORVAN S14 -> 4312 return-integrity companion guard (LAB ONLY).

This is a surrogate protocol test against *supplied* owner receipts. It does
NOT call Casa, inspect a native WAL, activate 4312, or assert real execution.
Contracts owns event correctness; WAL owns durable commit; the original
function owner owns return; 4312 may only gate/transport their attestations.
"""

REQUIRED_TEXT = (
    "mission_id", "mission_revision", "assurance_thread_id", "event_id",
    "correlation_id", "causation_id", "expected_return_owner",
    "return_owner", "return_contract_ref", "idempotency_key", "wal_ref",
)
CONTRACT_MATCH = (
    ("event_id", "event_id"), ("mission_id", "mission_id"),
    ("mission_revision", "mission_revision"),
    ("assurance_thread_id", "assurance_thread_id"),
    ("correlation_id", "correlation_id"),
    ("idempotency_key", "idempotency_key"),
)
RETURN_MATCH = (
    ("event_id", "event_id"), ("assurance_thread_id", "assurance_thread_id"),
    ("return_owner", "return_owner"),
    ("return_contract_ref", "return_contract_ref"),
)
WAL_MATCH = (
    ("event_id", "event_id"),
    ("mission_revision", "mission_revision"),
    ("wal_ref", "wal_ref"),
    ("event_seq", "event_seq"),
)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _hold(status):
    return {"status": status, "native_casa_executed": False,
            "claim": "laboratory protocol guard only"}


def evaluate_return_integrity(packet, evidence, expected_sequence=None):
    """Fail-closed reconciliation of opaque owner receipts.

    All observed fields come from the caller. This prototype DOES NOT verify
    that evidence actually belongs to an authenticated owner or Drive/WAL.
    """
    if not isinstance(packet, dict):
        return _hold("HOLD_PACKET_SCHEMA")
    if not all(_text(packet.get(k)) for k in REQUIRED_TEXT):
        return _hold("HOLD_PACKET_SCHEMA")
    seq = packet.get("event_seq")
    if type(seq) is not int or seq < 1:
        return _hold("HOLD_PACKET_SCHEMA")
    if expected_sequence is None:
        return _hold("HOLD_SEQUENCE_BASELINE")
    if type(expected_sequence) is not int:
        return _hold("HOLD_EXPECTED_SEQUENCE_SCHEMA")
    if isinstance(expected_sequence, int) and expected_sequence < 1:
        return _hold("HOLD_EXPECTED_SEQUENCE_SCHEMA")
    if packet["return_owner"] != packet["expected_return_owner"]:
        return _hold("HOLD_OWNER_MISMATCH")
    if expected_sequence is not None and seq != expected_sequence:
        return _hold("HOLD_EVENT_GAP")
    if not isinstance(evidence, dict):
        return _hold("HOLD_OWNER_RECEIPTS")
    c, w, r = (evidence.get("contracts"), evidence.get("wal"),
               evidence.get("return_owner"))
    if not all(isinstance(x, dict) for x in (c, w, r)):
        return _hold("HOLD_OWNER_RECEIPTS")
    if any(c.get(ck) != packet[pk] for ck, pk in CONTRACT_MATCH):
        return _hold("HOLD_CONTRACTS_BINDING")
    if c.get("accepted") is not True or c.get("readback_verified") is not True:
        return _hold("HOLD_CONTRACTS_NOT_ACCEPTED")
    if c.get("duplicate") is True:
        return _hold("HOLD_DUPLICATE_REVIEW")
    if type(c.get("duplicate")) is not bool:
        return _hold("HOLD_CONTRACTS_SCHEMA")
    if any(w.get(wk) != packet[pk] for wk, pk in WAL_MATCH):
        return _hold("HOLD_WAL_BINDING")
    watermark = w.get("durable_high_watermark")
    if type(watermark) is not int or watermark < seq:
        return _hold("HOLD_WAL_WATERMARK")
    if w.get("durable_commit") is not True or w.get("readback_verified") is not True:
        return _hold("HOLD_WAL_NOT_DURABLE")
    if any(r.get(rk) != packet[pk] for rk, pk in RETURN_MATCH):
        return _hold("HOLD_RETURN_BINDING")
    if r.get("ack_state") != "ACKED":
        return _hold("HOLD_ACK_PENDING")
    if r.get("return_state") != "RETURNED" or r.get("readback_verified") is not True:
        return _hold("HOLD_RETURN_NOT_READBACK")
    return {
        "status": "READY_FOR_NATIVE_OWNER_RECONCILIATION",
        "native_casa_executed": False,
        "claim": "consistent supplied receipts only; not authenticated",
        "assurance_thread_id": packet["assurance_thread_id"],
        "event_id": packet["event_id"],
        "event_seq": seq,
    }
