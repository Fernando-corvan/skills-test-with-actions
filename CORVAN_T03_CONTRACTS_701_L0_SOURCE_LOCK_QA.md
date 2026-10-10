# CORVAN · T03 Contracts · 701/L0 source-bound evidence gate

Status: **LAB_ONLY / NOT_NATIVE / NO_DRIVE_WRITES / NOT_A_701_REGISTRATION**.

## Mother question
Can COG02 emit an evidence-grounded request to the **705 route owner** for the historical T03 Contracts relation, while preserving the independent functions of 03 and 08 and refusing fabricated 701 Q_OP/A_OP signatures, stale source revisions, unconfirmed L0 interfaces, or false route/execution claims?

## Original Drive source-locks observed
- **03_CORVAN_MESSAGE_EVENT_CONTRACT** — ID `1v3tRTw01GClNpqC-v25j_HyFED1_FWMqFMRpR-sP6N8`; revision `AHj4eMTc3iWPurGhPbEeuPMswSen83DKRq_O565-AvOTK-tZSTnKqhc61hOSL8jlItCmA6eYygyCvbX5893BJMf726UHutKEf3gAHTrMamQ`; physical parent `1n-Fmnl7wvC_3nQge16xqZktk5gJGSdnH`; status in document **ACTIVE_DRAFT_READY_TO_REVIEW**. Role: typed event/message envelope, event_id, source/target, correlation/causation, WAL refs, ACK and idempotency contract.
- **08_CORVAN_FAILURE_RETRY_POLICY_SCHEMA** — ID `1RtFVefDvE5qbEiX8u3QMMmqiguXRxpq5236SWOcu3Ss`; revision `ANLCKQkwLxOm1qdxrYv9nTRKGKsnG74NAOrYPXVD2u7peJE5zBLOW4HxwJLjfxtzJeB-PsH-jwJHXtUOYn14VbxQo-2BbY2Y1crbG-V8Dj8`; same parent; document status **READY_TO_REVIEW**. Role: retry eligibility, safe-retry budget, idempotency, circuit breaker, backoff, rollback/reentry.
- **701_C registry** — ID `1HZgBtCv4TY1l4R0bSnv-POEhI9LAKq5am8mfDKBLuy4`; revision `ANLCKQm7hENC4zpox2ZHGnMsXG99dIXRvT0Tg0f_lLYPU65BSu6p2vPfY043BaM-n2l4ZVMd2hZNvjnl5ZgpRCRAoOskNYqpdJgMiujfIl8`. It defines Q_OP / A_OP required; **no individual T03 03/08 registered cards were found in its body**.
- **4200_C/L0** — ID `1zGQ4t65VG68Y15z5-qHD8TFDhP7X3mVyVx6JnzPF7OU`; revision `AHj4eMS1SOOil11q0IdLBVs3xTtNuAW70pC17xQzC4EguCfJzoiFbM014Fc5Vcr7F0F7KUx8jboiBBD2A5pwu6nOtFbOUV5xqPlVl9wLl4A`. It resolves original owner/home/currentness/interfaces but has **no 03/08 verified interface entries in its current body**.
- **COG02** — ID `1-9lDHYr0H5SYJ-OoDltEMRX133Sf2nlZe643ryLwSio`; owner-preserving composer, proposal-only, local candidate. Source Python v0.3 `src/corvan_cognitive_bridges_v03.py` on parent commit `d713ffc3951a48be8ec005a35479706f248dc9c5`; its request ownership stays under `705`, not COG02.

## Candidate questions/outputs — NOT YET 701-ADMITTED
- Proposed 03 question (Q_OP *candidate*): "Given an event with original source, target, mission context and schema, does its envelope meet source-bound event/ACK/idempotency and WAL trace requirements without conflating delivery with proof?"
  Proposed bounded answer (A_OP *candidate*): typed `MESSAGE_EVENT_VALIDATION_RESULT` or explicit `HOLD_MESSAGE_EVENT`, routed only by its owner.
- Proposed 08 question (Q_OP *candidate*): "Given a classified failure and current budget, idempotency status and recovery state, what recovery *policy decision* is permitted without retry storm or authority escalation?"
  Proposed bounded answer (A_OP *candidate*): typed `FAILURE_RETRY_POLICY_DECISION` (`RETRY_ELIGIBLE|REPAIR|ROLLBACK|OPEN_CIRCUIT|FAIL_CLOSED|ESCALATE`) with provenance/limits. This is a *candidate schema*, not a claim of an existing exact output class in the 08 body.

These are draft translations from the source mechanisms; the **owner of 701** must accept, revise, or reject each card. We did not silently insert them into 701 or create signatures from body prose.

## Evidence gate
Pure `evaluate_t03(source_locks, registry701, resolution_l0, mission_id, correlation_id)`:
1. Require exact, pinned original body identity and the same observed Contracts folder for both members.
2. Require two 701-admitted Q_OP/A_OP cards (one per distinct function), matching source revisions, owner, home, interface schema, registry entry references and readback provenance.
3. Require two L0-verified, current interface/owner bindings, independently matching the same original bodies and admitted 701 registry entries.
4. Only if all conditions pass, invoke the **existing COG02 v0.3 proposal parser** to build **a laboratory owner-bound candidate to 705**, not a selected route or sent packet.

**Observed documentary input:** 701 cards = `[]`; L0 bindings = `[]`. Therefore `HOLD_701_QOP_AOP_SIGNATURE`, no route.
**Synthetic positive:** properly shaped *fabricated fixture* cards return `LAB_ROUTE_REQUEST_ONLY`; this does **not** authenticate the producer, verify the real interfaces or authorize dispatch. Passing flags alone is not real provenance.

## Negative tests
Missing Q_OP or A_OP; invalid owner; swapped document/home; stale revision; duplicated claim; missing/contradictory interface; missing L0 receipt; unauthorized `EXECUTOR` authority; missing expected owners; malformed packet and false route/ACK. The code never calls Drive, 705, WAL, Crown or native 701/L0.

## Disposition
**NO NEW OPCODE, NO NEW GLOBAL NUMBER, NO SOURCE BODY CHANGE, NO 701 REGISTRATION, NO L0 REBIND.**
GitHub laboratory artifacts alone cannot authorize Drive amendments or present an authentic native T03 route. After independent CI, the next admissible action is a **proposed Q_OP/A_OP signature card review for 701 and exact L0 interface verification**, followed by a new live-source-readback test. The documentation must remain HOLD until that happens.
