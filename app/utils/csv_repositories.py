"""
CSV implementations of repository interfaces.
"""

import csv
import json
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from .repositories import (
    AccountRepository, StatementRepository, LedgerRepository,
    CustomerRepository, AuditRepository,
    Account, StatementEntry, LedgerEntry, Customer
)


class CSVAccountRepository(AccountRepository):
    """CSV implementation of AccountRepository."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.accounts_file = os.path.join(data_dir, "bank_accounts.csv")

    def _load_accounts(self) -> List[Dict[str, str]]:
        """Load accounts from CSV file."""
        if not os.path.exists(self.accounts_file):
            return []

        accounts = []
        with open(self.accounts_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                accounts.append(row)
        return accounts

    def _save_accounts(self, accounts: List[Dict[str, str]]) -> bool:
        """Save accounts to CSV file."""
        if not accounts:
            return False

        try:
            with open(self.accounts_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = accounts[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(accounts)
            return True
        except Exception:
            return False

    def get_account(self, account_number: str) -> Optional[Account]:
        """Get account by account number."""
        accounts = self._load_accounts()
        for account_data in accounts:
            if account_data.get('Account Number', '') == account_number:
                return Account(
                    account_number=account_data.get('Account Number', ''),
                    account_name=account_data.get('Account Name', ''),
                    account_type=account_data.get('Account Type', ''),
                    currency=account_data.get('Currency', ''),
                    country=account_data.get('Country', ''),
                    debit_credit_authority=account_data.get(
                        'Debit/Credit Authority', ''),
                    reconciliation_type=account_data.get(
                        'Reconciliation Type', ''),
                    gl_code=account_data.get('GL Code', ''),
                    opening_balance=account_data.get('Opening Balance', ''),
                    last_reconciled_date=account_data.get(
                        'Last Reconciled Date', ''),
                    cost_center=account_data.get('Cost Center', ''),
                    account_status=account_data.get('Account Status', '')
                )
        return None

    def get_accounts_by_type(self, account_type: str) -> List[Account]:
        """Get all accounts of a specific type."""
        accounts = self._load_accounts()
        result = []
        for account_data in accounts:
            if account_data.get('Account Type', '') == account_type:
                result.append(Account(
                    account_number=account_data.get('Account Number', ''),
                    account_name=account_data.get('Account Name', ''),
                    account_type=account_data.get('Account Type', ''),
                    currency=account_data.get('Currency', ''),
                    country=account_data.get('Country', ''),
                    debit_credit_authority=account_data.get(
                        'Debit/Credit Authority', ''),
                    reconciliation_type=account_data.get(
                        'Reconciliation Type', ''),
                    gl_code=account_data.get('GL Code', ''),
                    opening_balance=account_data.get('Opening Balance', ''),
                    last_reconciled_date=account_data.get(
                        'Last Reconciled Date', ''),
                    cost_center=account_data.get('Cost Center', ''),
                    account_status=account_data.get('Account Status', '')
                ))
        return result

    def get_nostro_account_for_currency(self, currency: str) -> Optional[str]:
        """Get nostro account number for a currency."""
        nostro_accounts = self.get_accounts_by_type('Nostro')
        for account in nostro_accounts:
            if account.currency == currency:
                return account.account_number
        return None

    def get_customer_accounts(self, customer_iban: str) -> List[Dict[str, str]]:
        """Get all accounts for a specific customer by IBAN."""
        accounts = self._load_accounts()
        customer_accounts = []
        
        for account_data in accounts:
            # Check if this account belongs to the customer
            account_iban = account_data.get('IBAN', '')
            if account_iban == customer_iban:
                customer_accounts.append(account_data)
        
        return customer_accounts

    def update_account_balance(self, account_number: str, amount: float, operation: str, 
                              transaction_id: str = "", reference: str = "", 
                              description: str = "", audit_repo=None) -> bool:
        """Update account balance (debit/credit) and record transaction history."""
        accounts = self._load_accounts()
        for account_data in accounts:
            if account_data.get('Account Number', '') == account_number:
                current_balance = account_data.get('Opening Balance', '0')
                balance_before = current_balance
                
                # Parse balance (handle currency prefixes and commas)
                balance_str = current_balance.replace(',', '').replace(
                    account_data.get('Currency', ''), '').strip()
                try:
                    current_amount = float(balance_str)
                except ValueError:
                    current_amount = 0.0

                if operation == 'debit':
                    new_amount = current_amount - amount
                elif operation == 'credit':
                    new_amount = current_amount + amount
                else:
                    return False

                # Format new balance with currency
                currency = account_data.get('Currency', '')
                balance_after = f"{currency} {new_amount:,.2f}"
                account_data['Opening Balance'] = balance_after
                
                # Save updated accounts
                success = self._save_accounts(accounts)
                
                # Record transaction history if audit repository is provided
                if success and audit_repo and transaction_id:
                    audit_repo.record_balance_change(
                        transaction_id=transaction_id,
                        account_number=account_number,
                        operation=operation,
                        amount=amount,
                        currency=currency,
                        balance_before=balance_before,
                        balance_after=balance_after,
                        reference=reference,
                        description=description
                    )
                
                return success
        return False

    def get_all_accounts(self) -> List[Account]:
        """Get all accounts."""
        accounts = self._load_accounts()
        result = []
        for account_data in accounts:
            result.append(Account(
                account_number=account_data.get('Account Number', ''),
                account_name=account_data.get('Account Name', ''),
                account_type=account_data.get('Account Type', ''),
                currency=account_data.get('Currency', ''),
                country=account_data.get('Country', ''),
                debit_credit_authority=account_data.get(
                    'Debit/Credit Authority', ''),
                reconciliation_type=account_data.get(
                    'Reconciliation Type', ''),
                gl_code=account_data.get('GL Code', ''),
                opening_balance=account_data.get('Opening Balance', ''),
                last_reconciled_date=account_data.get(
                    'Last Reconciled Date', ''),
                cost_center=account_data.get('Cost Center', ''),
                account_status=account_data.get('Account Status', '')
            ))
        return result


class CSVStatementRepository(StatementRepository):
    """CSV implementation of StatementRepository."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.nostro_file = os.path.join(data_dir, "nostro_statement.csv")
        self.vostro_file = os.path.join(data_dir, "vostro_statement.csv")

    def _load_csv_data(self, file_path: str) -> List[Dict[str, str]]:
        """Load data from CSV file."""
        if not os.path.exists(file_path):
            return []

        data = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data

    def _save_csv_data(self, file_path: str, data: List[Dict[str, str]]) -> bool:
        """Save data to CSV file."""
        if not data:
            return False

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception:
            return False

    def _dict_to_statement_entry(self, data: Dict[str, str]) -> StatementEntry:
        """Convert dict to StatementEntry."""
        return StatementEntry(
            statement_id=data.get('Statement ID', ''),
            value_date=data.get('Value Date', ''),
            currency=data.get('Currency', ''),
            amount=data.get('Amount', ''),
            dr_cr=data.get('DR / CR', ''),
            description=data.get('Description', ''),
            reference=data.get('Reference', '')
        )

    def get_nostro_entries(self) -> List[StatementEntry]:
        """Get all nostro statement entries."""
        data = self._load_csv_data(self.nostro_file)
        return [self._dict_to_statement_entry(row) for row in data]

    def get_vostro_entries(self) -> List[StatementEntry]:
        """Get all vostro statement entries."""
        data = self._load_csv_data(self.vostro_file)
        return [self._dict_to_statement_entry(row) for row in data]

    def find_nostro_match(self, reference: str, uetr: str, amount: float, currency: str) -> Dict[str, Any]:
        """Find matching nostro entry (exact or partial)."""
        entries = self.get_nostro_entries()

        for entry in entries:
            # Extract reference and UETR from entry reference field
            entry_ref = self._extract_reference_from_description(
                entry.reference)
            entry_uetr = self._extract_uetr_from_description(entry.reference)

            # Check for exact match
            if (entry_ref == reference and
                entry_uetr == uetr and
                float(entry.amount) == amount and
                entry.currency == currency and
                    entry.dr_cr == 'CR'):

                return {
                    'found': True,
                    'match_type': 'exact',
                    'nostro_entry': entry,
                    'match_details': {
                        'reference_match': True,
                        'uetr_match': True,
                        'amount_match': True,
                        'currency_match': True,
                        'credit_match': True
                    }
                }

        # Check for partial matches (missing :61: but has :86:)
        for entry in entries:
            entry_ref = self._extract_reference_from_description(
                entry.reference)
            entry_uetr = self._extract_uetr_from_description(entry.reference)

            if (entry_ref == reference and
                entry_uetr == uetr and
                    entry.dr_cr == 'CR'):

                return {
                    'found': True,
                    'match_type': 'partial',
                    'nostro_entry': entry,
                    'match_details': {
                        'reference_match': True,
                        'uetr_match': True,
                        'amount_match': False,  # Missing :61: amount
                        'currency_match': False,
                        'credit_match': True
                    }
                }

        return {
            'found': False,
            'match_type': 'none',
            'nostro_entry': None,
            'match_details': {}
        }

    def _extract_reference_from_description(self, description: str) -> str:
        """Extract reference from MT940-style description."""
        if '/TRN/' in description:
            parts = description.split('/TRN/')
            if len(parts) > 1:
                return parts[1].split('/')[0]
        return ''

    def _extract_uetr_from_description(self, description: str) -> str:
        """Extract UETR from MT940-style description."""
        if '/UETR/' in description:
            parts = description.split('/UETR/')
            if len(parts) > 1:
                return parts[1].split('/')[0]
        return ''

    def add_nostro_entry(self, entry: StatementEntry) -> bool:
        """Add new nostro statement entry."""
        data = self._load_csv_data(self.nostro_file)
        new_row = {
            'Statement ID': entry.statement_id,
            'Value Date': entry.value_date,
            'Currency': entry.currency,
            'Amount': entry.amount,
            'DR / CR': entry.dr_cr,
            'Description': entry.description,
            'Reference': entry.reference
        }
        data.append(new_row)
        return self._save_csv_data(self.nostro_file, data)

    def add_vostro_entry(self, entry: StatementEntry) -> bool:
        """Add new vostro statement entry."""
        data = self._load_csv_data(self.vostro_file)
        new_row = {
            'Statement ID': entry.statement_id,
            'Value Date': entry.value_date,
            'Currency': entry.currency,
            'Amount': entry.amount,
            'DR / CR': entry.dr_cr,
            'Description': entry.description,
            'Reference': entry.reference
        }
        data.append(new_row)
        return self._save_csv_data(self.vostro_file, data)


