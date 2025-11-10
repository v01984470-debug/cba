"""
Refund agent implementing the D1-D9 decision flow from refund_flow_.md.
"""

from typing import Dict, List, Any
from app.utils.audit import append_audit
from app.utils.refund_decision_engine import RefundDecisionEngine
from app.utils.debit_authority import check_debit_authority


def _calculate_d1_d9_decisions(decision_path: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Calculate D1-D9 decisions based on decision path statements.
    Returns a dictionary with decision results and matching statements.
    """
    decisions = {}
    
    # D1: Foreign Currency
    d1_match = []
    d1_decision = 'No'
    for step in decision_path:
        if 'currency' in step.lower() and 'foreign' in step.lower():
            d1_match.append(step)
            if 'is foreign' in step.lower():
                d1_decision = 'Yes'
    decisions['D1'] = {
        'decision': d1_decision,
        'statement': d1_match[0] if d1_match else 'Not processed'
    }
    
    # D2: Nostro Found
    d2_match = []
    d2_decision = 'No'
    for step in decision_path:
        if 'nostro' in step.lower():
            d2_match.append(step)
            if 'item found' in step.lower():
                d2_decision = 'Yes'
    decisions['D2'] = {
        'decision': d2_decision,
        'statement': d2_match[0] if d2_match else 'Not processed'
    }
    
    # D3: FCA Refund
    d3_match = []
    d3_decision = 'No'
    for step in decision_path:
        if 'fca' in step.lower():
            d3_match.append(step)
            if 'not required' in step.lower():
                d3_decision = 'No'
            elif 'required' in step.lower():
                d3_decision = 'Yes'
    decisions['D3'] = {
        'decision': d3_decision,
        'statement': d3_match[0] if d3_match else 'Not processed'
    }
    
    # D4: MT103/202 (Client Payment)
    d4_match = []
    d4_decision = 'No'
    for step in decision_path:
        if 'payment' in step.lower() and 'client' in step.lower():
            d4_match.append(step)
            if 'is client payment' in step.lower():
                d4_decision = 'Yes'
    decisions['D4'] = {
        'decision': d4_decision,
        'statement': d4_match[0] if d4_match else 'Not processed'
    }
    
    # D5: Amendment (N/A - not in decision path)
    decisions['D5'] = {
        'decision': 'N/A',
        'statement': 'Not processed'
    }
    
    # D6: No Charges (N/A - not in decision path)
    decisions['D6'] = {
        'decision': 'N/A',
        'statement': 'Not processed'
    }
    
    # D7: Branch (N/A - not in decision path)
    decisions['D7'] = {
        'decision': 'N/A',
        'statement': 'Not processed'
    }
    
    # D8: Markets
    d8_match = []
    d8_decision = 'No'
    for step in decision_path:
        if 'markets' in step.lower():
            d8_match.append(step)
            if 'default: no' in step.lower():
                d8_decision = 'No'
            elif 'default: yes' in step.lower():
                d8_decision = 'Yes'
    decisions['D8'] = {
        'decision': d8_decision,
        'statement': d8_match[0] if d8_match else 'Not processed'
    }
    
    # D9: Email
    d9_match = []
    d9_decision = 'No'
    for step in decision_path:
        if 'email' in step.lower():
            d9_match.append(step)
            if 'has valid email' in step.lower():
                d9_decision = 'Yes'
    decisions['D9'] = {
        'decision': d9_decision,
        'statement': d9_match[0] if d9_match else 'Not processed'
    }
    
    return decisions


def run_refund(state: Dict) -> Dict:
    """
    Main refund processing function implementing D1-D9 decision flow.
    """
    try:
        # Get repositories and parsed data
        repos = state.get("repositories", {})
        p004 = state.get("parsed_pacs004", {})
        p008 = state.get("parsed_pacs008", {})
        verifier_summary = state.get("verifier_summary", {})
        nostro_result = verifier_summary.get("nostro_result", {})

        if not repos:
            return _create_error_response(state, "No repositories available")

        if not p004 or not p008:
            return _create_error_response(state, "Missing PACS messages")

        # Initialize decision engine with data directory
        decision_engine = RefundDecisionEngine("data")

        # Execute D1-D9 decision flow
        decision_result = decision_engine.process_refund(
            p004, p008, "data/customer_data.csv")

        # Extract credit account IBAN from account operations
        credit_iban = ""
        if decision_result.account_operations:
            for op in decision_result.account_operations:
                if op.get("operation_type") == "credit":
                    credit_iban = op.get("account_number", "")
                    break

        # Pre-calculate D1-D9 decisions
        decision_path = [result.reason for result in decision_result.decision_path]
        d1_d9_decisions = _calculate_d1_d9_decisions(decision_path)

        # Store results in state
        state["refund_decision"] = {
            "can_process": decision_result.success,
            "reason": decision_result.final_action,
            "credit_account_iban": credit_iban,
            "decision_path": decision_path,
            "account_operations": decision_result.account_operations,
            "d1_d9_decisions": d1_d9_decisions,
        }

        state["enhanced_refund_decision"] = {
            "can_process": decision_result.success,
            "reason": decision_result.final_action,
            "credit_account_iban": credit_iban,
            "decision_path": decision_path,
            "account_operations": decision_result.account_operations,
            "d1_d9_decisions": d1_d9_decisions,
            "processing_details": {
                "nostro_result": nostro_result,
                "decision_engine_result": decision_result,
            },
        }

        # Audit the decision
        audit_details = {
            "decision_path": [result.reason for result in decision_result.decision_path],
            "can_process": decision_result.success,
            "reason": decision_result.final_action,
            "account_operations_count": len(decision_result.account_operations or []),
        }

        return append_audit(
            state,
            "refund",
            "processed" if decision_result.success else "failed",
            audit_details,
        )

    except Exception as e:
        error_result = {
            "can_process": False,
            "reason": f"Processing error: {str(e)}",
            "error_details": str(e),
        }
        state["refund_decision"] = error_result
        state["enhanced_refund_decision"] = error_result
        return append_audit(state, "refund", "error", error_result)


def _create_error_response(state: Dict, reason: str) -> Dict:
    """Create standardized error response."""
    error_result = {
        "can_process": False,
        "reason": reason,
        "credit_account_iban": None,
        "decision_path": [],
        "account_operations": [],
    }
    state["refund_decision"] = error_result
    state["enhanced_refund_decision"] = error_result
    return append_audit(state, "refund", "error", error_result)
