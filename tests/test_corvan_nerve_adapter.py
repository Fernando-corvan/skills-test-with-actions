"""Corvan nerve adapter: bounded local execution and adversarial guardrails."""
from dataclasses import replace
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from corvan_mission_chain import Mission, Questions, route  # noqa: E402
from corvan_nerve_adapter import FunctionContract, NerveAdapter, NerveHold, Request  # noqa: E402


@pytest.fixture
def scenario():
    m = Mission("M-nerve", "r1", "fp:a", "trace:a", "src:1")
    q = Questions(m.mission_id, m.revision, "question:a", ("PANORAMA", "INSTINTO"))
    owners = {"PANORAMA": "PANORAMA_OWNER", "INSTINTO": "INSTINTO_OWNER",
              "DESTINO": "DESTINO_OWNER", "NEXUS": "NEXUS_LOCAL"}
    selection = route(m, q, owners)
    calls = []

    def panorama(p):
        calls.append("PANORAMA")
        return {"kind": "PANORAMA_PACKET", "delta": "relations:" + p["topic"]}

    def instinto(p):
        calls.append("INSTINTO")
        return {"kind": "WEAK_SIGNAL_PACKET", "delta": "signal:" + p["topic"]}

    contracts = (
        FunctionContract("PANORAMA", "PANORAMA_OWNER", "source:panorama:r1",
                         "TOPIC_PACKET", "PANORAMA_PACKET", "LOCAL_ADAPTER"),
        FunctionContract("INSTINTO", "INSTINTO_OWNER", "source:instinto:r1",
                         "TOPIC_PACKET", "WEAK_SIGNAL_PACKET", "LOCAL_ADAPTER"),
        FunctionContract("DESTINO", "DESTINO_OWNER", "source:destino:r1",
                         "TOPIC_PACKET", "DESTINO_PACKET", "DISCOVERY_ONLY"),
        FunctionContract("NEXUS", "NEXUS_LOCAL", "source:nexus:r1",
                         "TOPIC_PACKET", "NEXUS_PACKET", "HOST_METHOD"),
    )
    bus = NerveAdapter(contracts, {"PANORAMA": panorama, "INSTINTO": instinto})
    req = Request(m.mission_id, m.revision, m.trace_id, "PANORAMA",
                  "source:panorama:r1", "TOPIC_PACKET", {"topic": "x"}, "op:1")
    return m, owners, selection, bus, calls, req


def test_two_adapter_calls_have_real_local_returns(scenario):
    m, _, selection, bus, calls, req = scenario
    a = bus.dispatch(m, selection, req)
    b = bus.dispatch(m, selection, replace(
        req, function_id="INSTINTO", source_revision="source:instinto:r1",
        operation_id="op:2"))
    assert calls == ["PANORAMA", "INSTINTO"]
    assert a.owner_id == "PANORAMA_OWNER"
    assert a.provenance_class == "LOCAL_ADAPTER_RETURN_OBSERVED"
    assert b.observed_delta == "signal:x"
    assert len(bus.completed) == 2
    assert bus.native_callability() == "HOLD_NATIVE_OWNER_AUTHENTICATION_AND_INTERFACE"


@pytest.mark.parametrize("changes,message", [
    ({"source_revision": "stale"}, "stale_source_revision"),
    ({"input_type": "wrong"}, "input_contract_mismatch"),
    ({"operation_id": ""}, "missing_operation_id"),
    ({"function_id": "DESTINO", "source_revision": "source:destino:r1"},
     "not_selected_by_705"),
    ({"function_id": "UNKNOWN"}, "not_selected_by_705"),
    ({"mission_id": "forged"}, "mission_correlation_mismatch"),
    ({"trace_id": "forged"}, "mission_correlation_mismatch"),
])
def test_bad_handoff_is_blocked(scenario, changes, message):
    m, _, selection, bus, calls, req = scenario
    with pytest.raises(NerveHold, match=message):
        bus.dispatch(m, selection, replace(req, **changes))
    assert calls == []


def test_replayed_operation_blocked(scenario):
    m, _, selection, bus, calls, req = scenario
    bus.dispatch(m, selection, req)
    with pytest.raises(NerveHold, match="duplicate_operation_no_replay"):
        bus.dispatch(m, selection, req)
    assert calls == ["PANORAMA"]


def test_destino_and_nexus_do_not_get_false_native_status(scenario):
    m, owners, _, bus, calls, req = scenario
    q = Questions(m.mission_id, m.revision, "q:optionality", ("DESTINO", "NEXUS"))
    selected = route(m, q, owners)
    with pytest.raises(NerveHold, match="discovery_is_not_execution"):
        bus.dispatch(m, selected, replace(
            req, function_id="DESTINO", source_revision="source:destino:r1"))
    with pytest.raises(NerveHold, match="host_method_no_independent_owner_call"):
        bus.dispatch(m, selected, replace(
            req, function_id="NEXUS", source_revision="source:nexus:r1"))
    assert calls == []


def test_forged_owner_and_invalid_return_blocked(scenario):
    m, owners, selected, bus, _, req = scenario
    owners["PANORAMA"] = "FAKE_OWNER"
    forged_route = route(m, Questions(m.mission_id, m.revision, "q",
                                     ("PANORAMA",)), owners)
    with pytest.raises(NerveHold, match="owner_conflict"):
        bus.dispatch(m, forged_route, req)
    bad_bus = NerveAdapter(tuple(bus.contracts.values()),
                           {"PANORAMA": lambda _: {"kind": "WRONG", "delta": "x"}})
    with pytest.raises(NerveHold, match="invalid_owner_return_type"):
        bad_bus.dispatch(m, selected, req)
    assert not bad_bus.completed


def test_external_effect_is_blocked(scenario):
    m, _, selection, bus, calls, req = scenario
    changed = replace(bus.contracts["PANORAMA"], effect="WRITE")
    restricted = NerveAdapter((changed,), bus.implementations)
    with pytest.raises(NerveHold, match="external_effect_not_authorized_here"):
        restricted.dispatch(m, selection, req)
    assert calls == []


def test_missing_adapter_stale_route_and_duplicate_signature(scenario):
    m, _, selection, bus, _, req = scenario
    empty = NerveAdapter(tuple(bus.contracts.values()), {})
    with pytest.raises(NerveHold, match="missing_actual_adapter"):
        empty.dispatch(m, selection, req)
    with pytest.raises(NerveHold, match="stale_route"):
        bus.dispatch(replace(m, revision="r2"), selection,
                     replace(req, revision="r2"))
    c = bus.contracts["PANORAMA"]
    with pytest.raises(NerveHold, match="duplicate_function_id"):
        NerveAdapter((c, c), {})
