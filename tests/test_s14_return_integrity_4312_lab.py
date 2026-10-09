"""Behavioral tests for lab-only S14 -> 4312 receipt-interlock companion."""
import os
import sys
import copy

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from corvan_s14_return_integrity_guard import evaluate_return_integrity


@pytest.fixture
def scenario():
    p = dict(mission_id="m1", mission_revision="rev3", assurance_thread_id="t5",
             event_id="e4", correlation_id="c1", causation_id="e3",
             expected_return_owner="organ-A", return_owner="organ-A",
             return_contract_ref="contract-A", idempotency_key="key-4",
             wal_ref="wal-4", event_seq=4)
    e = {
        "contracts": dict(event_id="e4", mission_id="m1", mission_revision="rev3",
                          assurance_thread_id="t5", correlation_id="c1",
                          idempotency_key="key-4", accepted=True,
                          readback_verified=True, duplicate=False),
        "wal": dict(event_id="e4", mission_revision="rev3", wal_ref="wal-4",
                    event_seq=4, durable_high_watermark=4,
                    durable_commit=True, readback_verified=True),
        "return_owner": dict(event_id="e4", assurance_thread_id="t5",
                             return_owner="organ-A", return_contract_ref="contract-A",
                             ack_state="ACKED", return_state="RETURNED",
                             readback_verified=True),
    }
    return p, e


def call(scenario, *, seq=4):
    p, e = scenario
    return evaluate_return_integrity(p, e, expected_sequence=seq)


def test_valid_mock_receipts_only_prepare_native_owner_reconciliation(scenario):
    r = call(scenario)
    assert r["status"] == "READY_FOR_NATIVE_OWNER_RECONCILIATION"
    assert r["native_casa_executed"] is False
    assert "not authenticated" in r["claim"]
    assert r["assurance_thread_id"] == "t5"


@pytest.mark.parametrize("key", [
    "mission_id", "mission_revision", "assurance_thread_id", "event_id",
    "correlation_id", "causation_id", "expected_return_owner",
    "return_contract_ref", "wal_ref", "idempotency_key"
])
def test_missing_packet_identifier_is_blocking(scenario, key):
    p, e = scenario
    p.pop(key)
    assert call((p, e))["status"] == "HOLD_PACKET_SCHEMA"


@pytest.mark.parametrize("bad", [None, "", "  ", 9, True, []])
def test_bad_required_field_types_block(scenario, bad):
    p, e = scenario
    p["event_id"] = bad
    assert call((p, e))["status"] == "HOLD_PACKET_SCHEMA"


@pytest.mark.parametrize("bad", [0, -1, True, 4.0, "4", None])
def test_invalid_event_sequence_blocks(scenario, bad):
    p, e = scenario
    p["event_seq"] = bad
    assert call((p, e))["status"] == "HOLD_PACKET_SCHEMA"


@pytest.mark.parametrize("bad", [True, "4", 4.0, 0, -2, None])
def test_invalid_sequence_baseline_blocks(scenario, bad):
    p, e = scenario
    expected = "HOLD_SEQUENCE_BASELINE" if bad is None else "HOLD_EXPECTED_SEQUENCE_SCHEMA"
    assert call((p, e), seq=bad)["status"] == expected


def test_event_gap_blocks_rather_than_compacting(scenario):
    assert call(scenario, seq=5)["status"] == "HOLD_EVENT_GAP"


def test_wrong_return_owner_blocks(scenario):
    p, e = scenario
    p["return_owner"] = "other-organ"
    assert call((p, e))["status"] == "HOLD_OWNER_MISMATCH"


@pytest.mark.parametrize("field,bad", [
    ("mission_id", "other-mission"), ("mission_revision", "rev2"),
    ("assurance_thread_id", "other-thread"),
    ("correlation_id", "another-correlation"),
    ("idempotency_key", "new-key"), ("event_id", "different-event"),
])
def test_contract_owner_receipt_binding_required(scenario, field, bad):
    p, e = scenario
    e["contracts"][field] = bad
    assert call((p, e))["status"] == "HOLD_CONTRACTS_BINDING"


