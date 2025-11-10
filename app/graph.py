from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.agents.loggerAg import run_prep_logger
from app.agents.investigator import run_investigator
from app.agents.verifier import run_verifier
from app.agents.nostro import run_nostro
from app.agents.refund import run_refund
from app.agents.comms import run_communications
from app.agents.logverifier import run_log_verifier
from app.agents.checklist import run_checklist
from app.agents.fx import run_fx
from app.agents.manual_review import run_manual_review


def should_proceed_to_refund(state: Dict[str, Any]) -> str:
    """Route based on checklist and FX results.

    Returns:
        - "manual_review": If any terminal condition is met or FX loss exceeds limit
        - "nostro": If all checks pass and FX loss is within limit
    """
    # Check if manual review is required from checklist
    if state.get('manual_review_required', False):
        return "manual_review"

    # Check if proceed_to_refund is explicitly set to False
    if state.get('proceed_to_refund') is False:
        return "manual_review"

    # If we reach here, proceed to refund processing
    return "nostro"


def should_refund_after_verifier(state: Dict[str, Any]) -> str:
    """After verification, decide whether to proceed to refund.

    If Nostro match not found, stop processing and go to logging.
    """
    ver = state.get("verifier_summary") or {}
    checks = ver.get("checks") or {}
    if not checks.get("nostro_match_found", False):
        return "log_verifier"
    return "refund"


def verifier_decision(state: Dict[str, Any]) -> str:
    """Verifier step decision logic with three outcomes:
    1. approve_and_process - approve and process the refund
    2. resend_to_investigator - resend to investigator for clarification  
    3. human_intervention - pass for human intervention
    """
    ver = state.get("verifier_summary") or {}
    checks = ver.get("checks") or {}
    reconciliation_ok = ver.get("reconciliation_ok", False)

    # Decision logic based on verification results
    if reconciliation_ok and checks.get("nostro_match_found", False):
        # All checks passed - approve and process refund
        state["verifier_decision"] = "approve_and_process"
        state["verifier_decision_reason"] = "All verification checks passed"
        return "refund"
    elif not checks.get("nostro_match_found", False):
        # Nostro match not found - needs more investigation
        state["verifier_decision"] = "resend_to_investigator"
        state["verifier_decision_reason"] = "Nostro match not found - needs clarification"
        return "investigator"
    else:
        # Other issues - requires human intervention
        state["verifier_decision"] = "human_intervention"
        state["verifier_decision_reason"] = "Verification issues require human review"
        return "log_verifier"


def build_graph():
    graph = StateGraph(Dict[str, Any])

    # Add all nodes
    graph.add_node("prep_logger", run_prep_logger)
    graph.add_node("investigator", run_investigator)
    graph.add_node("fx", run_fx)
    graph.add_node("checklist", run_checklist)
    graph.add_node("manual_review", run_manual_review)
    graph.add_node("nostro", run_nostro)
    graph.add_node("verifier", run_verifier)
    graph.add_node("refund", run_refund)
    graph.add_node("log_verifier", run_log_verifier)
    graph.add_node("communications", run_communications)

    # Set entry point
    graph.set_entry_point("prep_logger")

    # Linear flow: prep_logger → investigator → fx → checklist
    graph.add_edge("prep_logger", "investigator")
    graph.add_edge("investigator", "fx")
    graph.add_edge("fx", "checklist")

    # Conditional routing from checklist
    graph.add_conditional_edges(
        "checklist",
        should_proceed_to_refund,
        {
            "manual_review": "manual_review",
            "nostro": "nostro"
        }
    )

    # Manual review path (ends processing)
    graph.add_edge("manual_review", "log_verifier")

    # Normal refund processing path
    graph.add_edge("nostro", "verifier")
    graph.add_conditional_edges(
        "verifier",
        verifier_decision,
        {
            "refund": "refund",
            "investigator": "investigator",  # Resend to investigator
            "log_verifier": "log_verifier",  # Human intervention
        },
    )
    graph.add_edge("refund", "log_verifier")

    # Final processing
    graph.add_edge("log_verifier", "communications")
    graph.add_edge("communications", END)

    return graph.compile()
