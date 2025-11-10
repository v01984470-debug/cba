"""
Prep Logger Agent - Anonymizes data and prepares MT103-formatted email to Intelli.
This agent runs before the investigator to prepare the case for processing.
"""

from typing import Dict, Any
from datetime import datetime
from app.utils.audit import append_audit
from app.utils.xml_parsers import parse_pacs004, parse_pacs008


def run_prep_logger(state: Dict) -> Dict:
    """
    Prep Logger agent that anonymizes PACS data and prepares MT103 email to Intelli.

    Args:
        state: Current state containing PACS.004 and PACS.008 XML data

    Returns:
        Updated state with prep_logger.email_payload containing MT103 email
    """
    try:
        # Extract XML data from state
        pacs004_xml = state.get("pacs004_xml", "")
        pacs008_xml = state.get("pacs008_xml", "")
        case_id = state.get("case_id", "UNKNOWN")

        if not pacs004_xml or not pacs008_xml:
            return _create_error_response(state, "Missing PACS XML data")

        # Parse PACS messages
        p004 = parse_pacs004(pacs004_xml)
        p008 = parse_pacs008(pacs008_xml)

        if not p004 or not p008:
            return _create_error_response(state, "Failed to parse PACS messages")

        # Store parsed data in state for downstream agents
        state["parsed_pacs004"] = p004
        state["parsed_pacs008"] = p008

        # Anonymize customer data
        anonymized_data = _anonymize_customer_data(p004, p008)

        # Generate MT103-formatted email
        mt103_email = _generate_mt103_email(
            p004, p008, anonymized_data, case_id)

        # Store email payload in state
        state["prep_logger"] = {
            "email_payload": mt103_email,
            "case_id": case_id,
            "anonymized_data": anonymized_data,
            "processing_timestamp": datetime.now().isoformat()
        }

        # Add audit event
        audit_details = {
            "case_id": case_id,
            "email_subject": mt103_email.get("subject", ""),
            "customer_email": mt103_email.get("customer_email", ""),
            "transaction_reference": mt103_email.get("reference", ""),
            "anonymization_applied": True
        }

        return append_audit(state, "prep_logger", "email_prepared", audit_details)

    except Exception as e:
        error_result = {
            "email_payload": None,
            "error": str(e),
            "processing_timestamp": datetime.now().isoformat()
        }
        state["prep_logger"] = error_result
        return append_audit(state, "prep_logger", "error", {"error": str(e)})


def _anonymize_customer_data(p004: Dict, p008: Dict) -> Dict:
    """Anonymize sensitive customer data while preserving structure."""
    return {
        "anonymized_creditor_name": _mask_name(p004.get("cdtr_name", "Unknown")),
        "anonymized_debtor_name": _mask_name(p008.get("dbtr_name", "Unknown")),
        "original_creditor_name": p004.get("cdtr_name", "Unknown"),
        "original_debtor_name": p008.get("dbtr_name", "Unknown"),
        "creditor_iban": p004.get("cdtr_iban", ""),
        "debtor_iban": p008.get("dbtr_iban", ""),
        "amount": p004.get("rtr_amount", 0),
        "currency": p004.get("rtr_ccy", ""),
        "return_reason": p004.get("rsn", ""),
        "return_reason_info": p004.get("rsn_info", "")
    }


def _mask_name(name: str) -> str:
    """Mask customer name for anonymization."""
    if not name or len(name) < 3:
        return "CUSTOMER"

    # Keep first letter and last letter, mask the middle
    if len(name) <= 4:
        return name[0] + "*" * (len(name) - 2) + name[-1]
    else:
        return name[0] + "*" * (len(name) - 2) + name[-1]


def _generate_mt103_email(p004: Dict, p008: Dict, anonymized: Dict, case_id: str) -> Dict:
    """Generate MT103-formatted email for Intelli."""

    # Extract transaction details
    transaction_ref = p004.get("e2e", "UNKNOWN")
    uetr = p004.get("uetr", "")
    amount = p004.get("rtr_amount", 0)
    currency = p004.get("rtr_ccy", "")
    return_reason = p004.get("rsn", "")
    return_reason_info = p004.get("rsn_info", "")

    # Format date (use current date for value date)
    value_date = datetime.now().strftime("%y%m%d")

    # Format amount with proper decimal separator
    formatted_amount = f"{amount:,.2f}".replace(",", "")

    # Generate MT103 message body
    mt103_body = f"""Reference: {case_id}
Subject: return of funds
Transaction reference: {transaction_ref}

:20:{transaction_ref}
:23B:CRED
:32A:{value_date}{currency}{formatted_amount}
:33B:{currency}{formatted_amount}
:50K:{anonymized['anonymized_debtor_name']}
:52A:{p008.get('instg_agent_bic', 'BOSPGBPMXXXX')}
:57A:CBAAU2SXXXX
:59A:CBAAU2SXXXX
:71F:{currency}0,00
:71F:USD0,00
:72:/BEN/99
/R99/MS01/MREF/{transaction_ref}/TEX
/MREF/OL_REFERENCE
/TEXT/IT/{return_reason_info or return_reason}"""

    # Get customer email from CSV validation (will be populated by investigator)
    # Default, will be updated by investigator
    customer_email = "customer@example.com"

    return {
        "subject": "return of funds",
        "reference": transaction_ref,
        "customer_name": anonymized['anonymized_debtor_name'],
        "customer_email": customer_email,
        "body": mt103_body,
        "case_id": case_id,
        "uetr": uetr,
        "amount": amount,
        "currency": currency,
        "return_reason": return_reason,
        "return_reason_info": return_reason_info
    }


def _create_error_response(state: Dict, reason: str) -> Dict:
    """Create standardized error response."""
    error_result = {
        "email_payload": None,
        "error": reason,
        "processing_timestamp": datetime.now().isoformat()
    }
    state["prep_logger"] = error_result
    return append_audit(state, "prep_logger", "error", {"error": reason})
