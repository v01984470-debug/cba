from typing import Dict
from app.utils.xml_parsers import parse_pacs004, parse_pacs008
from app.utils.sqlite_repositories import create_repositories
from app.utils.audit import append_audit
from app.utils.reason_analyzer import analyze_return_reason
from app.utils.mt103_status import get_mt103_status
from app.utils.fx import convert_to_aud, get_aud_rate


AUTO_REFUND_FX_LOSS_AUD_LIMIT = 300.0


def run_investigator(state: Dict) -> Dict:
    p004_xml: str = state.get("pacs004_xml", "")
    p008_xml: str = state.get("pacs008_xml", "")
    ui_fx_loss_aud: float = float(state.get("fx_loss_aud", 0.0) or 0.0)
    non_branch: bool = bool(state.get("non_branch", False))
    sanctions_ok: bool = bool(state.get("sanctions", True))

    # Initialize repositories
    repos = create_repositories()
    customer_repo = repos['customers']
    account_repo = repos['accounts']

    p004 = parse_pacs004(p004_xml)
    p008 = parse_pacs008(p008_xml)

    cross_errs = []
    if p004.get("uetr") and p008.get("uetr") and p004["uetr"] != p008["uetr"]:
        cross_errs.append("UETR mismatch between PACS.004 and PACS.008")
    if p004.get("e2e") and p008.get("e2e") and p004["e2e"] != p008["e2e"]:
        cross_errs.append("EndToEndId mismatch between PACS.004 and PACS.008")
    # Customer cross-check should compare debtor IBANs across both messages
    if p004.get("dbtr_iban") and p008.get("dbtr_iban") and p004["dbtr_iban"] != p008["dbtr_iban"]:
        cross_errs.append(
            "Customer IBAN mismatch (PACS004 DbtrAcct vs PACS008 DbtrAcct)")

    # Validate customer against CSV using repository
    customer = customer_repo.get_customer_by_iban(p008.get("dbtr_iban", ""))
    csv_check = {
        "ok": customer is not None and customer.account_status == "Active",
        "customer": customer.__dict__ if customer else None,
        "iban": p008.get("dbtr_iban"),
        "holder_name": p008.get("dbtr_name"),
        "ccy": p008.get("ccy")
    }

    reason_analysis = analyze_return_reason(
        p004.get("rsn"), p004.get("rsn_info"))

    # Amounts and currencies
    orig_ccy = p008.get("ccy")
    rtr_ccy = p004.get("rtr_ccy")
    orig_amt = float(p008.get("amount") or 0.0)
    rtr_amt = float(p004.get("rtr_amount") or 0.0)

    # Check if return reason supports auto-refund
    reason_supports_auto_refund = reason_analysis.get(
        "auto_refund_eligible", False)

    # Check for currency mismatch (wrong currency scenario)
    currency_mismatch = (orig_ccy and rtr_ccy and orig_ccy != rtr_ccy)
    if currency_mismatch:
        # Currency mismatch should prevent auto-refund regardless of reason code
        reason_supports_auto_refund = False

    # Fetch rates and convert to AUD
    orig_rate = get_aud_rate(orig_ccy) if orig_ccy else None
    rtr_rate = get_aud_rate(rtr_ccy) if rtr_ccy else None
    orig_aud = (orig_amt * orig_rate) if (orig_rate is not None) else None
    rtr_aud = (rtr_amt * rtr_rate) if (rtr_rate is not None) else None

    # Compute loss
    fx_loss_aud = ui_fx_loss_aud
    if orig_aud is not None and rtr_aud is not None:
        fx_loss_aud = max(0.0, float(orig_aud) - float(rtr_aud))
    else:
        if orig_amt and rtr_amt and (orig_ccy == rtr_ccy):
            if orig_ccy == "AUD":
                fx_loss_aud = max(0.0, orig_amt - rtr_amt)
                if orig_aud is None:
                    orig_aud = orig_amt
                if rtr_aud is None:
                    rtr_aud = rtr_amt
            else:
                fx_loss_aud = ui_fx_loss_aud if ui_fx_loss_aud else max(
                    0.0, orig_amt - rtr_amt)

    is_aud_refund = (rtr_ccy == "AUD")
    fx_ok = fx_loss_aud <= AUTO_REFUND_FX_LOSS_AUD_LIMIT

    mt103 = get_mt103_status(p008.get("uetr"))
    mt103_sent = mt103.get("available") and mt103.get("status") == "SENT"
    elig_core = (is_aud_refund or fx_ok) and (
        not mt103_sent) and reason_supports_auto_refund
    eligibility = {
        "is_aud_refund": is_aud_refund,
        "fx_loss_aud": fx_loss_aud,
        "fx_loss_within_limit": fx_ok,
        "non_branch": non_branch,
        "sanctions_ok": sanctions_ok,
        "reason": p004.get("rsn"),
        "reason_info": p004.get("rsn_info"),
        "reason_analysis": reason_analysis,
        "reason_supports_auto_refund": reason_supports_auto_refund,
        "currency_mismatch": currency_mismatch,
        "mt103_status": mt103,
        "account_status": customer.account_status if customer else None,
        "eligible_auto_refund": elig_core and non_branch and sanctions_ok and csv_check.get("ok", False) and not cross_errs,
        # FX details for UI
        "original_amount": orig_amt,
        "original_currency": orig_ccy,
        "returned_amount": rtr_amt,
        "returned_currency": rtr_ccy,
        "original_amount_aud": orig_aud,
        "returned_amount_aud": rtr_aud,
        "original_aud_rate": orig_rate,
        "returned_aud_rate": rtr_rate,
    }

    # Process-Flow mandated decisions
    if True:
        decisions = {
            "payments_team_rejection_email": False,
            "correct_payment_attached": True,
            "has_mt103_message": False,
            "has_202_message": False,
            "is_aud_payment": (orig_ccy == "AUD"),
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
            "loss_amount_gt_300": bool(fx_loss_aud > 300.0),
        }
        state["decisions"] = decisions

    state.update({
        "parsed_pacs004": p004,
        "parsed_pacs008": p008,
        "investigator_cross_errors": cross_errs,
        "investigator_csv_validation": csv_check,
        "investigator_eligibility": eligibility,
        "repositories": repos,  # Pass repositories to next agents
    })
    state = append_audit(state, "investigator", "evaluated", {
        "cross_errors": cross_errs,
        "csv_ok": csv_check.get("ok"),
        "eligibility": eligibility,
    })
    return state