@pytest.mark.parametrize("field,bad", [
    ("accepted", False), ("readback_verified", False),
])
def test_unaccepted_unread_contracts_receipt_blocks(scenario, field, bad):
    p, e = scenario
    e["contracts"][field] = bad
    assert call((p, e))["status"] == "HOLD_CONTRACTS_NOT_ACCEPTED"


@pytest.mark.parametrize("bad", [None, "false", 1])
def test_duplicate_flag_needs_real_boolean(scenario, bad):
    p, e = scenario
    e["contracts"]["duplicate"] = bad
    assert call((p, e))["status"] == "HOLD_CONTRACTS_SCHEMA"


def test_duplicate_is_not_new_evidence(scenario):
    p, e = scenario
    e["contracts"]["duplicate"] = True
    assert call((p, e))["status"] == "HOLD_DUPLICATE_REVIEW"


@pytest.mark.parametrize("field,bad", [
    ("event_id", "e2"), ("event_seq", 3),
    ("mission_revision", "rev2"), ("wal_ref", "other-wal"),
])
def test_wal_event_binding_required(scenario, field, bad):
    p, e = scenario
    e["wal"][field] = bad
    assert call((p, e))["status"] == "HOLD_WAL_BINDING"


@pytest.mark.parametrize("bad", [None, "4", 3, True])
def test_non_durable_or_invalid_high_watermark_blocks(scenario, bad):
    p, e = scenario
    e["wal"]["durable_high_watermark"] = bad
    assert call((p, e))["status"] == "HOLD_WAL_WATERMARK"


@pytest.mark.parametrize("field,bad", [
    ("durable_commit", False), ("readback_verified", False)
])
def test_write_attempt_ne_committed_wal(scenario, field, bad):
    p, e = scenario
    e["wal"][field] = bad
    assert call((p, e))["status"] == "HOLD_WAL_NOT_DURABLE"


@pytest.mark.parametrize("field,bad", [
    ("event_id", "different"), ("assurance_thread_id", "old-thread"),
    ("return_owner", "wrong-organ"), ("return_contract_ref", "wrong-contract")
])
def test_return_receipt_must_match_original(scenario, field, bad):
    p, e = scenario
    e["return_owner"][field] = bad
    assert call((p, e))["status"] == "HOLD_RETURN_BINDING"


def test_request_sent_ne_ack(scenario):
    p, e = scenario
    e["return_owner"]["ack_state"] = "ACK_PENDING"
    assert call((p, e))["status"] == "HOLD_ACK_PENDING"


@pytest.mark.parametrize("field,bad", [
    ("return_state", "RETURN_PENDING"), ("readback_verified", False)
])
def test_return_without_readback_does_not_close(scenario, field, bad):
    p, e = scenario
    e["return_owner"][field] = bad
    assert call((p, e))["status"] == "HOLD_RETURN_NOT_READBACK"


@pytest.mark.parametrize("bad", [None, [], "not-a-dict"])
def test_malformed_evidence_not_accepted(scenario, bad):
    p, e = scenario
    assert evaluate_return_integrity(p, bad, expected_sequence=4)["status"] == "HOLD_OWNER_RECEIPTS"


@pytest.mark.parametrize("which", ["contracts", "wal", "return_owner"])
def test_missing_owner_receipt_not_accepted(scenario, which):
    p, e = scenario
    e[which] = None
    assert call((p, e))["status"] == "HOLD_OWNER_RECEIPTS"


def test_packet_not_an_object_is_blocked(scenario):
    _, e = scenario
    assert evaluate_return_integrity([], e, expected_sequence=4)["status"] == "HOLD_PACKET_SCHEMA"


def test_input_is_not_modified(scenario):
    p, e = scenario
    snapshot = copy.deepcopy((p, e))
    call((p, e))
    assert snapshot == (p, e)
