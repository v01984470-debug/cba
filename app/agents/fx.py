from typing import Dict, Any
from app.utils.audit import append_audit
from app.utils.csv_repositories import CSVAccountRepository


def run_fx(state: Dict[str, Any]) -> Dict[str, Any]:
    """Compute FX loss at prevailing rate and check against $300 limit.

    Reads values prepared by investigator: result.investigation.eligibility
    - original_amount_aud
    - returned_amount_aud
    Sets state['fx'] with loss calculation and threshold check
    """
    result = dict(state)
    # Use investigator output directly
    elig = state.get('investigator_eligibility') or {}
    
    # Get amounts from eligibility (already calculated by investigator)
    original_aud = elig.get('original_amount_aud')
    returned_aud = elig.get('returned_amount_aud')
    original_amount = elig.get('original_amount', 0)
    returned_amount = elig.get('returned_amount', 0)
    original_currency = elig.get('original_currency', '')
    returned_currency = elig.get('returned_currency', '')
    
    # Calculate FX loss
    fx_loss_aud = 0.0
    calculation_method = "default"
    
    print(f"DEBUG FX: Starting FX calculation")
    print(f"DEBUG FX: original_aud: {original_aud}")
    print(f"DEBUG FX: returned_aud: {returned_aud}")
    print(f"DEBUG FX: original_amount: {original_amount}")
    print(f"DEBUG FX: returned_amount: {returned_amount}")
    print(f"DEBUG FX: original_currency: {original_currency}")
    print(f"DEBUG FX: returned_currency: {returned_currency}")
    
    try:
        if original_aud is not None and returned_aud is not None:
            # Use AUD amounts if available
            fx_loss_aud = max(0.0, float(original_aud) - float(returned_aud))
            calculation_method = "aud_conversion"
        elif original_amount and returned_amount and original_currency == returned_currency:
            # Same currency, direct comparison
            if original_currency == "AUD":
                fx_loss_aud = max(0.0, float(original_amount) - float(returned_amount))
                calculation_method = "aud_direct"
            else:
                # For non-AUD same currency, assume no FX loss
                fx_loss_aud = 0.0
                calculation_method = "same_currency_non_aud"
        else:
            # Default to 0 if calculation not possible
            fx_loss_aud = 0.0
            calculation_method = "default_zero"
    except Exception as e:
        fx_loss_aud = 0.0
        calculation_method = f"error: {str(e)}"
    
    print(f"DEBUG FX: Calculated fx_loss_aud: {fx_loss_aud}")
    print(f"DEBUG FX: Calculation method: {calculation_method}")
    
    # Check against $300 threshold
    FX_LOSS_THRESHOLD_AUD = 300.0
    loss_exceeds_limit = fx_loss_aud > FX_LOSS_THRESHOLD_AUD
    
    print(f"DEBUG FX: FX_LOSS_THRESHOLD_AUD: {FX_LOSS_THRESHOLD_AUD}")
    print(f"DEBUG FX: loss_exceeds_limit: {loss_exceeds_limit}")
    
    # If FX loss exceeds limit, check for FCA account
    fca_account_found = False
    manual_review_required = False
    review_reason = None
    
    if loss_exceeds_limit:
        print(f"DEBUG FX: FX loss exceeds limit, checking for FCA account...")
        try:
            # Get customer IBAN from parsed data
            pacs004 = state.get('parsed_pacs004', {})
            print(f"DEBUG FX: pacs004 keys: {list(pacs004.keys()) if pacs004 else 'None'}")
            customer_iban = pacs004.get('dbtr_iban') or pacs004.get('cdtr_iban')
            print(f"DEBUG FX: customer_iban: {customer_iban}")
            
            if customer_iban:
                # Check if customer has FCA account
                account_repo = CSVAccountRepository('data')
                
                # Get customer name from the main account
                customer_accounts = account_repo.get_customer_accounts(customer_iban)
                customer_name = None
                if customer_accounts:
                    customer_name = customer_accounts[0].get('Account Name', '')
                
                print(f"DEBUG FX: Customer IBAN: {customer_iban}")
                print(f"DEBUG FX: Customer name: {customer_name}")
                print(f"DEBUG FX: Customer accounts found: {len(customer_accounts)}")
                
                if customer_name:
                    # Look for FCA account with same customer name
                    all_accounts = account_repo.get_all_accounts()
                    print(f"DEBUG FX: Total accounts: {len(all_accounts)}")
                    
                    for account in all_accounts:
                        account_type = account.get('Account Type', '').upper()
                        account_name = account.get('Account Name', '')
                        print(f"DEBUG FX: Checking account: {account_name} (Type: {account_type})")
                        
                        if (account_type == 'FCA' and 
                            account_name.startswith(customer_name.split()[0])):  # Match first name
                            print(f"DEBUG FX: FCA account found: {account_name}")
                            fca_account_found = True
                            break
            
            if fca_account_found:
                # FCA account found - proceed with refund
                manual_review_required = False
                review_reason = f"FX loss ${fx_loss_aud:.2f} exceeds ${FX_LOSS_THRESHOLD_AUD} limit but FCA account found - proceeding with refund"
            else:
                # No FCA account - submit to pending for 5 business days
                manual_review_required = True
                review_reason = f"FX loss ${fx_loss_aud:.2f} exceeds ${FX_LOSS_THRESHOLD_AUD} limit and no FCA account found - submitting to pending for 5 business days"
                
        except Exception as e:
            # If error checking FCA, default to manual review
            print(f"DEBUG FX: Exception in FCA lookup: {str(e)}")
            import traceback
            traceback.print_exc()
            manual_review_required = True
            review_reason = f"FX loss ${fx_loss_aud:.2f} exceeds ${FX_LOSS_THRESHOLD_AUD} limit - error checking FCA account: {str(e)}"
    
    # Store FX results
    result['fx'] = {
        'loss_aud': round(fx_loss_aud, 2),
        'original_amount_aud': original_aud,
        'returned_amount_aud': returned_aud,
        'original_amount': original_amount,
        'returned_amount': returned_amount,
        'original_currency': original_currency,
        'returned_currency': returned_currency,
        'calculation_method': calculation_method,
        'threshold_aud': FX_LOSS_THRESHOLD_AUD,
        'exceeds_limit': loss_exceeds_limit,
        'fca_account_found': fca_account_found
    }
    
    # Update manual review flags if FX loss exceeds limit
    if manual_review_required:
        result['manual_review_required'] = True
        result['review_reason'] = review_reason
        result['proceed_to_refund'] = False
    else:
        # Only set proceed_to_refund if not already set by checklist
        if 'proceed_to_refund' not in result:
            result['proceed_to_refund'] = True
    
    # Audit the FX calculation
    audit_details = {
        'fx_loss_aud': fx_loss_aud,
        'exceeds_limit': loss_exceeds_limit,
        'calculation_method': calculation_method,
        'original_amount_aud': original_aud,
        'returned_amount_aud': returned_aud,
        'fca_account_found': fca_account_found,
        'manual_review_required': manual_review_required,
        'review_reason': review_reason
    }
    
    return append_audit(
        result,
        "fx",
        "manual_review" if manual_review_required else "passed",
        audit_details
    )


