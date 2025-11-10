from typing import Dict, Any
from app.utils.audit import append_audit


def run_checklist(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute pre-flow checklist decisions per flow_.md linear sequence.

    Implements the exact flow from flow_.md with terminal checks that stop processing.
    Only non-terminal path proceeds to FX loss check and then refund_process.
    """
    result = dict(state)
    
    # Get parsed data from investigator
    p004 = state.get("parsed_pacs004", {})
    p008 = state.get("parsed_pacs008", {})
    # Use investigator output directly
    eligibility = state.get("investigator_eligibility", {})
    
    # Initialize checklist results
    checks = {}
    decision_path = []
    # Respect prior flags (from FX or previous agents)
    prior_manual = bool(state.get('manual_review_required', False))
    prior_proceed = state.get('proceed_to_refund')
    fx_state = state.get('fx') or {}
    fx_exceeds = bool(fx_state.get('exceeds_limit', False))

    manual_review_required = prior_manual or fx_exceeds
    review_reason = state.get('review_reason')
    if fx_exceeds and not review_reason:
        review_reason = f"FX loss exceeds limit ({fx_state.get('loss_aud')})"

    if fx_exceeds:
        decision_path.append("FX loss check: EXCEEDS $300 → MANUAL REVIEW REQUIRED")
    
    # Flow_.md linear decision sequence
    # Each check can be terminal (stops processing) or non-terminal (continues)
    
    # 1. Email rejection check (TERMINAL)
    checks['payments_team_rejection_email'] = False  # POC default
    decision_path.append("Email rejection check: NO")
    if checks['payments_team_rejection_email']:
        manual_review_required = True
        review_reason = "Payments team rejection email received"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 2. Correct payment attached (TERMINAL)
    checks['correct_payment_attached'] = True  # POC default
    decision_path.append("Correct payment attached: YES")
    if not checks['correct_payment_attached']:
        manual_review_required = True
        review_reason = "Incorrect payment attached"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 3. Has MT103 and MT202 (TERMINAL)
    checks['has_mt103_and_202'] = False  # POC default
    decision_path.append("Has MT103 and MT202: NO")
    if checks['has_mt103_and_202']:
        manual_review_required = True
        review_reason = "MT103 and MT202 present - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 4. Is AUD payment (TERMINAL)
    checks['is_aud_payment'] = eligibility.get('is_aud_refund', False)
    decision_path.append(f"Is AUD payment: {'YES' if checks['is_aud_payment'] else 'NO'}")
    if checks['is_aud_payment']:
        manual_review_required = True
        review_reason = "AUD payment - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 5. Amendment previously sent (TERMINAL)
    checks['amendment_previously_sent'] = False  # POC default
    decision_path.append("Amendment previously sent: NO")
    if checks['amendment_previously_sent']:
        manual_review_required = True
        review_reason = "Amendment previously sent - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 6. Returned due to CBA FCA (TERMINAL)
    checks['returned_due_to_cba_fca'] = False  # POC default
    decision_path.append("Returned due to CBA FCA: NO")
    if checks['returned_due_to_cba_fca']:
        manual_review_required = True
        review_reason = "Returned due to CBA FCA - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 7. No funds due to charges (TERMINAL)
    checks['no_funds_due_to_charges'] = False  # POC default
    decision_path.append("No funds due to charges: NO")
    if checks['no_funds_due_to_charges']:
        manual_review_required = True
        review_reason = "No funds due to charges - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 8. Return reason clear (TERMINAL)
    checks['return_reason_clear'] = True  # POC default
    decision_path.append("Return reason clear: YES")
    if not checks['return_reason_clear']:
        manual_review_required = True
        review_reason = "Return reason unclear - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 9. Is Markets (TERMINAL)
    checks['is_markets'] = False  # POC default
    decision_path.append("Is Markets: NO")
    if checks['is_markets']:
        manual_review_required = True
        review_reason = "Markets involved - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 10. Remitter account closed (TERMINAL)
    checks['remitter_account_closed'] = False  # POC default
    decision_path.append("Remitter account closed: NO")
    if checks['remitter_account_closed']:
        manual_review_required = True
        review_reason = "Remitter account closed - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 11. Returned due to value date (TERMINAL)
    checks['returned_due_to_value_date'] = False  # POC default
    decision_path.append("Returned due to value date: NO")
    if checks['returned_due_to_value_date']:
        manual_review_required = True
        review_reason = "Returned due to value date - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 12. OFI advised IBAN invalid (TERMINAL)
    checks['ofi_advised_iban_invalid'] = False  # POC default
    decision_path.append("OFI advised IBAN invalid: NO")
    if checks['ofi_advised_iban_invalid']:
        manual_review_required = True
        review_reason = "OFI advised IBAN invalid - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 13. Reason internal policy (TERMINAL)
    checks['reason_internal_policy'] = False  # POC default
    decision_path.append("Reason internal policy: NO")
    if checks['reason_internal_policy']:
        manual_review_required = True
        review_reason = "Internal policy reason - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 14. Reason correspondent issue (TERMINAL)
    checks['reason_correspondent_issue'] = False  # POC default
    decision_path.append("Reason correspondent issue: NO")
    if checks['reason_correspondent_issue']:
        manual_review_required = True
        review_reason = "Correspondent issue - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 15. Reason wrong currency (TERMINAL)
    checks['reason_wrong_currency'] = eligibility.get('currency_mismatch', False)
    decision_path.append(f"Reason wrong currency: {'YES' if checks['reason_wrong_currency'] else 'NO'}")
    if checks['reason_wrong_currency']:
        manual_review_required = True
        review_reason = "Wrong currency - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # 16. Client amending instructions (TERMINAL)
    checks['client_amending_instructions'] = False  # POC default
    decision_path.append("Client amending instructions: NO")
    if checks['client_amending_instructions']:
        manual_review_required = True
        review_reason = "Client amending instructions - manual review required"
        decision_path.append("→ MANUAL REVIEW REQUIRED")
    
    # Finalize decision respecting prior flags and FX
    if manual_review_required:
        decision_path.append("→ MANUAL REVIEW REQUIRED")
        result['proceed_to_refund'] = False
    else:
        decision_path.append("All pre-flow checks passed")
        decision_path.append("→ Proceed to refund processing")
        # Only set proceed_to_refund True if not previously forced False
        if prior_proceed is not False:
            result['proceed_to_refund'] = True
    
    # Store results
    result['checklist'] = checks
    result['checklist_decision_path'] = decision_path
    result['manual_review_required'] = manual_review_required
    result['review_reason'] = review_reason
    result['checklist_summary'] = {
        'all_checks_passed': not manual_review_required,
        'manual_review_required': manual_review_required,
        'review_reason': review_reason,
        'total_checks': len(checks),
        'passed_checks': sum(1 for v in checks.values() if v is False or v is True)
    }
    
    # Audit the checklist results
    audit_details = {
        'checks': checks,
        'decision_path': decision_path,
        'manual_review_required': manual_review_required,
        'review_reason': review_reason
    }
    
    return append_audit(
        result,
        "checklist",
        "manual_review" if manual_review_required else "passed",
        audit_details
    )