class CSVLedgerRepository(LedgerRepository):
    """CSV implementation of LedgerRepository."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ledger_file = os.path.join(data_dir, "internal_ledger.csv")

    def _load_ledger_data(self) -> List[Dict[str, str]]:
        """Load ledger data from CSV file."""
        if not os.path.exists(self.ledger_file):
            return []

        data = []
        with open(self.ledger_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data

    def _save_ledger_data(self, data: List[Dict[str, str]]) -> bool:
        """Save ledger data to CSV file."""
        if not data:
            return False

        try:
            with open(self.ledger_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception:
            return False

    def get_ledger_entries(self) -> List[LedgerEntry]:
        """Get all ledger entries."""
        data = self._load_ledger_data()
        result = []
        for row in data:
            result.append(LedgerEntry(
                transaction_id=row.get('Transaction ID', ''),
                value_date=row.get('Value Date', ''),
                currency=row.get('Currency', ''),
                amount=row.get('Amount', ''),
                counterparty=row.get('Counterparty', ''),
                reference=row.get('Reference', ''),
                return_reason=row.get('Return Reason', '')
            ))
        return result

    def get_entry_by_reference(self, reference: str) -> Optional[LedgerEntry]:
        """Get ledger entry by reference."""
        entries = self.get_ledger_entries()
        for entry in entries:
            if entry.reference == reference:
                return entry
        return None

    def add_ledger_entry(self, entry: LedgerEntry) -> bool:
        """Add new ledger entry."""
        data = self._load_ledger_data()
        new_row = {
            'Transaction ID': entry.transaction_id,
            'Value Date': entry.value_date,
            'Currency': entry.currency,
            'Amount': entry.amount,
            'Counterparty': entry.counterparty,
            'Reference': entry.reference,
            'Return Reason': entry.return_reason
        }
        data.append(new_row)
        return self._save_ledger_data(data)

    def update_entry_status(self, reference: str, status: str) -> bool:
        """Update entry status."""
        data = self._load_ledger_data()
        for row in data:
            if row.get('Reference', '') == reference:
                row['Return Reason'] = status
                return self._save_ledger_data(data)
        return False


class CSVCustomerRepository(CustomerRepository):
    """CSV implementation of CustomerRepository."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.customers_file = os.path.join(data_dir, "customer_data.csv")

    def _load_customers(self) -> List[Dict[str, str]]:
        """Load customers from CSV file."""
        if not os.path.exists(self.customers_file):
            return []

        customers = []
        with open(self.customers_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                customers.append(row)
        return customers

    def get_customer_by_account(self, account_number: str) -> Optional[Customer]:
        """Get customer by account number."""
        customers = self._load_customers()
        for customer_data in customers:
            if customer_data.get('Account Number', '') == account_number:
                return Customer(
                    customer_name=customer_data.get('Customer Name', ''),
                    account_name=customer_data.get('Account Name', ''),
                    account_number=customer_data.get('Account Number', ''),
                    account_type=customer_data.get('Account Type', ''),
                    ledger_balance=customer_data.get('Ledger Balance', ''),
                    available_balance=customer_data.get(
                        'Available Balance', ''),
                    account_status=customer_data.get('Account Status', ''),
                    email=customer_data.get('e-mail', '')
                )
        return None

    def get_customer_by_iban(self, iban: str) -> Optional[Customer]:
        """Get customer by IBAN."""
        # For now, treat IBAN same as account number
        return self.get_customer_by_account(iban)

    def get_all_customers(self) -> List[Customer]:
        """Get all customers."""
        customers = self._load_customers()
        result = []
        for customer_data in customers:
            result.append(Customer(
                customer_name=customer_data.get('Customer Name', ''),
                account_name=customer_data.get('Account Name', ''),
                account_number=customer_data.get('Account Number', ''),
                account_type=customer_data.get('Account Type', ''),
                ledger_balance=customer_data.get('Ledger Balance', ''),
                available_balance=customer_data.get('Available Balance', ''),
                account_status=customer_data.get('Account Status', ''),
                email=customer_data.get('e-mail', '')
            ))
        return result

    def suggest_alternate_account(self, original_account: str) -> Optional[str]:
        """Suggest alternate active account for customer."""
        # Simple implementation: find another active account for the same customer
        customers = self._load_customers()
        original_customer = None

        # Find the original customer
        for customer_data in customers:
            if customer_data.get('Account Number', '') == original_account:
                original_customer = customer_data.get('Customer Name', '')
                break

        if not original_customer:
            return None

        # Find another active account for the same customer
        for customer_data in customers:
            if (customer_data.get('Customer Name', '') == original_customer and
                customer_data.get('Account Number', '') != original_account and
                    customer_data.get('Account Status', '') == 'Active'):
                return customer_data.get('Account Number', '')

        return None


class CSVAuditRepository(AuditRepository):
    """CSV implementation of AuditRepository."""

    def __init__(self, data_dir: str = "data", reports_dir: str = "csv_reports"):
        self.data_dir = data_dir
        self.reports_dir = reports_dir
        self.audit_file = os.path.join(data_dir, "audit_log.csv")

        # Ensure reports directory exists
        os.makedirs(reports_dir, exist_ok=True)

    def _load_audit_data(self) -> List[Dict[str, str]]:
        """Load audit data from CSV file."""
        if not os.path.exists(self.audit_file):
            return []

        data = []
        with open(self.audit_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data

    def _save_audit_data(self, data: List[Dict[str, str]]) -> bool:
        """Save audit data to CSV file."""
        try:
            with open(self.audit_file, 'w', newline='', encoding='utf-8') as f:
                if data:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            return True
        except Exception:
            return False

    def add_audit_event(self, event: Dict[str, Any]) -> bool:
        """Add audit event."""
        data = self._load_audit_data()

        # Convert event to CSV row format
        event_row = {
            'Timestamp': event.get('timestamp', datetime.now().isoformat()),
            'Transaction ID': event.get('transaction_id', ''),
            'Event Type': event.get('event_type', ''),
            'Actor': event.get('actor', ''),
            'Action': event.get('action', ''),
            'Details': json.dumps(event.get('details', {}), default=str),
            'Level': event.get('level', 'INFO')
        }

        data.append(event_row)
        return self._save_audit_data(data)

    def get_audit_events(self, transaction_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit events, optionally filtered by transaction ID."""
        data = self._load_audit_data()
        result = []

        for row in data:
            if transaction_id and row.get('Transaction ID', '') != transaction_id:
                continue

            event = {
                'timestamp': row.get('Timestamp', ''),
                'transaction_id': row.get('Transaction ID', ''),
                'event_type': row.get('Event Type', ''),
                'actor': row.get('Actor', ''),
                'action': row.get('Action', ''),
                'details': json.loads(row.get('Details', '{}')),
                'level': row.get('Level', 'INFO')
            }
            result.append(event)

        return result

    def save_run_report(self, run_id: str, report_data: Dict[str, Any]) -> str:
        """Save run report and return file path."""
        filename = f"{run_id}.json"
        file_path = os.path.join(self.reports_dir, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2,
                          ensure_ascii=False, default=str)
            return file_path
        except Exception:
            return ""

    def get_run_report(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run report by ID."""
        filename = f"{run_id}.json"
        file_path = os.path.join(self.reports_dir, filename)

        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def record_balance_change(self, transaction_id: str, account_number: str, 
                             operation: str, amount: float, currency: str,
                             balance_before: str, balance_after: str, 
                             reference: str = "", description: str = "") -> bool:
        """Record every balance change with full audit trail."""
        try:
            # Create transaction_history.csv if it doesn't exist
            history_file = os.path.join(self.data_dir, "transaction_history.csv")
            
            # Check if file exists, if not create with headers
            file_exists = os.path.exists(history_file)
            
            with open(history_file, 'a', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'Transaction ID', 'Timestamp', 'Account Number', 'Account Name',
                    'Operation', 'Amount', 'Currency', 'Balance Before', 'Balance After',
                    'Reference', 'Description'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                
                # Get account name from bank_accounts.csv
                account_name = "Unknown Account"
                try:
                    accounts_file = os.path.join(self.data_dir, "bank_accounts.csv")
                    if os.path.exists(accounts_file):
                        with open(accounts_file, 'r', newline='', encoding='utf-8') as af:
                            reader = csv.DictReader(af)
                            for row in reader:
                                if row.get('Account Number', '') == account_number:
                                    account_name = row.get('Account Name', 'Unknown Account')
                                    break
                except Exception:
                    pass  # Use default account name
                
                # Write transaction record
                writer.writerow({
                    'Transaction ID': transaction_id,
                    'Timestamp': datetime.now().isoformat(),
                    'Account Number': account_number,
                    'Account Name': account_name,
                    'Operation': operation,
                    'Amount': amount,
                    'Currency': currency,
                    'Balance Before': balance_before,
                    'Balance After': balance_after,
                    'Reference': reference,
                    'Description': description
                })
            
            return True
        except Exception as e:
            print(f"Error recording balance change: {e}")
            return False


# Factory function to create repository instances
def create_repositories(data_dir: str = "data", reports_dir: str = "csv_reports"):
    """Create repository instances."""
    return {
        'accounts': CSVAccountRepository(data_dir),
        'statements': CSVStatementRepository(data_dir),
        'ledger': CSVLedgerRepository(data_dir),
        'customers': CSVCustomerRepository(data_dir),
        'audit': CSVAuditRepository(data_dir, reports_dir)
    }


