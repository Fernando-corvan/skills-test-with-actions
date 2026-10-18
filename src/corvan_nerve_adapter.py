"""Bounded nerve/handoff adapter for an existing Corvan mission Route.

This is laboratory transport plumbing, NOT a Casa organ, router, authorizer,
background service, or independently authenticated remote-owner interface.
"""
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple


class NerveHold(ValueError):
    """Fail closed for an invalid or unsupported owner handoff."""


@dataclass(frozen=True)
class FunctionContract:
    function_id: str
    owner_id: str
    source_revision: str
    input_type: str
    output_type: str
    mode: str  # LOCAL_ADAPTER, HOST_METHOD, or DISCOVERY_ONLY
    effect: str = "READ_ONLY"


@dataclass(frozen=True)
class Request:
    mission_id: str
    revision: str
    trace_id: str
    function_id: str
    source_revision: str
    input_type: str
    payload: dict
    operation_id: str


@dataclass(frozen=True)
class Receipt:
    mission_id: str
    revision: str
    trace_id: str
    function_id: str
    owner_id: str
    operation_id: str
    result_kind: str
    observed_delta: Optional[str]
    provenance_class: str
    # LOCAL_ADAPTER_RETURN_OBSERVED is never an independent native RPC.


class NerveAdapter:
    """Consume 705's preselected route; do not decide which owners to route."""

    def __init__(self, contracts: Tuple[FunctionContract, ...],
                 implementations: Dict[str, Callable[[dict], dict]]):
        self.contracts = {c.function_id: c for c in contracts}
        if len(self.contracts) != len(contracts):
            raise NerveHold("duplicate_function_id")
        self.implementations = implementations
        self.completed = set()

    def dispatch(self, mission, selected_route, request: Request) -> Receipt:
        if (mission.mission_id, mission.revision, mission.trace_id) != (
                request.mission_id, request.revision, request.trace_id):
            raise NerveHold("mission_correlation_mismatch")
        if (selected_route.mission_id, selected_route.revision,
                selected_route.trace_id) != (mission.mission_id,
                                            mission.revision, mission.trace_id):
            raise NerveHold("stale_route")
        selected = dict(selected_route.selected)
        if request.function_id not in selected:
            raise NerveHold("not_selected_by_705")
        c = self.contracts.get(request.function_id)
        if c is None:
            raise NerveHold("missing_701_signature")
        if c.owner_id != selected[request.function_id]:
            raise NerveHold("owner_conflict")
        if not c.source_revision or c.source_revision != request.source_revision:
            raise NerveHold("stale_source_revision")
        if c.input_type != request.input_type or not isinstance(request.payload, dict):
            raise NerveHold("input_contract_mismatch")
        if not request.operation_id:
            raise NerveHold("missing_operation_id")
        event_key = (request.mission_id, request.revision, request.operation_id)
        if event_key in self.completed:
            raise NerveHold("duplicate_operation_no_replay")
        if c.effect != "READ_ONLY":
            raise NerveHold("external_effect_not_authorized_here")
        if c.mode == "DISCOVERY_ONLY":
            raise NerveHold("discovery_is_not_execution")
        if c.mode == "HOST_METHOD":
            # A method-only request cannot be turned into an owner ACK by text.
            raise NerveHold("host_method_no_independent_owner_call")
        if c.mode != "LOCAL_ADAPTER":
            raise NerveHold("unknown_or_unsupported_dispatch_mode")
        fn = self.implementations.get(c.function_id)
        if not callable(fn):
            raise NerveHold("missing_actual_adapter")
        # Do not mark a request completed before the adapter's return is observed.
        result = fn(dict(request.payload))
        if not isinstance(result, dict) or result.get("kind") != c.output_type:
            raise NerveHold("invalid_owner_return_type")
        delta = result.get("delta")
        if not isinstance(delta, str) or not delta.strip():
            raise NerveHold("missing_observed_delta")
        self.completed.add(event_key)
        return Receipt(request.mission_id, request.revision, request.trace_id,
                       c.function_id, c.owner_id, request.operation_id,
                       c.output_type, delta, "LOCAL_ADAPTER_RETURN_OBSERVED")

    @staticmethod
    def native_callability():
        """Independent remote original-organ execution is not implemented."""
        return "HOLD_NATIVE_OWNER_AUTHENTICATION_AND_INTERFACE"
