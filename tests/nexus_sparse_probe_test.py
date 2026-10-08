# System Modules
import os
import sys

# Project Modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from nexus_sparse_probe import (  # noqa: E402
    SALIENT_EVENTS,
    continuous_probe_plan,
    sparse_probe_plan,
)


def test_sparse_probe_catches_all_salient_events_with_fewer_probes():
    events = [
        "normal_progress",
        "normal_progress",
        "unexpected_latency",
        "normal_progress",
        "mission_switch",
        "normal_progress",
        "explicit_user_request",
        "normal_progress",
        "strong_state_change",
        "normal_progress",
    ]

    sparse = sparse_probe_plan(events)
    continuous = continuous_probe_plan(events)

    detected = {event for _, event in sparse}

    assert detected == {
        "unexpected_latency",
        "mission_switch",
        "explicit_user_request",
        "strong_state_change",
    }
    assert detected.issubset(SALIENT_EVENTS)
    assert len(sparse) == 4
    assert len(continuous) == 10
    assert len(sparse) < len(continuous)


def test_sparse_probe_ignores_non_salient_progress():
    events = ["normal_progress", "normal_progress", "normal_progress"]

    assert sparse_probe_plan(events) == []
