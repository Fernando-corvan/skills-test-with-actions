"""Forensic admission for a requested historic numeric opcode (laboratory only).

This module is *not* opcode 50. It forbids testing an unrelated M50 module
or inferring functionality when the original numbered body was not found.
"""
import re


def _valid_text(value):
    return isinstance(value, str) and bool(value.strip())


def _exact_candidate_title(number, title):
    if type(number) is not int or number < 0 or number > 9999:
        return False
    if not _valid_text(title):
        return False
    # Numeric ID belongs to the start of a standalone file, not M50 or 3507.
    pattern = r"^0*" + str(number) + r"(?:_[A-Z]{1,5})?_CORVAN(?:_|$)"
    return re.match(pattern, title) is not None


def assess_opcode_primary_source(number, candidates):
    """Return discovery status. Does not run, emulate, or certify the opcode.

    A title is discovery evidence only. A document body and owner/contract
    reconciliation are necessary before attempting a real functionality test.
    """
    if type(number) is not int or not (0 <= number <= 9999):
        return {"status": "BLOCKED_INVALID_NUMBER", "tested_original": False}
    if not isinstance(candidates, list):
        return {"status": "HOLD_DISCOVERY_INPUT", "tested_original": False}

    hits = []
    for item in candidates:
        if not isinstance(item, dict):
            return {"status": "HOLD_DISCOVERY_INPUT", "tested_original": False}
        if _exact_candidate_title(number, item.get("title")):
            hits.append(item)

    if not hits:
        return {"number": number, "status": "HOLD_SOURCE_NOT_LOCATED",
                "original_body_found": False, "tested_original": False,
                "next": "Search primary Casa source with L0/4103; do not guess owner"}
    if len(hits) > 1:
        return {"number": number, "status": "HOLD_NUMERIC_COLLISION",
                "matches": len(hits), "tested_original": False,
                "next": "L0/4103 reconcile exact home, lineage and current carrier"}

    hit = hits[0]
    if not _valid_text(hit.get("document_id")) or not _valid_text(hit.get("revision")):
        return {"number": number, "status": "HOLD_SOURCE_IDENTITY",
                "tested_original": False}
    if hit.get("primary_body_readback") is not True:
        return {"number": number, "status": "HOLD_PRIMARY_BODY",
                "tested_original": False}
    if not _valid_text(hit.get("owner")) or not _valid_text(hit.get("contract_ref")):
        return {"number": number, "status": "HOLD_OWNER_OR_CONTRACT",
                "tested_original": False}

    return {"number": number, "status": "READY_TO_DESIGN_FUNCTIONAL_TESTS",
            "source_revision": hit["revision"], "tested_original": False,
            "claim": "source located only; functional behavior not yet exercised"}
