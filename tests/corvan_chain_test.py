"""T01-T08 Corvan cross-organ contract-fixture regression and adversarial tests."""
import os
import sys
from dataclasses import replace
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from corvan_mission_chain import (  # noqa: E402
    Mission, Questions, ChainBlocked, route, bind, invalidate, verify, resume,
)


@pytest.fixture
def case():
    m = Mission("M-01", "r4", "fingerprint:ext-L2",
                "trace:001", "source:rev-20")
    q = Questions("M-01", "r4", "questions:3768",
                  ("L2_MISSION", "ROUTE", "QA"))
    owners = {"L2_MISSION": "L2", "ROUTE": "705", "QA": "QA"}
    g = route(m, q, owners)
    t = bind(m, q, g, ("relation:a", "relation:b"),
             ("proof:source", "proof:readback"), "checkpoint:3731",
             "semantic:4312")
    return m, q, owners, g, t


def test_t01_t08_correlated_chain_local_only(case):
    m, q, owners, g, t = case
    assert q.mission_id == t.mission_id == g.mission_id == m.mission_id
    assert q.revision == t.revision == g.revision == m.revision
    assert g.selected == (("L2_MISSION", "L2"), ("ROUTE", "705"), ("QA", "QA"))
    assert t.fingerprint == m.fingerprint
    assert t.graph_ref == g.graph_ref
    assert t.owner_map_ref == g.owner_map_ref
    assert t.semantic_ref == "semantic:4312"
    assert verify(m, g, t) == {"status": "PASS_LOCAL_FIXTURE", "blockers": (),
                                "trace_id": m.trace_id}


def test_t02_dynamic_subset_not_all_owners(case):
    m, q, owners, _, _ = case
    q = replace(q, functions=("QA", "QA"))
    g = route(m, q, owners)
    assert g.selected == (("QA", "QA"),)


@pytest.mark.parametrize("changes,message", [
    ({"mission_id": "M-wrong"}, "mission_revision_mismatch"),
    ({"revision": "stale"}, "mission_revision_mismatch"),
    ({"question_ref": ""}, "missing:question_ref"),
    ({"functions": ()}, "no_required_function"),
    ({"functions": ("LOST",)}, "missing:owner:LOST"),
    ({"functions": ("",)}, "missing:function"),
])
def test_t02_block_bad_question_or_missing_owner(case, changes, message):
    m, q, owners, _, _ = case
    with pytest.raises(ChainBlocked, match=message):
        route(m, replace(q, **changes), owners)


@pytest.mark.parametrize("field", ["mission_id", "revision", "fingerprint",
                                     "trace_id", "source_revision"])
def test_t01_missing_mission_fields_block(case, field):
    m, q, owners, _, _ = case
    with pytest.raises(ChainBlocked, match="missing:" + field):
        route(replace(m, **{field: ""}), q, owners)


@pytest.mark.parametrize("field", ["mission_id", "revision", "fingerprint",
                                     "trace_id"])
def test_t03_route_receipt_mismatch_blocks(case, field):
    m, q, _, g, _ = case
    with pytest.raises(ChainBlocked, match="route_mismatch"):
        bind(m, q, replace(g, **{field: "tampered"}), ("r",), ("p",),
             "cp", "sem")


@pytest.mark.parametrize("field", ["graph_ref", "owner_map_ref"])
def test_t03_missing_graph_owner_receipt_blocks(case, field):
    m, q, _, g, _ = case
    with pytest.raises(ChainBlocked, match="missing:" + field):
        bind(m, q, replace(g, **{field: ""}), ("r",), ("p",), "cp", "sem")


@pytest.mark.parametrize("field", ["checkpoint_ref", "semantic_ref"])
def test_t04_missing_required_continuity_ref_blocks(case, field):
    m, q, _, g, _ = case
    values = {"checkpoint_ref": "cp", "semantic_ref": "sem"}
    values[field] = ""
    with pytest.raises(ChainBlocked, match="missing:" + field):
        bind(m, q, g, ("r",), ("p",), **values)


def test_t04_question_receipt_mismatch_blocks(case):
    m, q, _, g, _ = case
    with pytest.raises(ChainBlocked, match="question_mismatch"):
        bind(m, replace(q, revision="stale"), g, ("r",), ("p",), "cp", "sem")


def test_t05_duplicate_or_bad_evidence_blocks(case):
    m, q, _, g, _ = case
    with pytest.raises(ChainBlocked, match="duplicate_relation"):
        bind(m, q, g, ("r", "r"), ("p",), "cp", "sem")
    with pytest.raises(ChainBlocked, match="missing:evidence_or_relation_ref"):
        bind(m, q, g, ("",), ("p",), "cp", "sem")
    with pytest.raises(ChainBlocked, match="missing:evidence_or_relation_ref"):
        bind(m, q, g, ("r",), ("",), "cp", "sem")


def test_t06_targeted_invalidation_preserves_healthy_relations(case):
    m, _, _, g, t = case
    changed = invalidate(t, "relation:a")
    assert changed.relations == ("relation:a", "relation:b")
    assert changed.invalidated == ("relation:a",)
    assert invalidate(changed, "relation:a") == changed
    assert verify(m, g, changed)["blockers"] == ("revalidation_required",)
    with pytest.raises(ChainBlocked, match="unknown_relation"):
        invalidate(t, "invented")


def test_t05_no_proof_or_relation_is_hold_not_false_pass(case):
    m, _, _, g, t = case
    assert verify(m, g, replace(t, proofs=()))["blockers"] == ("missing_proof",)
    assert verify(m, g, replace(t, relations=()))["blockers"] == ("missing_relations",)


def test_t05_forged_state_or_owner_receipt_blocks(case):
    m, _, _, g, t = case
    with pytest.raises(ChainBlocked, match="continuity_mismatch"):
        verify(m, g, replace(t, source_revision="forged"))
    with pytest.raises(ChainBlocked, match="routing_evidence_mismatch"):
        verify(m, replace(g, graph_ref="forged"), t)


def test_t07_checkpoint_resume_no_replay(case):
    _, _, _, _, t = case
    cp = dict(mission_id=t.mission_id, revision=t.revision,
              checkpoint_ref=t.checkpoint_ref, completed=("done",),
              pending=("next",), committed_effects=("sent-email",))
    assert resume(t, cp, "next") == "next"
    for op, message in [("done", "completed_replay"),
                        ("sent-email", "committed_effect_replay"),
                        ("unknown", "not_pending"),
                        ("", "missing:operation")]:
        with pytest.raises(ChainBlocked, match=message):
            resume(t, cp, op)
    with pytest.raises(ChainBlocked, match="checkpoint_mismatch"):
        resume(t, dict(cp, checkpoint_ref="other"), "next")
