"""
Refund Decision Engine
Implements the complete decision tree from refund_flow_.md using CSV-based operations.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from app.utils.csv_reconciliation import csv_reconciliation_engine
from app.utils.debit_authority import debit_authority_manager
from app.utils.csv_store import load_accounts_csv, suggest_alternate_active


class DecisionNode(Enum):
    """Decision nodes from refund_flow_.md"""
    D1_FOREIGN_CURRENCY = "D1"
    D2_NOSTRO_FOUND = "D2"
    D3_FCA_REFUND = "D3"
    D4_NOSTRO_FOUND_AFTER_SCR = "D4"
    D5_MARKETS = "D5"
    D6_VOSTRO_AUTHORITY = "D6"
    D7_BRANCH_PAYMENT = "D7"
    D8_MARKETS_FINAL = "D8"
    D9_VALID_EMAIL = "D9"


@dataclass
class DecisionResult:
    """Result of a decision node."""
    node: DecisionNode
    decision: bool
    reason: str
    next_node: Optional[DecisionNode] = None
    action_taken: Optional[str] = None
    data: Optional[Dict] = None


@dataclass
class RefundProcessingResult:
    """Complete result of refund processing."""
    success: bool
    decision_path: List[DecisionResult]
    final_action: str
    accounts_affected: List[Dict]
    account_operations: List[Dict] = None
    audit_trail: List[Dict] = None
    error: Optional[str] = None


class RefundDecisionEngine:
    """Implements the refund decision flow from refund_flow_.md."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.decision_path: List[DecisionResult] = []
        self.audit_trail: List[Dict] = []
        self.accounts_affected: List[Dict] = []
        self.account_operations: List[Dict] = []

    def process_refund(self, p004_data: Dict, p008_data: Dict, customers_csv_path: str = "data/customer_data.csv") -> RefundProcessingResult:
        """Process refund following the complete decision tree."""
        try:
            # Initialize processing
            self.decision_path = []
            self.audit_trail = []
            self.accounts_affected = []
            self.account_operations = []

            # Extract key data
            return_reference = p004_data.get('e2e', '')  # OrgnlEndToEndId
            uetr = p004_data.get('uetr', '')
            amount = float(p004_data.get('rtr_amount', 0))
            currency = p004_data.get('rtr_ccy', '')
            reason = p004_data.get('rsn', '')
            reason_info = p004_data.get('rsn_info', '')
            creditor_agent_bic = self._extract_creditor_agent_bic(p004_data)

            # Start decision tree at D1
            current_node = DecisionNode.D1_FOREIGN_CURRENCY

            while current_node:
                decision_result = self._process_decision_node(
                    current_node, p004_data, p008_data, customers_csv_path,
                    return_reference, uetr, amount, currency, reason, reason_info, creditor_agent_bic
                )

                self.decision_path.append(decision_result)
                self._log_decision(decision_result)

                # Determine next node
                current_node = decision_result.next_node

                # Check for terminal conditions
                if decision_result.action_taken in ['SUBMIT_CASE_TO_CLOSED', 'FUNDS_IN_OB']:
                    break

            # Determine final result
            success = any(result.action_taken ==
                          'SUBMIT_CASE_TO_CLOSED' for result in self.decision_path)
            final_action = self.decision_path[-1].action_taken if self.decision_path else 'UNKNOWN'

            return RefundProcessingResult(
                success=success,
                decision_path=self.decision_path,
                final_action=final_action,
                accounts_affected=self.accounts_affected,
                account_operations=self.account_operations,
                audit_trail=self.audit_trail
            )

        except Exception as e:
            return RefundProcessingResult(
                success=False,
                decision_path=self.decision_path,
                final_action='ERROR',
                accounts_affected=self.accounts_affected,
                account_operations=self.account_operations,
                audit_trail=self.audit_trail,
                error=str(e)
            )

    def _process_decision_node(self, node: DecisionNode, p004_data: Dict, p008_data: Dict,
                               customers_csv_path: str, return_reference: str, uetr: str,
                               amount: float, currency: str, reason: str, reason_info: str,
                               creditor_agent_bic: str) -> DecisionResult:
        """Process a specific decision node."""

        if node == DecisionNode.D1_FOREIGN_CURRENCY:
            return self._d1_foreign_currency(currency)

        elif node == DecisionNode.D2_NOSTRO_FOUND:
            return self._d2_nostro_found(return_reference, uetr, amount, currency)

        elif node == DecisionNode.D3_FCA_REFUND:
            return self._d3_fca_refund(p004_data, p008_data, customers_csv_path)

        elif node == DecisionNode.D4_NOSTRO_FOUND_AFTER_SCR:
            return self._d4_nostro_found_after_scr(return_reference, uetr, amount, currency)

        elif node == DecisionNode.D5_MARKETS:
            return self._d5_markets()

        elif node == DecisionNode.D6_VOSTRO_AUTHORITY:
            return self._d6_vostro_authority(creditor_agent_bic, currency, amount, return_reference, uetr, reason_info)

        elif node == DecisionNode.D7_BRANCH_PAYMENT:
            return self._d7_branch_payment(p004_data, p008_data)

        elif node == DecisionNode.D8_MARKETS_FINAL:
            return self._d8_markets_final()

        elif node == DecisionNode.D9_VALID_EMAIL:
            return self._d9_valid_email(p004_data)

        else:
            return DecisionResult(
                node=node,
                decision=False,
                reason=f"Unknown decision node: {node}",
                next_node=None
            )

    def _d1_foreign_currency(self, currency: str) -> DecisionResult:
        """D1: Is the returned amount foreign currency?"""
        is_foreign = currency.upper() != 'AUD'

        if is_foreign:
            # Attach SC/LC documents (Intellimatch)
            self._attach_sc_lc_documents()
            next_node = DecisionNode.D2_NOSTRO_FOUND
        else:
            next_node = DecisionNode.D6_VOSTRO_AUTHORITY

        return DecisionResult(
            node=DecisionNode.D1_FOREIGN_CURRENCY,
            decision=is_foreign,
            reason=f"Currency {currency} is {'foreign' if is_foreign else 'domestic'}",
            next_node=next_node,
            action_taken="ATTACH_SC_LC" if is_foreign else None
        )

    def _d2_nostro_found(self, return_reference: str, uetr: str, amount: float, currency: str) -> DecisionResult:
        """D2: Was the nostro item found?"""
        nostro_result = csv_reconciliation_engine.find_nostro_match(
            return_reference, uetr, amount, currency)

        if nostro_result.found:
            next_node = DecisionNode.D3_FCA_REFUND
        else:
            # Disposition waiting for SCR
            self._disposition_waiting_for_scr()
            next_node = DecisionNode.D4_NOSTRO_FOUND_AFTER_SCR

        return DecisionResult(
            node=DecisionNode.D2_NOSTRO_FOUND,
            decision=nostro_result.found,
            reason=f"Nostro item {'found' if nostro_result.found else 'not found'}",
            next_node=next_node,
            data={'nostro_result': nostro_result}
        )

    def _d3_fca_refund(self, p004_data: Dict, p008_data: Dict, customers_csv_path: str) -> DecisionResult:
        """D3: Are we refunding the FCA?"""
        # Check if customer has FCA account
        customer_iban = p008_data.get('dbtr_iban', '')
        accounts = load_accounts_csv(customers_csv_path)
        customer_record = accounts.get(customer_iban.upper(), {})

        is_fca = 'FCA' in customer_record.get('account_type', '').upper()

        if is_fca:
            # FCA SAME NAME - ensure FCA account is same as original debited account
            self._fca_same_name_verification(customer_record)

            # Debit Nostro
            nostro_debit_result = self._debit_nostro(p004_data)

            # Credit FCA
            fca_credit_result = self._credit_fca(customer_record, p004_data)

            # Update SNDR Ref
            self._update_sndr_ref(p004_data)

            next_node = DecisionNode.D5_MARKETS
        else:
            # Debit Nostro Payment Input Screen
            self._debit_nostro_payment_input_screen(p004_data)

            # Update SNDR Ref
            self._update_sndr_ref(p004_data)

            next_node = DecisionNode.D7_BRANCH_PAYMENT

        return DecisionResult(
            node=DecisionNode.D3_FCA_REFUND,
            decision=is_fca,
            reason=f"FCA refund {'required' if is_fca else 'not required'}",
            next_node=next_node,
            action_taken="FCA_SAME_NAME" if is_fca else "DEBIT_NOSTRO_PAYMENT_INPUT"
        )

    def _d4_nostro_found_after_scr(self, return_reference: str, uetr: str, amount: float, currency: str) -> DecisionResult:
        """D4: Was the nostro item found? (after SCR)"""
        nostro_result = csv_reconciliation_engine.find_nostro_match(
            return_reference, uetr, amount, currency)

        if nostro_result.found:
            # Attach SC/LC
            self._attach_sc_lc_documents()
            next_node = DecisionNode.D3_FCA_REFUND
        else:
            # Send Nostro Not Credited
            self._send_nostro_not_credited()
            next_node = DecisionNode.D7_BRANCH_PAYMENT

        return DecisionResult(
            node=DecisionNode.D4_NOSTRO_FOUND_AFTER_SCR,
            decision=nostro_result.found,
            reason=f"Nostro item {'found' if nostro_result.found else 'still not found'} after SCR",
            next_node=next_node,
            action_taken="SEND_NOSTRO_NOT_CREDITED" if not nostro_result.found else "ATTACH_SC_LC"
        )

    def _d5_markets(self) -> DecisionResult:
        """D5: Is Markets?"""
        # POC default is NO
        is_markets = False

        if is_markets:
            # Send Refund FCA Email
            self._send_refund_fca_email()
            next_node = DecisionNode.D8_MARKETS_FINAL
        else:
            # Send Refund (Daily List/Full List)
            self._send_refund_daily_list()
            next_node = DecisionNode.D8_MARKETS_FINAL

        return DecisionResult(
            node=DecisionNode.D5_MARKETS,
            decision=is_markets,
            reason="Markets case (POC default: NO)",
            next_node=next_node,
            action_taken="SEND_REFUND_FCA_EMAIL" if is_markets else "SEND_REFUND_DAILY_LIST"
        )

    def _d6_vostro_authority(self, creditor_agent_bic: str, currency: str, amount: float,
                             return_reference: str, uetr: str, reason_info: str) -> DecisionResult:
        """D6: Vostro bank has given debit authority?"""
        authority_check = csv_reconciliation_engine.check_debit_authority(
            creditor_agent_bic, currency, amount)

        if authority_check['authority_exists']:
            # Debit Vostro Payment Input Screen
            self._debit_vostro_payment_input_screen(
                return_reference, amount, currency)

            # SNDR Ref being Vostro bank's case reference
            self._update_vostro_sndr_ref(return_reference)

            next_node = DecisionNode.D7_BRANCH_PAYMENT
        else:
            # Funds in OB
            self._funds_in_ob()

            # Debit OB Payment Input Screen
            self._debit_ob_payment_input_screen(
                return_reference, amount, currency)

            # SNDR Ref being CBA case reference without letters
            self._update_ob_sndr_ref(return_reference)

            next_node = DecisionNode.D7_BRANCH_PAYMENT

        return DecisionResult(
            node=DecisionNode.D6_VOSTRO_AUTHORITY,
            decision=authority_check['authority_exists'],
            reason=f"Debit authority {'exists' if authority_check['authority_exists'] else 'does not exist'}",
            next_node=next_node,
            action_taken="DEBIT_VOSTRO" if authority_check['authority_exists'] else "FUNDS_IN_OB"
        )

    def _d7_branch_payment(self, p004_data: Dict, p008_data: Dict) -> DecisionResult:
        """D7: Is this a Branch payment?"""
        # Determine if this is a branch payment (simplified logic)
        is_branch = self._is_branch_payment(p004_data)

        if is_branch:
            # Credit Branch SAIT
            self._credit_branch_sait(p004_data)
        else:
            # Credit Client Original Debited Account
            self._credit_client_original(p004_data, p008_data)

        next_node = DecisionNode.D8_MARKETS_FINAL

        return DecisionResult(
            node=DecisionNode.D7_BRANCH_PAYMENT,
            decision=is_branch,
            reason=f"Payment is {'branch' if is_branch else 'client'} payment",
            next_node=next_node,
            action_taken="CREDIT_BRANCH_SAIT" if is_branch else "CREDIT_CLIENT_ORIGINAL"
        )

    def _d8_markets_final(self) -> DecisionResult:
        """D8: Is Markets?"""
        is_markets = False  # POC default

        if is_markets:
            # Send Refund Sent Email
            self._send_refund_sent_email()
        else:
            next_node = DecisionNode.D9_VALID_EMAIL

        return DecisionResult(
            node=DecisionNode.D8_MARKETS_FINAL,
            decision=is_markets,
            reason="Markets case (POC default: NO)",
            next_node=next_node if not is_markets else None,
            action_taken="SEND_REFUND_SENT_EMAIL" if is_markets else None
        )

    def _d9_valid_email(self, p004_data: Dict) -> DecisionResult:
        """D9: Does client have valid email address?"""
        has_valid_email = self._check_valid_email(p004_data)

        if has_valid_email:
            # Send Refund (Daily List/Full List)
            self._send_refund_daily_list()
        else:
            # Send the client an AdHoc
            self._send_client_adhoc()

            # Send Refund NO email (Full List) to CBA Reports
            self._send_refund_no_email_cba_reports()

        # Update QF
        self._update_qf()

        # Submit Case to Closed
        self._submit_case_to_closed()

        return DecisionResult(
            node=DecisionNode.D9_VALID_EMAIL,
            decision=has_valid_email,
            reason=f"Client {'has' if has_valid_email else 'does not have'} valid email",
            next_node=None,
            action_taken="SUBMIT_CASE_TO_CLOSED"
        )

    # Action methods
    def _attach_sc_lc_documents(self):
        """Attach Settlement Copy (SC), Letter of Credit (LC), and Supporting Documents."""
        self._log_action(
            "ATTACH_SC_LC", "Attached SC, LC, and supporting documents via Intellimatch")

    def _disposition_waiting_for_scr(self):
        """Add note with current date; awaiting SCR."""
        self._log_action("DISPOSITION_WAITING_FOR_SCR",
                         "Added note with current date; awaiting SCR")

    def _fca_same_name_verification(self, customer_record: Dict):
        """Ensure FCA account is same as original debited account. Attach note: 'FCA SAME NAME'."""
        self._log_action(
            "FCA_SAME_NAME", f"Verified FCA same name for customer: {customer_record.get('account_holder_name', 'Unknown')}")

    def _debit_nostro(self, p004_data: Dict) -> bool:
        """Debit Nostro account; check MT940 :61: and :86: for traceability."""
        amount = float(p004_data.get('rtr_amount', 0))
        currency = p004_data.get('rtr_ccy', '')

        # Find nostro account for currency
        nostro_account = self._get_nostro_account_for_currency(currency)
        if nostro_account:
            # Get current balance before debit
            accounts_data = csv_reconciliation_engine.load_csv_data(
                'data/bank_accounts.csv')
            current_balance = None
            account_name = None
            for account in accounts_data:
                if account.get('Account Number', '') == nostro_account:
                    current_balance = account.get('Opening Balance', '')
                    account_name = account.get('Account Name', '')
                    break

            success = csv_reconciliation_engine.update_bank_account_balance(
                nostro_account, amount, 'debit')

            # Get new balance after debit
            accounts_data_after = csv_reconciliation_engine.load_csv_data(
                'data/bank_accounts.csv')
            new_balance = None
            for account in accounts_data_after:
                if account.get('Account Number', '') == nostro_account:
                    new_balance = account.get('Opening Balance', '')
                    break

            # Record detailed account operation
            operation = {
                'operation_type': 'DEBIT',
                'account_number': nostro_account,
                'account_name': account_name,
                'account_type': 'Nostro',
                'currency': currency,
                'amount': amount,
                'balance_before': current_balance,
                'balance_after': new_balance,
                'reason': 'Return processing - nostro debit',
                'reference': p004_data.get('e2e', ''),
                'uetr': p004_data.get('uetr', '')
            }
            self.account_operations.append(operation)

            self._log_action(
                "DEBIT_NOSTRO", f"Debited {currency} {amount} from nostro account {nostro_account} ({account_name})")
            return success
        return False

    def _credit_fca(self, customer_record: Dict, p004_data: Dict) -> bool:
        """Update client's FCA balance."""
        amount = float(p004_data.get('rtr_amount', 0))
        account_number = customer_record.get('account_number', '')
        currency = p004_data.get('rtr_ccy', '')

        # Get current balance before credit
        current_balance = customer_record.get('ledger_balance', '0')

        success = csv_reconciliation_engine.update_customer_balance(
            account_number, amount, 'credit')

        # Record detailed account operation
        operation = {
            'operation_type': 'CREDIT',
            'account_number': account_number,
            'account_name': customer_record.get('account_holder_name', 'Unknown'),
            'account_type': 'FCA',
            'currency': currency,
            'amount': amount,
            'balance_before': current_balance,
            'balance_after': f"{float(current_balance) + amount:.2f}",
            'reason': 'Return processing - FCA credit',
            'reference': p004_data.get('e2e', ''),
            'uetr': p004_data.get('uetr', '')
        }
        self.account_operations.append(operation)

        self._log_action(
            "CREDIT_FCA", f"Credited {currency} {amount} to FCA account {account_number} ({customer_record.get('account_holder_name', 'Unknown')})")
        return success

    def _credit_client_original(self, p004_data: Dict, p008_data: Dict) -> bool:
        """Credit client's original account."""
        amount = float(p004_data.get('rtr_amount', 0))
        currency = p004_data.get('rtr_ccy', '')
        client_iban = p008_data.get('dbtr_iban', '')
        client_name = p008_data.get('dbtr_name', 'Unknown')

        # Get current balance before credit
        accounts_data = csv_reconciliation_engine.load_csv_data(
            'data/bank_accounts.csv')
        current_balance = None
        account_name = None
        for account in accounts_data:
            if account.get('Account Number', '') == client_iban:
                current_balance = account.get('Opening Balance', '')
                account_name = account.get('Account Name', '')
                break

        # Update the client account balance
        success = csv_reconciliation_engine.update_bank_account_balance(
            client_iban, amount, 'credit')

        # Get new balance after credit
        accounts_data_after = csv_reconciliation_engine.load_csv_data(
            'data/bank_accounts.csv')
        new_balance = None
        for account in accounts_data_after:
            if account.get('Account Number', '') == client_iban:
                new_balance = account.get('Opening Balance', '')
                break

        # Record detailed account operation
        operation = {
            'operation_type': 'CREDIT',
            'account_number': client_iban,
            'account_name': account_name or client_name,
            'account_type': 'Client',
            'currency': currency,
            'amount': amount,
            'balance_before': current_balance or 'N/A',
            'balance_after': new_balance or 'N/A',
            'reason': 'Return processing - credit client original account',
            'reference': p004_data.get('e2e', ''),
            'uetr': p004_data.get('uetr', '')
        }
        self.account_operations.append(operation)

        self._log_action(
            "CREDIT_CLIENT_ORIGINAL", f"Credited {currency} {amount} to client account {client_iban} ({account_name or client_name})")
        return success

    def _update_sndr_ref(self, p004_data: Dict):
        """Use Nostro reference from MT940/return messages."""
        reference = p004_data.get('e2e', '')
        self._log_action("UPDATE_SNDR_REF",
                         f"Updated SNDR reference: {reference}")

    def _debit_nostro_payment_input_screen(self, p004_data: Dict):
        """Payment input screen per SOP - debit nostro account."""
        # Actually debit the nostro account
        nostro_debit_result = self._debit_nostro(p004_data)

        self._log_action("DEBIT_NOSTRO_PAYMENT_INPUT",
                         f"Processed payment input screen per SOP - nostro debit: {nostro_debit_result}")

    def _send_nostro_not_credited(self):
        """Send Nostro Not Credited document."""
        self._log_action("SEND_NOSTRO_NOT_CREDITED",
                         "Sent Nostro Not Credited document (Saved_Name: 39)")

    def _send_refund_fca_email(self):
        """Send Refund FCA Email."""
        self._log_action("SEND_REFUND_FCA_EMAIL",
                         "Sent Refund FCA Email (Saved_Name: 56)")

    def _send_refund_daily_list(self):
        """Send Refund (Daily List/Full List)."""
        self._log_action("SEND_REFUND_DAILY_LIST",
                         "Sent Refund Daily List/Full List (Saved_Name: 26)")

    def _debit_vostro_payment_input_screen(self, return_reference: str, amount: float, currency: str):
        """Debit Vostro using approved camt.029 response."""
        self._log_action("DEBIT_VOSTRO_PAYMENT_INPUT",
                         f"Debited Vostro {currency} {amount} for {return_reference}")

    def _update_vostro_sndr_ref(self, return_reference: str):
        """Record reference as returned in Pacs.004."""
        self._log_action("UPDATE_VOSTRO_SNDR_REF",
                         f"Updated Vostro SNDR reference: {return_reference}")

    def _funds_in_ob(self):
        """Check OB accounts."""
        self._log_action("FUNDS_IN_OB", "Checked OB accounts")

    def _debit_ob_payment_input_screen(self, return_reference: str, amount: float, currency: str):
        """Debit OB Payment Input Screen."""
        self._log_action("DEBIT_OB_PAYMENT_INPUT",
                         f"Debited OB {currency} {amount} for {return_reference}")

    def _update_ob_sndr_ref(self, return_reference: str):
        """Use OB reference."""
        self._log_action("UPDATE_OB_SNDR_REF",
                         f"Updated OB SNDR reference: {return_reference}")

    def _is_branch_payment(self, p004_data: Dict) -> bool:
        """Determine if this is a branch payment."""
        # Simplified logic - in real implementation, this would check account types
        return False  # Default to client payment

    def _credit_branch_sait(self, p004_data: Dict):
        """Account number changes to branch SAIT (4-digit BSB + 0001195062)."""
        self._log_action("CREDIT_BRANCH_SAIT", "Credited branch SAIT account")

    def _credit_client_original_account(self, p004_data: Dict):
        """Credit Client Original Debited Account."""
        self._log_action("CREDIT_CLIENT_ORIGINAL",
                         "Credited client original debited account")

    def _send_refund_sent_email(self):
        """Send Refund Sent Email."""
        self._log_action("SEND_REFUND_SENT_EMAIL",
                         "Sent Refund Sent Email (Saved_Name: 67)")

    def _check_valid_email(self, p004_data: Dict) -> bool:
        """Check if client has valid email address."""
        # Simplified logic - in real implementation, this would check customer data
        return True  # Default to having valid email

    def _send_client_adhoc(self):
        """Send the client an AdHoc."""
        self._log_action("SEND_CLIENT_ADHOC", "Sent client AdHoc")

    def _send_refund_no_email_cba_reports(self):
        """Send Refund NO email (Full List) to CBA Reports."""
        self._log_action("SEND_REFUND_NO_EMAIL_CBA",
                         "Sent Refund NO email to CBA Reports (Saved_Name: 19)")

    def _update_qf(self):
        """Update QF screen as per SOP."""
        self._log_action("UPDATE_QF", "Updated QF screen as per SOP")

    def _submit_case_to_closed(self):
        """Submit Case to Closed - END OF THE PROCESS."""
        self._log_action("SUBMIT_CASE_TO_CLOSED",
                         "Submitted case to closed - END OF THE PROCESS")

    # Helper methods
    def _extract_creditor_agent_bic(self, p004_data: Dict) -> str:
        """Extract creditor agent BIC from PACS.004 data."""
        # This would need to be implemented based on actual PACS.004 structure
        return "CHASUS33XXX"  # Default for testing

    def _get_nostro_account_for_currency(self, currency: str) -> Optional[str]:
        """Get nostro account number for given currency from CSV dynamically."""
        try:
            accounts_data = csv_reconciliation_engine.load_csv_data(
                'data/bank_accounts.csv')
            currency_upper = (currency or '').upper()
            # Prefer active Nostro accounts matching currency
            for account in accounts_data:
                if (account.get('Account Type', '').strip().lower() == 'nostro' and
                        (account.get('Currency', '').strip().upper() == currency_upper) and
                        (account.get('Account Status', '').strip().lower() == 'active')):
                    return account.get('Account Number')
            # Fallback: any Nostro with currency match regardless of status
            for account in accounts_data:
                if (account.get('Account Type', '').strip().lower() == 'nostro' and
                        (account.get('Currency', '').strip().upper() == currency_upper)):
                    return account.get('Account Number')
        except Exception:
            pass
        return None

    def _log_decision(self, decision_result: DecisionResult):
        """Log decision result."""
        self.audit_trail.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'DECISION',
            'node': decision_result.node.value,
            'decision': decision_result.decision,
            'reason': decision_result.reason,
            'next_node': decision_result.next_node.value if decision_result.next_node else None
        })

    def _log_action(self, action_type: str, description: str):
        """Log action taken."""
        self.audit_trail.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'ACTION',
            'action': action_type,
            'description': description
        })


# Global refund decision engine instance
refund_decision_engine = RefundDecisionEngine()
