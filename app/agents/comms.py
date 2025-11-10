from typing import Dict, Optional
from app.utils.audit import append_audit
from app.utils.gemini_email import generate_customer_email


def run_communications(state: Dict) -> Dict:
    """
    Communications agent that generates customer and branch notification templates.
    """
    try:
        verifier = state.get("verifier_summary", {})
        refund = state.get("refund_decision", {})
        elig = state.get("investigator_eligibility", {})
        p004 = state.get("parsed_pacs004", {})
        p008 = state.get("parsed_pacs008", {})
        csv_validation = state.get("investigator_csv_validation", {})

        # Generate communication templates
        templates = _generate_communication_templates(
            verifier, refund, elig, p004, p008
        )

        # Create detailed communication data for report.html
        communication_data = {
            "templates": templates,
            "customer_notification": _create_customer_notification(refund, p004, p008, elig, csv_validation),
            "branch_advisory": _create_branch_advisory(verifier, refund, elig),
            "ops_advisory": _create_ops_advisory(verifier, refund, elig),
            "decision_summary": _create_decision_summary(refund, elig),
            "decision_path": refund.get("decision_path", []),
            "nostro_reference": (verifier.get("nostro_result", {}) or {}).get("nostro_entry", {}),
        }

        state["communication_templates"] = communication_data

        print(
            f"DEBUG: Communication templates saved - customer_notification keys: {list(communication_data.get('customer_notification', {}).keys())}")
        print(
            f"DEBUG: Customer notification has html_body: {bool(communication_data.get('customer_notification', {}).get('html_body'))}")
        print(
            f"DEBUG: Customer notification generated_by: {communication_data.get('customer_notification', {}).get('generated_by', 'N/A')}")

        return append_audit(state, "communications", "prepared", {
            "templates_count": len(templates),
            "communication_data": communication_data
        })

    except Exception as e:
        error_result = {
            "templates": [f"Communication error: {str(e)}"],
            "error": str(e)
        }
        state["communication_templates"] = error_result
        return append_audit(state, "communications", "error", error_result)


def _generate_communication_templates(verifier: Dict, refund: Dict, elig: Dict, p004: Dict, p008: Dict) -> list:
    """Generate communication templates based on processing results."""
    templates = []

    # Check reconciliation status
    if not verifier.get("reconciliation_ok"):
        failed_checks = []
        checks = (verifier.get("checks") or {})
        labelmap = {
            'sequence_ok': 'Sequence Check',
            'cross_checks_ok': 'Cross-Message Validation',
            'csv_validation_ok': 'Customer Validation',
            'non_branch_ok': 'Channel Type',
            'sanctions_ok': 'Sanctions',
            'fx_loss_within_limit': 'FX Loss Limit',
            'nostro_match_found': 'Nostro Reconciliation',
            'process_flow_ok': 'Process Compliance'
        }
        for k, v in checks.items():
            if not v:
                failed_checks.append(labelmap.get(k, k))

        # Add specific process-flow failures
        for c in (verifier.get("process_flow_checks") or []):
            if not c.get("ok"):
                failed_checks.append(c.get("label"))

        if failed_checks:
            templates.append(
                "Ops advisory: reconciliation failed: " + "; ".join(failed_checks))
        else:
            templates.append("Ops advisory: reconciliation failed; see logs.")

    # Generate refund-specific templates
    if refund.get("can_process"):
        account_ops = refund.get("account_operations", [])
        if account_ops:
            # Show account operations in template
            ops_summary = []
            for op in account_ops:
                ops_summary.append(
                    f"{op.get('operation_type', '').upper()} {op.get('amount', 0)} {op.get('currency', '')} to/from {op.get('account_name', '')}")

            templates.append(
                f"Customer/Branch: Refund processed successfully. Operations: {'; '.join(ops_summary)}. Reference: {p004.get('e2e', '')}")
        else:
            path = ">".join(refund.get("decision_path", [])) or "D1-D9 path"
            templates.append(
                f"Customer/Branch: Refund processed successfully (path: {path}). Reference: {p004.get('e2e', '')}")
    else:
        # Generate failure-specific templates
        reason = elig.get("reason", "")
        if reason == "AC04":
            templates.append(
                "Customer: Account closed. Please provide an alternate active account for refund.")
        elif reason == "AC01":
            templates.append(
                "Customer: Incorrect account number. Please provide the correct account details for refund.")
        elif not verifier.get("reconciliation_ok"):
            templates.append(
                "Customer/Branch: Refund pending due to failed verification/compliance checks.")
        else:
            templates.append(
                "Customer/Branch: Refund pending eligibility (FX/channel/sanctions) or validation.")

    return templates


