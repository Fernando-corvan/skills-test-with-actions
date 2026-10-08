"""Corvan contract-chain lab: deterministic fixture, not autonomous Casa runtime."""
from dataclasses import dataclass, replace
from hashlib import sha256
import json


class ChainBlocked(ValueError):
    pass


def require(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ChainBlocked("missing:" + name)
    return value


def digest(value):
    return sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()[:16]


@dataclass(frozen=True)
class Mission:
    mission_id: str
    revision: str
    fingerprint: str
    trace_id: str
    source_revision: str


@dataclass(frozen=True)
class Questions:
    mission_id: str
    revision: str
    question_ref: str
    functions: tuple


@dataclass(frozen=True)
class Route:
    mission_id: str
    revision: str
    fingerprint: str
    trace_id: str
    graph_ref: str
    owner_map_ref: str
    selected: tuple


@dataclass(frozen=True)
class Thread:
    mission_id: str
    revision: str
    fingerprint: str
    trace_id: str
    source_revision: str
    question_ref: str
    graph_ref: str
    owner_map_ref: str
    relations: tuple
    proofs: tuple
    checkpoint_ref: str
    semantic_ref: str
    invalidated: tuple = ()


def route(mission, questions, owners):
    """Route only requested functional responsibilities, not all brothers."""
    for field in vars(mission):
        require(getattr(mission, field), field)
    if (mission.mission_id, mission.revision) != (
            questions.mission_id, questions.revision):
        raise ChainBlocked("mission_revision_mismatch")
    require(questions.question_ref, "question_ref")
    if not questions.functions:
        raise ChainBlocked("no_required_function")
    selected = []
    for func in dict.fromkeys(questions.functions):
        require(func, "function")
        selected.append((func, require(owners.get(func), "owner:" + func)))
    selected = tuple(selected)
    return Route(mission.mission_id, mission.revision, mission.fingerprint,
                 mission.trace_id, "graph:" + digest((mission.mission_id, selected)),
                 "owners:" + digest(selected), selected)


def bind(mission, questions, routing, relations, proofs,
         checkpoint_ref, semantic_ref):
    """Keep owner, graph, identity and semantic/provenance references."""
    if (routing.mission_id, routing.revision, routing.fingerprint,
            routing.trace_id) != (mission.mission_id, mission.revision,
                                 mission.fingerprint, mission.trace_id):
        raise ChainBlocked("route_mismatch")
    if (questions.mission_id, questions.revision) != (
            mission.mission_id, mission.revision):
        raise ChainBlocked("question_mismatch")
    for label, value in (("graph_ref", routing.graph_ref),
                         ("owner_map_ref", routing.owner_map_ref),
                         ("checkpoint_ref", checkpoint_ref),
                         ("semantic_ref", semantic_ref)):
        require(value, label)
    if len(set(relations)) != len(relations):
        raise ChainBlocked("duplicate_relation")
    for ref in tuple(relations) + tuple(proofs):
        require(ref, "evidence_or_relation_ref")
    return Thread(mission.mission_id, mission.revision, mission.fingerprint,
                  mission.trace_id, mission.source_revision,
                  questions.question_ref, routing.graph_ref,
                  routing.owner_map_ref, tuple(relations), tuple(proofs),
                  checkpoint_ref, semantic_ref)


def invalidate(thread, ref):
    if ref not in thread.relations:
        raise ChainBlocked("unknown_relation")
    if ref in thread.invalidated:
        return thread
    return replace(thread, invalidated=thread.invalidated + (ref,))


def verify(mission, routing, thread):
    """PASS means local contract fixture only; never live Casa runtime."""
    if (mission.mission_id, mission.revision, mission.fingerprint,
            mission.trace_id, mission.source_revision) != (
            thread.mission_id, thread.revision, thread.fingerprint,
            thread.trace_id, thread.source_revision):
        raise ChainBlocked("continuity_mismatch")
    if (routing.graph_ref, routing.owner_map_ref) != (
            thread.graph_ref, thread.owner_map_ref):
        raise ChainBlocked("routing_evidence_mismatch")
    blockers = []
    if not thread.proofs:
        blockers.append("missing_proof")
    if not thread.relations:
        blockers.append("missing_relations")
    if thread.invalidated:
        blockers.append("revalidation_required")
    return {"status": "HOLD" if blockers else "PASS_LOCAL_FIXTURE",
            "blockers": tuple(blockers), "trace_id": thread.trace_id}


def resume(thread, checkpoint, operation):
    """Do not replay already-completed or committed external effects."""
    if (checkpoint["mission_id"], checkpoint["revision"],
            checkpoint["checkpoint_ref"]) != (
            thread.mission_id, thread.revision, thread.checkpoint_ref):
        raise ChainBlocked("checkpoint_mismatch")
    require(operation, "operation")
    if operation in checkpoint["committed_effects"]:
        raise ChainBlocked("committed_effect_replay")
    if operation in checkpoint["completed"]:
        raise ChainBlocked("completed_replay")
    if operation not in checkpoint["pending"]:
        raise ChainBlocked("not_pending")
    return operation
