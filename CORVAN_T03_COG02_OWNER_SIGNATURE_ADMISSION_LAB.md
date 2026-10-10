# T03 Contracts → 701/L0 → COG02 — isolated signature admission

## Why this exists

This is a **lab adapter**, not Casa CORVAN's active COG02 and not a new opcode.

The existing COG02 v0.3 adapter accepts a structurally plausible, caller-supplied
`function_owners` entry with `current=True`, `authority=REFERENCE_ONLY` and a
nonempty interface, then emits `ROUTE_REQUEST_ONLY`. That is insufficient when
`701_C` has **not recorded exact Q_OP/A_OP signatures** for the 03/08 Contracts
documents and L0 has **not independently resolved callable current interfaces**.

This lab tests a *pre-admission gate*, not an owner's signature service.

## Sources of truth consulted (current readback before the experiment)

| Source | Document ID | Provenance |
| --- | --- | --- |
| 03 Message/Event Contract | `1v3tRTw01GClNpqC-v25j_HyFED1_FWMqFMRpR-sP6N8` | Source family L_SHARED_CONTRACTS; draft/review, not an authenticated RPC service |
| 08 Failure/Retry Policy | `1RtFVefDvE5qbEiX8u3QMMmqiguXRxpq5236SWOcu3Ss` | Source family L_SHARED_CONTRACTS; review, not an authenticated RPC service |
| 701 Function Registry | `1HZgBtCv4TY1l4R0bSnv-POEhI9LAKq5am8mfDKBLuy4` | Requires individual brother ID, Q_OP, A_OP, home, route and output schema; no exact registered source-specific 03/08 cards found |
| 4200 L0 | `1zGQ4t65VG68Y15z5-qHD8TFDhP7X3mVyVx6JnzPF7OU` | Resolves owner/currentness/callable interface; exact 03/08 binding not observed |
| COG02 | `1-9lDHYr0H5SYJ-OoDltEMRX133Sf2nlZe643ryLwSio` | Candidate, nonactive, no global number |
| Existing QA preflight | `1rDaFjDJosyslqeaMhKR5ynzkX2NXFjdPnk0uACY8v4A` | Earlier T03 negative test is reused, not overwritten |

Private source revisions and the official Drive QA receipt are intentionally
**not embedded in this public lab**. The native owner's signed revision and
interface must arrive from a trusted provider; this code cannot authenticate them.

## Decision graph

```
03/08 exact source doc identities + pinned readback
  -> original COG01 candidate with both source refs
  -> 701 two individual cards, each with Q_OP/A_OP/function signature,
     source revision, home, route, owner and registry revision
  -> L0 two consistent owner/currentness/interface/return-expectation bindings
  -> bounded existing COG02 v0.3 adapter
  -> LAB_ROUTE_REQUEST_ONLY (fixture consistency only)
  -> next: original owners must attest independently
  -> only then is a real route request to 705 potentially admissible
```

**Without exact 701 cards:** `HOLD_701_QOP_AOP_SIGNATURE`.  
**Without L0 bindings:** `HOLD_L0_INTERFACE`.  
**Stale source:** `HOLD_SOURCE_REVISION`.  
**Forged execution assertion:** `BLOCKED_FALSE_EXECUTION`.

The output never invokes 705 or makes a native PASS claim, even with a
positive controlled test fixture. No source bodies, numeric slots, source
registries, or owner authority are modified.

## Commands

```bash
pytest -q tests/test_t03_cog02_signature_admission.py
pytest --verbose
```

## Gate to return to Casa

1. Real 701 function owner registers or explicitly rejects the distinct
   03/08 candidate Q_OP/A_OP signatures, citing source revisions.
2. Original L0 resolves original home, owner, **callable versus schema-only**
   interface, return contract and independent currentness for each.
3. The original COG02 candidate is retested against the authenticated
   records, not merely these Python fixtures.
4. QA records exact GitHub SHA and runtime status separately.
5. Any Drive addition remains append-only, scoped to the right QA/COG02
   home. No code transfer, activation or original 03/08 body edit from
   this lab without an additional, separately verified need.

## Security/assurance limit

Function signatures reconstructed from document prose are **draft candidates**
and not automatically signed 701 entries. A Google Doc URL/revision proves
document identity and can prove revision, but not a callable organ. A test
fixture containing `current=True` or a mock interface is not a valid L0
attestation. No new opcode or 705 route is warranted by this test alone.
