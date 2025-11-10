from typing import Dict, List
import uuid
from datetime import datetime
from app.utils.audit import append_audit

REQUIRED_FIELDS = [
    "parsed_pacs004",
    "parsed_pacs008",
    "investigator_csv_validation",
    "investigator_eligibility",
]


def run_log_verifier(state: Dict) -> Dict:
    """
    Log verifier agent that consolidates audit events and saves run report.
    """
    try:
        # Check required fields
        missing = [f for f in REQUIRED_FIELDS if not state.get(f)]
        ok = len(missing) == 0

        # Get repositories
        repos = state.get("repositories", {})
        audit_repo = repos.get("audit")

        if not audit_repo:
            return {**state, "log_verifier": {"ok": False, "missing": ["repositories"]}}

        # Generate run ID
        run_id = str(uuid.uuid4())
        state["run_id"] = run_id

        # Consolidate audit events
        audit_events = _consolidate_audit_events(state)

        # Create comprehensive report
        report_data = _create_run_report(state, audit_events)

        # Save report to csv_reports/
        report_path = audit_repo.save_run_report(run_id, report_data)

        # Add audit events to audit log
        for event in audit_events:
            audit_repo.add_audit_event(event)

        # Update state
        state["log_verifier"] = {
            "ok": ok,
            "missing": missing,
            "run_id": run_id,
            "report_path": report_path,
            "audit_events_count": len(audit_events)
        }

        # Add final audit event
        return append_audit(state, "log_verifier", "completed", {
            "run_id": run_id,
            "report_path": report_path,
            "audit_events_count": len(audit_events)
        })

    except Exception as e:
        error_result = {
            "ok": False,
            "missing": ["error"],
            "error": str(e)
        }
        state["log_verifier"] = error_result
        return append_audit(state, "log_verifier", "error", error_result)


def _consolidate_audit_events(state: Dict) -> List[Dict]:
    """Consolidate all audit events from the processing pipeline."""
    audit_events = []

    # Get transaction ID from PACS.004
    p004 = state.get("parsed_pacs004", {})
    transaction_id = p004.get("e2e", "UNKNOWN")

    # Add investigator events
    if "investigator_eligibility" in state:
        audit_events.append({
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "event_type": "INVESTIGATION",
            "actor": "investigator",
            "action": "eligibility_check",
            "details": {
                "eligibility": state.get("investigator_eligibility", {}),
                "csv_validation": state.get("investigator_csv_validation", {}),
                "cross_errors": state.get("investigator_cross_errors", [])
            },
            "level": "INFO"
        })

    # Add verifier events
    if "verifier_summary" in state:
        audit_events.append({
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "event_type": "VERIFICATION",
            "actor": "verifier",
            "action": "reconciliation_check",
            "details": {
                "verifier_summary": state.get("verifier_summary", {}),
                "nostro_result": state.get("verifier_summary", {}).get("nostro_result", {})
            },
            "level": "INFO"
        })

    # Add refund events
    if "refund_decision" in state:
        audit_events.append({
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "event_type": "REFUND_PROCESSING",
            "actor": "refund",
            "action": "decision_processing",
            "details": {
                "refund_decision": state.get("refund_decision", {}),
                "enhanced_refund_decision": state.get("enhanced_refund_decision", {}),
                "account_operations": state.get("refund_decision", {}).get("account_operations", [])
            },
            "level": "INFO"
        })

    # Add communications events
    if "communication_templates" in state:
        audit_events.append({
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "event_type": "COMMUNICATION",
            "actor": "comms",
            "action": "template_generation",
            "details": {
                "communication_templates": state.get("communication_templates", {})
            },
            "level": "INFO"
        })

    return audit_events


def _create_run_report(state: Dict, audit_events: List[Dict]) -> Dict:
    """Create comprehensive run report with enhanced structure."""
    p004 = state.get("parsed_pacs004", {})
    p008 = state.get("parsed_pacs008", {})

    # Get flow checklist results
    checklist_results = state.get("checklist", {})
    checklist_path = state.get("checklist_decision_path", [])
    manual_review_required = state.get("manual_review_required", False)
    review_reason = state.get("review_reason", "")

    # Get FX results
    fx_results = state.get("fx", {})

    # Get refund decision path
    refund_decision = state.get("refund_decision", {})
    refund_path = refund_decision.get(
        "decision_path", []) if refund_decision else []

    # Get account operations
    account_operations = []
    if refund_decision and refund_decision.get("account_operations"):
        account_operations = refund_decision.get("account_operations", [])
    elif state.get("enhanced_refund_decision", {}).get("account_operations"):
        account_operations = state.get(
            "enhanced_refund_decision", {}).get("account_operations", [])

    # Calculate balance changes summary
    balance_changes_summary = {
        "accounts_affected": len(account_operations),
        "total_debits": sum(float(op.get("amount", 0)) for op in account_operations if op.get("operation_type") == "debit"),
        "total_credits": sum(float(op.get("amount", 0)) for op in account_operations if op.get("operation_type") == "credit"),
        "net_change": 0.0
    }
    balance_changes_summary["net_change"] = balance_changes_summary["total_credits"] - \
        balance_changes_summary["total_debits"]

    return {
        "run_id": state.get("run_id", ""),
        "timestamp": datetime.now().isoformat(),
        "transaction_id": p004.get("e2e", "UNKNOWN"),
        "uetr": p004.get("uetr", ""),
        "summary": {
            "can_process": state.get("refund_decision", {}).get("can_process", False),
            "reason": state.get("refund_decision", {}).get("reason", ""),
            "credit_account_iban": state.get("refund_decision", {}).get("credit_account_iban", ""),
            "decision_path": state.get("refund_decision", {}).get("decision_path", []),
            "d1_d9_decisions": state.get("refund_decision", {}).get("d1_d9_decisions", {}),
            "account_operations_count": len(account_operations)
        },
        "parsed_data": {
            "pacs004": p004,
            "pacs008": p008
        },
        "investigation": {
            "eligibility": state.get("investigator_eligibility", {}),
            "csv_validation": state.get("investigator_csv_validation", {}),
            "cross_errors": state.get("investigator_cross_errors", [])
        },
        "flow_checklist": {
            "checks": checklist_results,
            "decision_path": checklist_path,
            "manual_review_required": manual_review_required,
            "review_reason": review_reason
        },
        "fx_calculation": fx_results,
        "verification": {
            "verifier_summary": state.get("verifier_summary", {}),
            "nostro_result": state.get("verifier_summary", {}).get("nostro_result", {})
        },
        "refund_processing": {
            "refund_decision": refund_decision,
            "enhanced_refund_decision": state.get("enhanced_refund_decision", {}),
            "account_operations": account_operations
        },
        "refund_flow": {
            "decision_path": refund_path,
            "final_decision": refund_decision.get("final_decision", "Not processed") if refund_decision else "Not processed"
        },
        "account_operations": account_operations,
        "balance_changes_summary": balance_changes_summary,
        "manual_review_case": state.get("manual_review_case", {}),
        "processing_status": state.get("processing_status", "Unknown"),
        "communications": {
            "communication_templates": state.get("communication_templates", {})
        },
        "prep_logger": state.get("prep_logger", {}),
        "audit_events": audit_events,
        "metadata": {
            "processing_time": datetime.now().isoformat(),
            "version": "1.0",
            "system": "CBA Refund Processing System"
        }
    }
