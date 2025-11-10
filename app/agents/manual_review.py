from typing import Dict, Any
from datetime import datetime, timedelta
from app.utils.audit import append_audit


def run_manual_review(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle cases requiring manual review.

    This agent is called when either:
    1. Pre-flow checklist identifies a terminal condition
    2. FX loss exceeds $300 threshold
    
    Creates a review case and stops refund processing.
    """
    result = dict(state)
    
    # Get review information
    manual_review_required = state.get('manual_review_required', False)
    review_reason = state.get('review_reason', 'Unknown reason')
    checklist_results = state.get('checklist', {})
    fx_results = state.get('fx', {})
    
    # Determine case type and status based on review reason
    is_fx_loss_no_fca = 'FX loss' in review_reason and 'no FCA account found' in review_reason
    case_status = 'PENDING_5_BUSINESS_DAYS' if is_fx_loss_no_fca else 'PENDING_MANUAL_REVIEW'
    
    # Calculate pending date if it's a 5 business days case
    pending_until = None
    if is_fx_loss_no_fca:
        # Calculate 5 business days from now
        current_date = datetime.now()
        business_days_added = 0
        pending_date = current_date
        
        while business_days_added < 5:
            pending_date += timedelta(days=1)
            # Skip weekends (Saturday=5, Sunday=6)
            if pending_date.weekday() < 5:
                business_days_added += 1
        
        pending_until = pending_date.strftime('%Y-%m-%d')
    
    # Create review case details
    review_case = {
        'case_id': f"REVIEW-{state.get('transaction_id', 'UNKNOWN')}-{state.get('run_id', 'UNKNOWN')}",
        'status': case_status,
        'review_reason': review_reason,
        'created_timestamp': state.get('timestamp', ''),
        'transaction_id': state.get('transaction_id', ''),
        'uetr': state.get('uetr', ''),
        'checklist_results': checklist_results,
        'fx_results': fx_results,
        'requires_human_intervention': not is_fx_loss_no_fca,  # No human intervention needed for 5-day pending
        'priority': 'HIGH' if 'FX loss' in review_reason else 'MEDIUM',
        'pending_until': pending_until,
        'case_type': 'FX_LOSS_NO_FCA' if is_fx_loss_no_fca else 'MANUAL_REVIEW'
    }
    
    # Store review case
    result['manual_review_case'] = review_case
    result['processing_status'] = 'PENDING_5_BUSINESS_DAYS' if is_fx_loss_no_fca else 'MANUAL_REVIEW_REQUIRED'
    result['can_process_refund'] = False
    
    # Audit the manual review creation
    audit_details = {
        'case_id': review_case['case_id'],
        'review_reason': review_reason,
        'priority': review_case['priority'],
        'case_type': review_case['case_type'],
        'case_status': case_status,
        'pending_until': pending_until,
        'checklist_failures': [k for k, v in checklist_results.items() if v is True],
        'fx_loss_exceeded': fx_results.get('exceeds_limit', False),
        'fca_account_found': fx_results.get('fca_account_found', False)
    }
    
    return append_audit(
        result,
        "manual_review",
        "case_created",
        audit_details
    )

