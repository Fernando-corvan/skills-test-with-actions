# CORVAN nerve handoff adapter — laboratory only

**Purpose:** exercise the existing 705 preselected mission route through a bounded typed handoff and receipt interface. This is an adapter, not a new brother, registry, route owner, Crown lens, or autonomous process.

## Contract map

- **701 / 713:** supply externally verified function owner and source revision; this fixture uses small stand-in contracts, not live Drive registration.
- **703:** defines allowed typed inter-function relations; no graph ownership added here.
- **705:** selects needed (function_id, owner_id) pairs with `corvan_mission_chain.route`; `NerveAdapter` only consumes that route and never chooses functions.
- **4411:** validates a read-only request/return expectation and records a correlated local adapter receipt. It does not authenticate independent service calls by itself.
- **House Awareness:** pointer source; not activation/authority.

## Positive case

`test_two_adapter_calls_have_real_local_returns` calls two Python callbacks once each under separate typed owner/function IDs. Observations are tagged `LOCAL_ADAPTER_RETURN_OBSERVED`. This **proves local fixture dispatch**, NOT Casa original owner execution or an RPC to Panorama/Instinto.

## Negative gates

Missing/stale source revision, stale route, owner mismatch, forged mission/trace, unsupported input/return, absent adapter, replayed operation, unapproved write effect, and invocation of unavailable Destino or independent Nexus call are blocked. Only read-only local adapters may run in this version.

## Run

```sh
python -m pytest -q tests/test_corvan_nerve_adapter.py
```

This test imports the existing `src/corvan_mission_chain.py`; it does not replace the original 705-owned routing capability.

## Current proof ceiling

`LOCAL_ADAPTER_RETURN_OBSERVED`, tests performed on GitHub Actions/host within their scope. **NOT PROVEN**: external owner-origin authenticated return; continuous worker; live transport to real Casa opcodes; independent Nexus runtime; Destino activation; global canon or Master Index promotion. A PR/CI PASS is not a Casa admission receipt.

## Next legal step

Under the original 4411/705 owners and human authorization, inject a real **read-only** authenticated provider adapter that returns a source-origin, revision-bound observation. Independently verify the connector's owner/origin and observed effect, create QA + WAL + Reanchor, and request Casa 2.0 admission through the existing `protocols/lab_to_casa.md` process in the private memory repository. Do not merge or promote to runtime on lab tests alone.
