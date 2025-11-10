"""
CSV-based reconciliation system for nostro/vostro statements and internal ledger.
Replaces API mockups with direct CSV file operations.
"""

import csv
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ReconciliationResult:
    """Result of reconciliation operation."""
    found: bool
    match_type: str  # 'exact', 'partial', 'none'
    nostro_entry: Optional[Dict] = None
    vostro_entry: Optional[Dict] = None
    internal_entry: Optional[Dict] = None
    match_details: Optional[Dict] = None
    error: Optional[str] = None


class CSVReconciliationEngine:
    """CSV-based reconciliation engine for payment returns."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.nostro_statement_path = f"{data_dir}/nostro_statement.csv"
        self.vostro_statement_path = f"{data_dir}/vostro_statement.csv"
        self.internal_ledger_path = f"{data_dir}/internal_ledger.csv"
        self.bank_accounts_path = f"{data_dir}/bank_accounts.csv"
        self.customer_data_path = f"{data_dir}/customer_data.csv"

    def load_csv_data(self, file_path: str) -> List[Dict]:
        """Load CSV data into list of dictionaries."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            return []
        except Exception as e:
            raise Exception(f"Error loading {file_path}: {str(e)}")

    def save_csv_data(self, file_path: str, data: List[Dict], fieldnames: List[str]):
        """Save data to CSV file."""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            raise Exception(f"Error saving {file_path}: {str(e)}")

    def extract_reference_from_description(self, description: str) -> Optional[str]:
        """Extract reference from MT940-like description."""
        if not description:
            return None

        # Look for /TRN/ pattern
        trn_match = re.search(r'/TRN/([^/]+)', description)
        if trn_match:
            return trn_match.group(1)

        # Look for other reference patterns
        ref_match = re.search(r'RET-([A-Z]+-\d+)', description)
        if ref_match:
            return f"RET-{ref_match.group(1)}"

        return None

    def extract_uetr_from_description(self, description: str) -> Optional[str]:
        """Extract UETR from MT940-like description."""
        if not description:
            return None

        # Look for /UETR/ pattern
        uetr_match = re.search(r'/UETR/([^/]+)', description)
        if uetr_match:
            return uetr_match.group(1)

        return None

    def find_nostro_match(self, return_reference: str, uetr: str, amount: float, currency: str) -> ReconciliationResult:
        """Find matching nostro statement entry."""
        nostro_data = self.load_csv_data(self.nostro_statement_path)

        for entry in nostro_data:
            # Extract reference from reference field (not description)
            entry_ref = self.extract_reference_from_description(
                entry.get('Reference', ''))
            entry_uetr = self.extract_uetr_from_description(
                entry.get('Reference', ''))

            # Check for exact match
            if (entry_ref == return_reference and
                entry_uetr == uetr and
                float(entry.get('Amount', 0)) == amount and
                entry.get('Currency', '') == currency and
                    entry.get('DR / CR', '') == 'CR'):

                return ReconciliationResult(
                    found=True,
                    match_type='exact',
                    nostro_entry=entry,
                    match_details={
                        'reference_match': True,
                        'uetr_match': True,
                        'amount_match': True,
                        'currency_match': True,
                        'credit_match': True
                    }
                )

        # Check for partial matches (missing :61: but has :86:)
        for entry in nostro_data:
            entry_ref = self.extract_reference_from_description(
                entry.get('Reference', ''))
            entry_uetr = self.extract_uetr_from_description(
                entry.get('Reference', ''))

            if (entry_ref == return_reference and
                entry_uetr == uetr and
                    entry.get('DR / CR', '') == 'CR'):

                return ReconciliationResult(
                    found=True,
                    match_type='partial',
                    nostro_entry=entry,
                    match_details={
                        'reference_match': True,
                        'uetr_match': True,
                        'amount_match': False,  # Missing :61: amount
                        'currency_match': False,
                        'credit_match': True,
                        'note': 'Nostro entry found but missing :61: amount'
                    }
                )

        return ReconciliationResult(
            found=False,
            match_type='none',
            error=f"No nostro entry found for reference {return_reference}, UETR {uetr}"
        )

    def find_vostro_match(self, return_reference: str, uetr: str, amount: float, currency: str) -> ReconciliationResult:
        """Find matching vostro statement entry."""
        vostro_data = self.load_csv_data(self.vostro_statement_path)

        for entry in vostro_data:
            # Extract reference from description
            entry_ref = self.extract_reference_from_description(
                entry.get('Description', ''))

            # Check for debit authority match
            if (entry_ref == return_reference and
                float(entry.get('Amount', 0)) == amount and
                entry.get('Currency', '') == currency and
                    entry.get('DR / CR', '') == 'DR'):

                return ReconciliationResult(
                    found=True,
                    match_type='exact',
                    vostro_entry=entry,
                    match_details={
                        'reference_match': True,
                        'amount_match': True,
                        'currency_match': True,
                        'debit_match': True,
                        'debit_authority': True
                    }
                )

        return ReconciliationResult(
            found=False,
            match_type='none',
            error=f"No vostro entry found for reference {return_reference}"
        )

    def find_internal_ledger_match(self, return_reference: str, uetr: str) -> ReconciliationResult:
        """Find matching internal ledger entry."""
        ledger_data = self.load_csv_data(self.internal_ledger_path)

        for entry in ledger_data:
            if (entry.get('Reference', '') == return_reference or
                    entry.get('Transaction ID', '') == return_reference):

                return ReconciliationResult(
                    found=True,
                    match_type='exact',
                    internal_entry=entry,
                    match_details={
                        'reference_match': True,
                        'transaction_id_match': True
                    }
                )

        return ReconciliationResult(
            found=False,
            match_type='none',
            error=f"No internal ledger entry found for reference {return_reference}"
        )

    def check_debit_authority(self, creditor_agent_bic: str, currency: str, amount: float) -> Dict:
        """Check if debit authority exists for vostro account."""
        bank_accounts = self.load_csv_data(self.bank_accounts_path)

        # Find corresponding vostro account
        for account in bank_accounts:
            if (account.get('Account Type', '') == 'Vostro' and
                account.get('Currency', '') == currency and
                    creditor_agent_bic in account.get('Account Name', '')):

                authority = account.get('Debit/Credit Authority', '')
                if authority == 'Yes':
                    return {
                        'authority_exists': True,
                        'account_number': account.get('Account Number', ''),
                        'authority_type': 'Pre-approved'
                    }
                elif authority == 'By Request':
                    return {
                        'authority_exists': False,
                        'account_number': account.get('Account Number', ''),
                        'authority_type': 'By Request',
                        'requires_camt029': True
                    }

        return {
            'authority_exists': False,
            'authority_type': 'Not Found',
            'requires_camt029': True
        }

    def create_debit_authority_request(self, return_reference: str, uetr: str, creditor_agent_bic: str,
                                       amount: float, currency: str, reason: str) -> Dict:
        """Create camt.029 debit authority request."""
        request_id = f"AUTHREQ-CBA-{datetime.now().strftime('%Y%m%d')}-{return_reference[-6:]}"

        camt029_request = {
            'request_id': request_id,
            'request_type': 'camt.029',
            'case_id': return_reference,
            'uetr': uetr,
            'creditor_agent_bic': creditor_agent_bic,
            'amount': amount,
            'currency': currency,
            'reason': reason,
            'justification': 'AUTH',
            'request_date': datetime.now().isoformat(),
            'status': 'PENDING'
        }

        return camt029_request

    def process_debit_authority_response(self, request_id: str, approved: bool, response_details: str = "") -> Dict:
        """Process debit authority response."""
        response = {
            'request_id': request_id,
            'approved': approved,
            'response_details': response_details,
            'response_date': datetime.now().isoformat(),
            'status': 'APPROVED' if approved else 'REJECTED'
        }

        return response

    def update_nostro_statement(self, entry_data: Dict) -> bool:
        """Add new entry to nostro statement."""
        try:
            nostro_data = self.load_csv_data(self.nostro_statement_path)
            fieldnames = ['Statement ID', 'Value Date', 'Currency',
                          'Amount', 'DR / CR', 'Description', 'Reference']

            # Generate new statement ID
            entry_data['Statement ID'] = f"NST-{entry_data['Currency']}-{datetime.now().strftime('%Y%m%d')}-{len(nostro_data)+1:02d}"

            nostro_data.append(entry_data)
            self.save_csv_data(self.nostro_statement_path,
                               nostro_data, fieldnames)
            return True
        except Exception as e:
            print(f"Error updating nostro statement: {e}")
            return False

    def update_vostro_statement(self, entry_data: Dict) -> bool:
        """Add new entry to vostro statement."""
        try:
            vostro_data = self.load_csv_data(self.vostro_statement_path)
            fieldnames = ['Statement ID', 'Value Date', 'Currency',
                          'Amount', 'DR / CR', 'Description', 'Reference']

            # Generate new statement ID
            entry_data['Statement ID'] = f"VST-{entry_data['Currency']}-{datetime.now().strftime('%Y%m%d')}-{len(vostro_data)+1:02d}"

            vostro_data.append(entry_data)
            self.save_csv_data(self.vostro_statement_path,
                               vostro_data, fieldnames)
            return True
        except Exception as e:
            print(f"Error updating vostro statement: {e}")
            return False

    def update_internal_ledger(self, entry_data: Dict) -> bool:
        """Add new entry to internal ledger."""
        try:
            ledger_data = self.load_csv_data(self.internal_ledger_path)
            fieldnames = ['Transaction ID', 'Value Date', 'Currency',
                          'Amount', 'Counterparty', 'Reference', 'Return Reason']

            # Generate new transaction ID
            entry_data['Transaction ID'] = f"CBA{len(ledger_data)+1:03d}"

            ledger_data.append(entry_data)
            self.save_csv_data(self.internal_ledger_path,
                               ledger_data, fieldnames)
            return True
        except Exception as e:
            print(f"Error updating internal ledger: {e}")
            return False

    def update_bank_account_balance(self, account_number: str, amount: float, operation: str) -> bool:
        """Update bank account balance (debit/credit)."""
        try:
            accounts_data = self.load_csv_data(self.bank_accounts_path)
            fieldnames = ['Account Number', 'Account Name', 'Account Type', 'Currency', 'Country',
                          'Debit/Credit Authority', 'Reconciliation Type', 'GL Code', 'Opening Balance',
                          'Last Reconciled Date', 'Cost Center', 'Account Status']

            for account in accounts_data:
                if account.get('Account Number', '') == account_number:
                    current_balance = float(account.get('Opening Balance', '0').replace(',', '').replace(
                        'AUD ', '').replace('USD ', '').replace('EUR ', '').replace('SGD ', ''))

                    if operation == 'debit':
                        new_balance = current_balance - amount
                    elif operation == 'credit':
                        new_balance = current_balance + amount
                    else:
                        return False

                    # Update balance with currency prefix
                    currency = account.get('Currency', 'AUD')
                    account['Opening Balance'] = f"{currency} {new_balance:,.2f}"
                    account['Last Reconciled Date'] = datetime.now().strftime(
                        '%Y-%m-%d')
                    break

            self.save_csv_data(self.bank_accounts_path,
                               accounts_data, fieldnames)
            return True
        except Exception as e:
            print(f"Error updating bank account balance: {e}")
            return False

    def update_customer_balance(self, account_number: str, amount: float, operation: str) -> bool:
        """Update customer account balance."""
        try:
            customer_data = self.load_csv_data(self.customer_data_path)
            fieldnames = ['Customer Name', 'Account Name', 'Account Number', 'Account Type',
                          'Ledger Balance', 'Available Balance', 'Account Status', 'e-mail']

            for customer in customer_data:
                if customer.get('Account Number', '') == account_number:
                    # Update both ledger and available balance
                    for balance_field in ['Ledger Balance', 'Available Balance']:
                        current_balance = float(customer.get(balance_field, '0').replace(',', '').replace(
                            'AUD ', '').replace('USD ', '').replace('EUR ', '').replace('SGD ', ''))

                        if operation == 'debit':
                            new_balance = current_balance - amount
                        elif operation == 'credit':
                            new_balance = current_balance + amount
                        else:
                            return False

                        # Determine currency from account type or existing balance
                        currency = 'AUD'  # Default
                        if 'USD' in customer.get('Account Type', ''):
                            currency = 'USD'
                        elif 'EUR' in customer.get('Account Type', ''):
                            currency = 'EUR'
                        elif 'SGD' in customer.get('Account Type', ''):
                            currency = 'SGD'

                        customer[balance_field] = f"{currency} {new_balance:,.2f}"
                    break

            self.save_csv_data(self.customer_data_path,
                               customer_data, fieldnames)
            return True
        except Exception as e:
            print(f"Error updating customer balance: {e}")
            return False


# Global reconciliation engine instance
csv_reconciliation_engine = CSVReconciliationEngine()
