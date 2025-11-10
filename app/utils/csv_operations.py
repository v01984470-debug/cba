"""
CSV Operations Manager
Handles all CSV file operations for the refund processing system.
"""

import csv
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class CSVOperationResult:
    """Result of CSV operation."""
    success: bool
    operation: str
    file_path: str
    records_affected: int
    error: Optional[str] = None
    data: Optional[Any] = None


class CSVOperationsManager:
    """Manages all CSV file operations for the refund system."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """Ensure data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def load_csv(self, filename: str) -> List[Dict]:
        """Load CSV file into list of dictionaries."""
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            return []
        except Exception as e:
            raise Exception(f"Error loading {file_path}: {str(e)}")

    def save_csv(self, filename: str, data: List[Dict], fieldnames: List[str]) -> CSVOperationResult:
        """Save data to CSV file."""
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            return CSVOperationResult(
                success=True,
                operation="save_csv",
                file_path=file_path,
                records_affected=len(data)
            )
        except Exception as e:
            return CSVOperationResult(
                success=False,
                operation="save_csv",
                file_path=file_path,
                records_affected=0,
                error=str(e)
            )

    def append_to_csv(self, filename: str, new_record: Dict, fieldnames: List[str]) -> CSVOperationResult:
        """Append new record to CSV file."""
        # Load existing data
        existing_data = self.load_csv(filename)

        # Add new record
        existing_data.append(new_record)

        # Save back to file
        return self.save_csv(filename, existing_data, fieldnames)

    def update_csv_record(self, filename: str, key_field: str, key_value: str,
                          updates: Dict, fieldnames: List[str]) -> CSVOperationResult:
        """Update specific record in CSV file."""
        # Load existing data
        existing_data = self.load_csv(filename)

        # Find and update record
        records_updated = 0
        for record in existing_data:
            if record.get(key_field) == key_value:
                record.update(updates)
                records_updated += 1

        if records_updated == 0:
            return CSVOperationResult(
                success=False,
                operation="update_csv_record",
                file_path=os.path.join(self.data_dir, filename),
                records_affected=0,
                error=f"Record with {key_field}={key_value} not found"
            )

        # Save back to file
        result = self.save_csv(filename, existing_data, fieldnames)
        result.records_affected = records_updated
        return result

    def find_csv_record(self, filename: str, key_field: str, key_value: str) -> Optional[Dict]:
        """Find specific record in CSV file."""
        data = self.load_csv(filename)
        for record in data:
            if record.get(key_field) == key_value:
                return record
        return None

    def find_csv_records(self, filename: str, filter_func) -> List[Dict]:
        """Find records matching filter function."""
        data = self.load_csv(filename)
        return [record for record in data if filter_func(record)]

    # Specific operations for refund processing

    def update_bank_account_balance(self, account_number: str, amount: float, operation: str) -> CSVOperationResult:
        """Update bank account balance."""
        data = self.load_csv("bank_accounts.csv")
        fieldnames = ['Account Number', 'Account Name', 'Account Type', 'Currency', 'Country',
                      'Debit/Credit Authority', 'Reconciliation Type', 'GL Code', 'Opening Balance',
                      'Last Reconciled Date', 'Cost Center', 'Account Status']

        records_updated = 0
        for account in data:
            if account.get('Account Number') == account_number:
                # Parse current balance
                balance_str = account.get('Opening Balance', '0')
                currency = account.get('Currency', 'AUD')

                # Extract numeric value
                balance_value = self._parse_balance(balance_str)

                # Apply operation
                if operation == 'debit':
                    new_balance = balance_value - amount
                elif operation == 'credit':
                    new_balance = balance_value + amount
                else:
                    return CSVOperationResult(
                        success=False,
                        operation="update_bank_account_balance",
                        file_path=os.path.join(
                            self.data_dir, "bank_accounts.csv"),
                        records_affected=0,
                        error=f"Invalid operation: {operation}"
                    )

                # Update balance
                account['Opening Balance'] = f"{currency} {new_balance:,.2f}"
                account['Last Reconciled Date'] = datetime.now().strftime(
                    '%Y-%m-%d')
                records_updated += 1
                break

        if records_updated == 0:
            return CSVOperationResult(
                success=False,
                operation="update_bank_account_balance",
                file_path=os.path.join(self.data_dir, "bank_accounts.csv"),
                records_affected=0,
                error=f"Account {account_number} not found"
            )

        result = self.save_csv("bank_accounts.csv", data, fieldnames)
        result.records_affected = records_updated
        return result

    def update_customer_balance(self, account_number: str, amount: float, operation: str) -> CSVOperationResult:
        """Update customer account balance."""
        data = self.load_csv("customer_data.csv")
        fieldnames = ['Customer Name', 'Account Name', 'Account Number', 'Account Type',
                      'Ledger Balance', 'Available Balance', 'Account Status', 'e-mail']

        records_updated = 0
        for customer in data:
            if customer.get('Account Number') == account_number:
                # Update both ledger and available balance
                for balance_field in ['Ledger Balance', 'Available Balance']:
                    balance_str = customer.get(balance_field, '0')
                    balance_value = self._parse_balance(balance_str)

                    if operation == 'debit':
                        new_balance = balance_value - amount
                    elif operation == 'credit':
                        new_balance = balance_value + amount
                    else:
                        return CSVOperationResult(
                            success=False,
                            operation="update_customer_balance",
                            file_path=os.path.join(
                                self.data_dir, "customer_data.csv"),
                            records_affected=0,
                            error=f"Invalid operation: {operation}"
                        )

                    # Determine currency
                    currency = self._extract_currency_from_balance(balance_str)
                    customer[balance_field] = f"{currency} {new_balance:,.2f}"

                records_updated += 1
                break

        if records_updated == 0:
            return CSVOperationResult(
                success=False,
                operation="update_customer_balance",
                file_path=os.path.join(self.data_dir, "customer_data.csv"),
                records_affected=0,
                error=f"Customer account {account_number} not found"
            )

        result = self.save_csv("customer_data.csv", data, fieldnames)
        result.records_affected = records_updated
        return result

    def add_nostro_statement_entry(self, entry_data: Dict) -> CSVOperationResult:
        """Add new entry to nostro statement."""
        # Generate statement ID
        entry_data['Statement ID'] = f"NST-{entry_data.get('Currency', 'USD')}-{datetime.now().strftime('%Y%m%d')}-{len(self.load_csv('nostro_statement.csv'))+1:02d}"

        fieldnames = ['Statement ID', 'Value Date', 'Currency',
                      'Amount', 'DR / CR', 'Description', 'Reference']
        return self.append_to_csv("nostro_statement.csv", entry_data, fieldnames)

    def add_vostro_statement_entry(self, entry_data: Dict) -> CSVOperationResult:
        """Add new entry to vostro statement."""
        # Generate statement ID
        entry_data['Statement ID'] = f"VST-{entry_data.get('Currency', 'USD')}-{datetime.now().strftime('%Y%m%d')}-{len(self.load_csv('vostro_statement.csv'))+1:02d}"

        fieldnames = ['Statement ID', 'Value Date', 'Currency',
                      'Amount', 'DR / CR', 'Description', 'Reference']
        return self.append_to_csv("vostro_statement.csv", entry_data, fieldnames)

    def add_internal_ledger_entry(self, entry_data: Dict) -> CSVOperationResult:
        """Add new entry to internal ledger."""
        # Generate transaction ID
        entry_data['Transaction ID'] = f"CBA{len(self.load_csv('internal_ledger.csv'))+1:03d}"

        fieldnames = ['Transaction ID', 'Value Date', 'Currency',
                      'Amount', 'Counterparty', 'Reference', 'Return Reason']
        return self.append_to_csv("internal_ledger.csv", entry_data, fieldnames)

    def mark_ledger_entry_processed(self, transaction_id: str, processing_details: Dict) -> CSVOperationResult:
        """Mark internal ledger entry as processed."""
        updates = {
            'Processing Status': 'PROCESSED',
            'Processing Date': datetime.now().strftime('%Y-%m-%d'),
            'Processing Details': json.dumps(processing_details)
        }

        fieldnames = ['Transaction ID', 'Value Date', 'Currency', 'Amount', 'Counterparty',
                      'Reference', 'Return Reason', 'Processing Status', 'Processing Date', 'Processing Details']
        return self.update_csv_record("internal_ledger.csv", "Transaction ID", transaction_id, updates, fieldnames)

    def get_account_by_number(self, account_number: str) -> Optional[Dict]:
        """Get bank account by account number."""
        return self.find_csv_record("bank_accounts.csv", "Account Number", account_number)

    def get_customer_by_account_number(self, account_number: str) -> Optional[Dict]:
        """Get customer by account number."""
        return self.find_csv_record("customer_data.csv", "Account Number", account_number)

    def get_nostro_entries_by_reference(self, reference: str) -> List[Dict]:
        """Get nostro entries by reference."""
        def filter_func(entry):
            return reference in entry.get('Reference', '') or reference in entry.get('Description', '')

        return self.find_csv_records("nostro_statement.csv", filter_func)

    def get_vostro_entries_by_reference(self, reference: str) -> List[Dict]:
        """Get vostro entries by reference."""
        def filter_func(entry):
            return reference in entry.get('Reference', '') or reference in entry.get('Description', '')

        return self.find_csv_records("vostro_statement.csv", filter_func)

    def get_ledger_entries_by_reference(self, reference: str) -> List[Dict]:
        """Get internal ledger entries by reference."""
        def filter_func(entry):
            return reference in entry.get('Reference', '') or reference in entry.get('Transaction ID', '')

        return self.find_csv_records("internal_ledger.csv", filter_func)

    def create_audit_log_entry(self, log_entry: Dict) -> CSVOperationResult:
        """Create audit log entry."""
        log_entry['Timestamp'] = datetime.now().isoformat()
        log_entry['Log ID'] = f"LOG-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.load_csv('audit_log.csv'))+1:03d}"

        fieldnames = ['Log ID', 'Timestamp', 'Operation',
                      'Details', 'Status', 'User', 'System']
        return self.append_to_csv("audit_log.csv", log_entry, fieldnames)

    def _parse_balance(self, balance_str: str) -> float:
        """Parse balance string to float value."""
        if not balance_str:
            return 0.0

        # Remove currency prefixes and commas
        cleaned = balance_str.replace(',', '').replace('AUD ', '').replace(
            'USD ', '').replace('EUR ', '').replace('SGD ', '')

        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def _extract_currency_from_balance(self, balance_str: str) -> str:
        """Extract currency from balance string."""
        if 'USD' in balance_str:
            return 'USD'
        elif 'EUR' in balance_str:
            return 'EUR'
        elif 'SGD' in balance_str:
            return 'SGD'
        else:
            return 'AUD'  # Default

    def get_account_summary(self, account_number: str) -> Dict:
        """Get comprehensive account summary."""
        bank_account = self.get_account_by_number(account_number)
        customer_account = self.get_customer_by_account_number(account_number)

        summary = {
            'account_number': account_number,
            'bank_account': bank_account,
            'customer_account': customer_account,
            'nostro_entries': [],
            'vostro_entries': [],
            'ledger_entries': []
        }

        if bank_account:
            summary['nostro_entries'] = self.get_nostro_entries_by_reference(
                account_number)
            summary['vostro_entries'] = self.get_vostro_entries_by_reference(
                account_number)

        summary['ledger_entries'] = self.get_ledger_entries_by_reference(
            account_number)

        return summary

    def generate_processing_report(self, transaction_id: str) -> Dict:
        """Generate processing report for a transaction."""
        ledger_entries = self.get_ledger_entries_by_reference(transaction_id)

        if not ledger_entries:
            return {'error': f'Transaction {transaction_id} not found'}

        report = {
            'transaction_id': transaction_id,
            'processing_date': datetime.now().isoformat(),
            'ledger_entries': ledger_entries,
            'account_changes': [],
            'statement_entries': [],
            'audit_trail': []
        }

        # Get related entries
        for entry in ledger_entries:
            reference = entry.get('Reference', '')
            report['nostro_entries'] = self.get_nostro_entries_by_reference(
                reference)
            report['vostro_entries'] = self.get_vostro_entries_by_reference(
                reference)

        return report


# Global CSV operations manager instance
csv_operations_manager = CSVOperationsManager()

