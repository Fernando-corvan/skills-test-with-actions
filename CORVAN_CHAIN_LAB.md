# CORVAN GH LAB — Mission / Context / QA cross-organ contract chain

STATUS: LABORATORY_FIXTURE_ONLY — not the active Casa runtime, not canon, no Drive mutations.

## Source authority
The working definitions are reused verbatim in substance from the **private** `Fernando-corvan/corvan-agent-memory` repository, `architecture/factory/function-mechanism-capability.md`. Do not reproduce private content in public fixtures beyond the minimum classification. Canonical Casa documents stay external and authoritative; this lab neither certifies nor embeds their full bodies.

External Casa pointers (Drive document IDs): 3768 `1-bsDaekLKBhD6M4wZ_3xSpTJxdTFsnjBBBNvWSusl8U`, 3733 `1qlCzgDbilWVrTIdak5Wh9jhkE6DCRRbERbYRwKYoVlU`, 705 `1rct107cPzs101YzJDw4zITNKNTMHdQLjqc7UbjrH74A`, 4208 `1r5PHFzmIMHfuh3S55r3yGYNuM6PTeCTOIInbw-A0QTg`, 4312 `1k5A_fQD14UlQhSk89762UaLQX-TXJOKWgnyQQ5w-28U`, 3731 `1D6oKn8p5ZEd2HKjdG7-ZZV2rkvybXPmEzWHrW4I5WGc`.

Reconciliation record: `1mg7P9c-kd1p78sRx_SKD3AB821P0vMI9KX96nDoo9E0` (QA15/01). MAPS/05 pointer: `15oDZgK9K3c67eo8_6Uhu5Pz3zQRH-puPCJrO8DBFEN8`.

## Distinct architectural types

| Type | Meaning | Here |
| --- | --- | --- |
| **Function** | Durable responsibility: *what must be ensured*, with primary owner and authority ceiling | Preserve a mission and its QA integrity |
| **Mechanism** | Bounded causal transformation: trigger + inputs + operation + output delta + failure/reentry | `route`, `bind`, `invalidate`, `verify`, `resume` |
| **Capability** | Demonstrable ability under specified preconditions, interface and evidence | Correctly correlates simulated packet fields and blocks specific invalid handoffs under pytest |
| **Module** | Software packaging, not a function or authority | `src/corvan_mission_chain.py` |
| **Owner** | Current authorized organ accountable for the function | Resolved separately; test uses explicit fixture labels, never grants authority |
| **MAPS** | Discoverability / pointers, not runtime ownership | External document pointers only |

`FUNCTION != MECHANISM != CAPABILITY != MODULE`; `CAPABILITY != OWNER`; `DISCOVERY != ACTIVATION`; `CALL_DONT_COPY`.

## Experimental scope

This test creates **typed local stand-ins** for 3768 questions, 705 route receipts, 4208 continuity thread, a QA result, and a 3731 checkpoint. It checks necessary invariants without calling Drive or a running Casa dispatcher. A `PASS_LOCAL_FIXTURE` proves only that the Python implementation passed the specified fixtures.

Flow is *need-driven*, not a mandatory L0–L7 serial march:

```text
Mission (stable identity + source revision)
  + Questions (same mission ID/revision, required function signatures)
      -> route() : minimal selected (function, owner) edges + graph/owner refs
      -> bind()  : mission/graph/owner/semantic/proof/checkpoint continuity
      -> verify(): PASS_LOCAL_FIXTURE / HOLD, never runtime claim
      -> invalidate(): invalidate only affected edge; healthy edges remain
      -> resume(): prohibit replay of committed/completed work
```

## Gates tested

- T01: Preserve mission identity, revision, fingerprint and trace ID; block missing identity.
- T02: Select only material functions and current owners; reject absent owner or stale question.
- T03: Reject manipulated route receipt or absent graph / owner map.
- T04: Preserve question, checkpoint and semantic references; reject mismatched question revision.
- T05: Reject fabricated receipt/evidence refs; absence of proof is HOLD, not false PASS.
- T06: Local invalidation preserves unrelated relations and requires revalidation.
- T07: Resume from compatible checkpoint; prohibit replay of committed side effects.
- T08: Correlated QA result and trace with explicit local-only verdict; no promotion claim.

## Test command
`python -m pytest -q tests/corvan_chain_test.py`

The existing `Python package` and `Python Coverage` GitHub Actions workflows must run on PR. Gate: do not merge with failing required checks. After merge, read back `main`.

## Known limits and next step

- The actual 3768->705->4208->QA runtime handoffs are **not invoked**, so integration of original Casa organs remains **NOT_PROVEN**.
- The test does not implement 3992 or 4312 internal semantic adjudication; it preserves opaque provenance/semantic references only.
- No active state or canonical claim about 4411/4420.
- GitHub Actions execution is a genuine Python test in the test repository but **not** proof of cross-House autonomous execution.
- Next: connect authentic read-only packet adapters under existing authorization and measure one end-to-end trace with exact receipt IDs, live state readback and independent QA.
