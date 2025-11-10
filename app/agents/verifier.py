from typing import Dict
from app.utils.audit import append_audit


def run_verifier(state: Dict) -> Dict:
    cross = state.get("investigator_cross_errors", [])
    csv_val = state.get("investigator_csv_validation", {"ok": False})
    elig = state.get("investigator_eligibility", {})
    repos = state.get("repositories", {})

    # Get parsed data
    p004 = state.get("parsed_pacs004", {})
    p008 = state.get("parsed_pacs008", {})

    # MT940 reconciliation (prefer result from nostro agent if present)
    nostro_result = state.get("nostro_result") or {
        "found": False, "match_type": "none", "nostro_entry": None}
    if nostro_result is None:
        nostro_result = {"found": False,
                         "match_type": "none", "nostro_entry": None}
    if (not nostro_result or not isinstance(nostro_result, dict)) and repos and "statements" in repos:
        statement_repo = repos["statements"]
        reference = p004.get("e2e", "")
        uetr = p004.get("uetr", "")
        amount = float(p004.get("rtr_amount", 0))
        currency = p004.get("rtr_ccy", "")
        nostro_result = statement_repo.find_nostro_match(
            reference, uetr, amount, currency)

    checks = {
        "sequence_ok": True,
        "cross_checks_ok": not cross,
        "csv_validation_ok": csv_val.get("ok", False),
        "non_branch_ok": bool(elig.get("non_branch")),
        "sanctions_ok": bool(elig.get("sanctions_ok")),
        "fx_loss_within_limit": bool(elig.get("fx_loss_within_limit")),
        "nostro_match_found": nostro_result.get("found", False),
        "nostro_match_type": nostro_result.get("match_type", "none"),
    }
    reconciliation_ok = all(checks.values())

    # Always compute linear process comparisons for reporting
    flow_expected = {
        "payments_team_rejection_email": False,
        "correct_payment_attached": True,
        "has_mt103_message": False,
        "has_202_message": False,
        "is_aud_payment": False,
        "amendment_previously_sent": False,
        "returned_due_to_cba_fca": False,
        "charges_prevent_return": False,
        "return_reason_clear": True,
        "is_markets_payment": False,
        "remitter_account_closed": False,
        "returned_due_to_value_date": False,
        "ofi_advised_iban_invalid": False,
        "reason_internal_policy": False,
        "reason_correspondent_issue": False,
        "reason_wrong_currency": False,
        "client_amending_instructions": False,
        "loss_amount_gt_300": False,
    }
    flow_actual = state.get("decisions", {})
    flow_ok = True
    flow_diffs = []
    flow_checks = []
    readable_labels = {
        "payments_team_rejection_email": "Payments team advised rejection",
        "correct_payment_attached": "Correct payment attached",
        "has_mt103_message": "MT103 present",
        "has_202_message": "202 present",
        "is_aud_payment": "AUD payment",
        "amendment_previously_sent": "Amendment previously sent",
        "returned_due_to_cba_fca": "Return due to CBA FCA",
        "charges_prevent_return": "No funds due to charges",
        "return_reason_clear": "Return reason clear",
        "is_markets_payment": "Markets payment",
        "remitter_account_closed": "Remitter account closed",
        "returned_due_to_value_date": "Return due to Value Date",
        "ofi_advised_iban_invalid": "OFI advised IBAN invalid",
        "reason_internal_policy": "Reason: Internal policy",
        "reason_correspondent_issue": "Reason: Correspondent issue",
        "reason_wrong_currency": "Reason: Wrong currency",
        "client_amending_instructions": "Client provided amending instructions",
        "loss_amount_gt_300": "Loss amount > 300 AUD",
    }
    for k, exp in flow_expected.items():
        actual_val = flow_actual.get(k)
        ok = (actual_val == exp)
        if not ok:
            flow_ok = False
            flow_diffs.append(
                {"decision": k, "expected": exp, "actual": actual_val})
        flow_checks.append({
            "key": k,
            "label": readable_labels.get(k, k.replace("_", " ").title()),
            "ok": ok,
            "actual": bool(actual_val),
            "expected": bool(exp),
        })
    checks["process_flow_ok"] = flow_ok

    exceptions = []
    if cross:
        exceptions.extend(cross)
    if not csv_val.get("ok", False):
        exceptions.extend(csv_val.get("errors", []))
    for k, v in checks.items():
        if not v:
            exceptions.append(f"Check failed: {k}")

    # Determine decision outcome
    decision = "approve_and_process"
    decision_reason = "All verification checks passed"

    if not reconciliation_ok or not checks.get("nostro_match_found", False):
        if not checks.get("nostro_match_found", False):
            decision = "resend_to_investigator"
            decision_reason = "Nostro match not found - needs clarification"
        else:
            decision = "human_intervention"
            decision_reason = "Verification issues require human review"

    results = {
        "checks": checks,
        "reconciliation_ok": reconciliation_ok,
        "eligibility_flags": elig,
        "nostro_result": nostro_result,
        "decision": decision,
        "decision_reason": decision_reason,
    }
    results["process_flow_expected"] = flow_expected
    results["process_flow_actual"] = state.get("decisions", {})
    results["process_flow_diffs"] = flow_diffs
    results["process_flow_checks"] = flow_checks
    state.update({"verifier_summary": results,
                 "verifier_exceptions": exceptions})
    state = append_audit(state, "verifier", "verified", {
                         "checks": checks, "reconciliation_ok": reconciliation_ok, "exceptions": exceptions, "decision": decision, "decision_reason": decision_reason})
    return state
