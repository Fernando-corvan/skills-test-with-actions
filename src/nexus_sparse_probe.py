"""Executable probe for Nexus SPARSE_STATE_PROBE.

This module tests only the software-control property:
probe on salient events instead of probing continuously.
It does not claim to validate the human-performance research behind the pattern.
"""

SALIENT_EVENTS = frozenset({
    "task_error_delta",
    "repeated_intrusion",
    "unexpected_latency",
    "mission_switch",
    "explicit_user_request",
    "strong_state_change",
})


def should_probe(event):
    """Return True only for events that justify a state probe."""
    return event in SALIENT_EVENTS


def sparse_probe_plan(events):
    """Return the indices and names of events where a probe should occur."""
    return [
        (index, event)
        for index, event in enumerate(events)
        if should_probe(event)
    ]


def continuous_probe_plan(events):
    """Control strategy: probe after every event."""
    return list(enumerate(events))
