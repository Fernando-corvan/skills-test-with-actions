# CORVAN GH LAB — Test Evidence Classifier organ

STATUS: `LAB_IMPLEMENTATION_ONLY / NONCANONICAL / NO_CASA_RUNTIME_CLAIM`

This laboratory organ implements the evidence-scope distinction defined in the private operational memory repository.

## Organ identity

```text
ORGAN_ID=TEO-01
ROLE=TEST_EVIDENCE_CLASSIFIER
TYPE=ASSURANCE_CONTROL_ORGAN
AUTHORITY=CLASSIFICATION_ONLY
TRUTH_OWNER=NO
CANON_OWNER=NO
```

It prevents a test result from being promoted beyond what was actually exercised.

## Labels

- `CF` — cognitive function
- `M` — mechanism
- `IF` — interface
- `CTRL` — control mechanism
- `SYS` — system behavior
- `ADAPT` — adaptive behavior

Every result is reported as:

```text
TEST_CLASS / EVIDENCE_LEVEL / RESULT
```

Examples:

```text
M/OBSERVED/PASS
IF/CROSS_COMPONENT/PASS
ADAPT/OBSERVED/PASS
```

## Hard boundaries

```text
M_PASS != CF_PASS
CF_PASS != SYS_PASS
LOCAL_FIXTURE_PASS != CASA_RUNTIME_PASS
DOCUMENT_EXISTS != OPERATIONAL_FUNCTION
```

## What the executable validator checks

- material receipt fields exist;
- class-specific evidence exists;
- interface/system tests show cross-component evidence;
- adaptive tests state both perturbation and preserved invariant;
- mechanism tests explicitly forbid inference to their parent function/system;
- local evidence cannot claim Casa runtime unless evidence level is `RUNTIME_BOUND`.

## Test command

```bash
python -m pytest -q tests/test_evidence_classifier_test.py
```

This fixture is deliberately small. Its purpose is not to simulate cognition; it is to prevent overclaiming about whatever cognition or mechanism another test exercises.
