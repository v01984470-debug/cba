from typing import Dict
from app.utils.audit import append_audit


def run_nostro(state: Dict) -> Dict:
    """Perform MT940 reconciliation and store result in state as `nostro_result`."""
    repos = state.get("repositories", {})
    p004 = state.get("parsed_pacs004", {})

    result = {"found": False, "match_type": "none", "nostro_entry": None}

    try:
        if repos and "statements" in repos and p004:
            statement_repo = repos["statements"]
            reference = p004.get("e2e", "")
            uetr = p004.get("uetr", "")
            amount = float(p004.get("rtr_amount", 0))
            currency = p004.get("rtr_ccy", "")
            result = statement_repo.find_nostro_match(
                reference, uetr, amount, currency)
    except Exception as e:
        # attach error details but keep a safe default result
        result = {"found": False, "match_type": "error",
                  "nostro_entry": None, "error": str(e)}

    state["nostro_result"] = result
    state = append_audit(state, "nostro", "reconciled", {"result": result})
    return state