def _create_customer_notification(refund: Dict, p004: Dict, p008: Dict, elig: Optional[Dict] = None, csv_validation: Optional[Dict] = None) -> Dict:
    """Create customer notification details using Gemini API for email generation."""
    # Get customer data from CSV validation if available (preferred source)
    customer_record = None
    if csv_validation and csv_validation.get("customer"):
        customer_record = csv_validation["customer"]
        # Handle both dict and object types
        if hasattr(customer_record, "__dict__"):
            customer_record = customer_record.__dict__
        elif not isinstance(customer_record, dict):
            customer_record = None

    # Extract recipient information (prioritize CSV validation data)
    recipient_name = (
        customer_record.get("account_holder_name") if customer_record else None
    ) or p008.get("dbtr_name", "Customer")

    recipient_email = (
        customer_record.get("email") if customer_record else None
    ) or p008.get("dbtr_email", "")

    print(
        f"DEBUG: Generating email for recipient: {recipient_name} ({recipient_email})")

    # Extract transaction data
    uetr = p004.get("uetr", p004.get("e2e", "N/A"))
    return_amount = str(p004.get("rtr_amount", ""))
    return_currency = p004.get("rtr_ccy", "")
    reason_code = p004.get("rsn", "")
    reason_info = p004.get("rsn_info", "")

    # Get FX loss from eligibility if available
    fx_loss_aud = None
    if elig:
        fx_loss_aud = elig.get("fx_loss_aud")

    status = "Refund Processed" if refund.get(
        "can_process") else "Refund Pending"

    # Determine action required message
    action_required = _determine_action_required(refund, p004, elig)

    # Generate email using Gemini API
    try:
        print(f"DEBUG: Calling generate_customer_email for UETR {uetr}")
        email_data = generate_customer_email(
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            uetr=uetr,
            return_amount=return_amount,
            return_currency=return_currency,
            reason_code=reason_code,
            reason_info=reason_info,
            fx_loss_aud=fx_loss_aud,
            status=status,
            action_required=action_required,
            variation_mode=False
        )

        print(
            f"DEBUG: Email generation result - subject: {email_data.get('subject', 'N/A')[:50]}, has_html_body: {bool(email_data.get('html_body'))}, html_body_length: {len(email_data.get('html_body', ''))}, has_body: {bool(email_data.get('body'))}, body_length: {len(email_data.get('body', ''))}, generated_by: {email_data.get('generated_by', 'N/A')}")

        # Ensure we have the required fields
        if not email_data.get("html_body") and not email_data.get("body"):
            print(
                f"ERROR: Gemini email generation returned empty content for UETR {uetr}")
        elif not email_data.get("html_body") or not email_data.get("html_body").strip():
            print(
                f"WARNING: Gemini email generation returned empty html_body for UETR {uetr}, but has body text")
            # If we have body but no html_body, convert body to HTML
            if email_data.get("body"):
                from app.utils.gemini_email import _convert_to_html
                email_data["html_body"] = _convert_to_html(
                    email_data["body"], recipient_name, recipient_email, uetr)
                print(
                    f"DEBUG: Converted body to HTML, html_body length: {len(email_data.get('html_body', ''))}")
    except Exception as e:
        print(f"Error generating email with Gemini API: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to template-based email structure
        email_data = {
            "subject": f"Refund Processing Update - {p004.get('e2e', uetr)}",
            "body": "",
            "html_body": "",
            "generated_by": "template"
        }

    result = {
        "recipient": recipient_name,
        "email": recipient_email,
        "subject": email_data.get("subject", f"Refund Processing Update - {p004.get('e2e', '')}"),
        "body": email_data.get("body", ""),
        "html_body": email_data.get("html_body", ""),
        "status": "processed" if refund.get("can_process") else "pending",
        "amount": return_amount,
        "currency": return_currency,
        "reference": p004.get("e2e", ""),
        "uetr": uetr,
        "account_operations": refund.get("account_operations", []),
        "generated_by": email_data.get("generated_by", "template")
    }

    # Final validation - ensure html_body is not empty
    if not result.get("html_body") or not result["html_body"].strip():
        print(f"ERROR: Final result has empty html_body! This should not happen.")
        if result.get("body"):
            # Last resort: create basic HTML from body
            import html as html_escape
            result["html_body"] = f"<p>{html_escape.escape(result['body']).replace(chr(10), '<br>')}</p>"
            print(
                f"DEBUG: Created fallback HTML from body, length: {len(result['html_body'])}")

    print(
        f"DEBUG: Customer notification created - subject: {result['subject'][:50]}, html_body length: {len(result.get('html_body', ''))}, generated_by: {result['generated_by']}")

    return result


def _determine_action_required(refund: Dict, p004: Dict, elig: Optional[Dict]) -> str:
    """Determine the action required message based on refund status and reason."""
    if refund.get("can_process"):
        return "No action required. Your refund has been processed successfully."

    reason_code = p004.get("rsn", "")

    if reason_code == "AC01":
        return "Our systems indicate the account number provided is incorrect. To proceed with the refund, please provide the correct account details."
    elif reason_code == "AC04":
        return "Our systems indicate the original IBAN is no longer valid. To proceed with the refund, please provide an alternate active account number."
    elif reason_code == "CURR":
        return "This case requires manual review due to currency mismatch."
    elif elig and not elig.get("fx_loss_within_limit", True):
        return "This case requires manual review due to FX loss exceeding the threshold."
    else:
        return "We are reviewing your case and will update you shortly."


def _create_branch_advisory(verifier: Dict, refund: Dict, elig: Dict) -> Dict:
    """Create branch advisory details."""
    return {
        "recipient": "Branch Operations",
        "subject": "Refund Processing Advisory",
        "status": "processed" if refund.get("can_process") else "requires_attention",
        "reconciliation_status": verifier.get("reconciliation_ok", False),
        "nostro_match": verifier.get("nostro_result", {}).get("found", False),
        "match_type": verifier.get("nostro_result", {}).get("match_type", "none"),
        "eligibility_status": elig.get("eligible_auto_refund", False),
        "decision_path": refund.get("decision_path", [])
    }


def _create_ops_advisory(verifier: Dict, refund: Dict, elig: Dict) -> Dict:
    """Create operations advisory details."""
    return {
        "recipient": "Operations Team",
        "subject": "Refund Processing Operations Advisory",
        "priority": "high" if not refund.get("can_process") else "normal",
        "reconciliation_issues": not verifier.get("reconciliation_ok", True),
        "failed_checks": [k for k, v in verifier.get("checks", {}).items() if not v],
        "nostro_reconciliation": verifier.get("nostro_result", {}),
        "account_operations": refund.get("account_operations", []),
        "requires_manual_intervention": not refund.get("can_process", False)
    }


def _create_decision_summary(refund: Dict, elig: Dict) -> Dict:
    """Create decision summary for reporting."""
    return {
        "final_decision": "processed" if refund.get("can_process") else "failed",
        "decision_path": refund.get("decision_path", []),
        "reason": refund.get("reason", ""),
        "credit_account": refund.get("credit_account_iban", ""),
        "account_operations_count": len(refund.get("account_operations", [])),
        "eligibility_summary": {
            "auto_refund_eligible": elig.get("eligible_auto_refund", False),
            "fx_loss_aud": elig.get("fx_loss_aud", 0),
            "fx_within_limit": elig.get("fx_loss_within_limit", False),
            "is_aud_refund": elig.get("is_aud_refund", False)
        }
    }
