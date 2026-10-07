# Nexus SPARSE_STATE_PROBE — GitHub experiment

Pattern under test:

```text
probe when:
    task_error_delta
    repeated_intrusion
    unexpected_latency
    mission_switch
    explicit_user_request
    strong_state_change

not:
    continuously
```

## Operational question

Can the event-gated strategy preserve every predefined salient event while
performing fewer probes than a continuous strategy?

## Test design

A deterministic sequence contains 10 events. Four are salient:

- unexpected_latency
- mission_switch
- explicit_user_request
- strong_state_change

The control strategy probes after all 10 events.
The Nexus strategy probes only on the four salient events.

Success requires:

1. all four salient events are selected;
2. normal progress is ignored;
3. the sparse strategy uses fewer probes than the continuous control.

This experiment validates only the software-control behavior of the pattern.
It does not independently validate claims about human cognition or performance.
