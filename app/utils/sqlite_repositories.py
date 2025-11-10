"""
SQLite implementations of repository interfaces.
"""

import sqlite3
import json
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import contextmanager

from .repositories import (
    AccountRepository, StatementRepository, LedgerRepository,
    CustomerRepository, AuditRepository,
    Account, StatementEntry, LedgerEntry, Customer
)


class SQLiteAccountRepository(AccountRepository):
    """SQLite implementation of AccountRepository."""

    def __init__(self, db_path: str = "data/bank_data.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure database and tables exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    account_number TEXT PRIMARY KEY,
                    account_name TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    country TEXT NOT NULL,
                    debit_credit_authority TEXT NOT NULL,
                    reconciliation_type TEXT NOT NULL,
                    gl_code TEXT NOT NULL,
                    opening_balance TEXT NOT NULL,
                    last_reconciled_date TEXT NOT NULL,
                    cost_center TEXT NOT NULL,
                    account_status TEXT NOT NULL
                )
            ''')

    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get_account(self, account_number: str) -> Optional[Account]:
        """Get account by account number."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM accounts WHERE account_number = ?',
                (account_number,)
            )
            row = cursor.fetchone()
            if row:
                return Account(
                    account_number=row['account_number'],
                    account_name=row['account_name'],
                    account_type=row['account_type'],
                    currency=row['currency'],
                    country=row['country'],
                    debit_credit_authority=row['debit_credit_authority'],
                    reconciliation_type=row['reconciliation_type'],
                    gl_code=row['gl_code'],
                    opening_balance=row['opening_balance'],
                    last_reconciled_date=row['last_reconciled_date'],
                    cost_center=row['cost_center'],
                    account_status=row['account_status']
                )
        return None

    def get_accounts_by_type(self, account_type: str) -> List[Account]:
        """Get all accounts of a specific type."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM accounts WHERE account_type = ?',
                (account_type,)
            )
            rows = cursor.fetchall()
            return [
                Account(
                    account_number=row['account_number'],
                    account_name=row['account_name'],
                    account_type=row['account_type'],
                    currency=row['currency'],
                    country=row['country'],
                    debit_credit_authority=row['debit_credit_authority'],
                    reconciliation_type=row['reconciliation_type'],
                    gl_code=row['gl_code'],
                    opening_balance=row['opening_balance'],
                    last_reconciled_date=row['last_reconciled_date'],
                    cost_center=row['cost_center'],
                    account_status=row['account_status']
                ) for row in rows
            ]

    def get_nostro_account_for_currency(self, currency: str) -> Optional[str]:
        """Get nostro account number for a currency."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT account_number FROM accounts WHERE account_type = "Nostro" AND currency = ? LIMIT 1',
                (currency,)
            )
            row = cursor.fetchone()
            return row['account_number'] if row else None

    def update_account_balance(self, account_number: str, amount: float, operation: str) -> bool:
        """Update account balance (debit/credit)."""
        try:
            with self._get_connection() as conn:
                # Get current balance
                cursor = conn.execute(
                    'SELECT opening_balance FROM accounts WHERE account_number = ?',
                    (account_number,)
                )
                row = cursor.fetchone()
                if not row:
                    return False

                current_balance = float(row['opening_balance'])

                # Calculate new balance
                if operation.lower() == 'debit':
                    new_balance = current_balance - amount
                elif operation.lower() == 'credit':
                    new_balance = current_balance + amount
                else:
                    return False

                # Update balance
                conn.execute(
                    'UPDATE accounts SET opening_balance = ? WHERE account_number = ?',
                    (str(new_balance), account_number)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating account balance: {e}")
            return False

    def get_all_accounts(self) -> List[Account]:
        """Get all accounts."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM accounts')
            rows = cursor.fetchall()
            return [
                Account(
                    account_number=row['account_number'],
                    account_name=row['account_name'],
                    account_type=row['account_type'],
                    currency=row['currency'],
                    country=row['country'],
                    debit_credit_authority=row['debit_credit_authority'],
                    reconciliation_type=row['reconciliation_type'],
                    gl_code=row['gl_code'],
                    opening_balance=row['opening_balance'],
                    last_reconciled_date=row['last_reconciled_date'],
                    cost_center=row['cost_center'],
                    account_status=row['account_status']
                ) for row in rows
            ]


class SQLiteStatementRepository(StatementRepository):
    """SQLite implementation of StatementRepository."""

    def __init__(self, db_path: str = "data/bank_data.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure database and tables exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS nostro_statements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    statement_id TEXT NOT NULL,
                    value_date TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    dr_cr TEXT NOT NULL,
                    description TEXT NOT NULL,
                    reference TEXT NOT NULL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS vostro_statements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    statement_id TEXT NOT NULL,
                    value_date TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    dr_cr TEXT NOT NULL,
                    description TEXT NOT NULL,
                    reference TEXT NOT NULL
                )
            ''')

    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get_nostro_entries(self) -> List[StatementEntry]:
        """Get all nostro statement entries."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM nostro_statements')
            rows = cursor.fetchall()
            return [
                StatementEntry(
                    statement_id=row['statement_id'],
                    value_date=row['value_date'],
                    currency=row['currency'],
                    amount=row['amount'],
                    dr_cr=row['dr_cr'],
                    description=row['description'],
                    reference=row['reference']
                ) for row in rows
            ]

    def get_vostro_entries(self) -> List[StatementEntry]:
        """Get all vostro statement entries."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM vostro_statements')
            rows = cursor.fetchall()
            return [
                StatementEntry(
                    statement_id=row['statement_id'],
                    value_date=row['value_date'],
                    currency=row['currency'],
                    amount=row['amount'],
                    dr_cr=row['dr_cr'],
                    description=row['description'],
                    reference=row['reference']
                ) for row in rows
            ]

    def find_nostro_match(self, reference: str, uetr: str, amount: float, currency: str) -> Dict[str, Any]:
        """Find matching nostro entry (exact or partial)."""
        with self._get_connection() as conn:
            # Try exact match first
            cursor = conn.execute(
                'SELECT * FROM nostro_statements WHERE reference = ? AND amount = ? AND currency = ?',
                (reference, str(amount), currency)
            )
            row = cursor.fetchone()

            if row:
                return {
                    'found': True,
                    'match_type': 'exact',
                    'nostro_entry': StatementEntry(
                        statement_id=row['statement_id'],
                        value_date=row['value_date'],
                        currency=row['currency'],
                        amount=row['amount'],
                        dr_cr=row['dr_cr'],
                        description=row['description'],
                        reference=row['reference']
                    )
                }

            # Try partial match by UETR
            cursor = conn.execute(
                'SELECT * FROM nostro_statements WHERE reference LIKE ? AND currency = ?',
                (f'%{uetr}%', currency)
            )
            row = cursor.fetchone()

            if row:
                return {
                    'found': True,
                    'match_type': 'partial',
                    'nostro_entry': StatementEntry(
                        statement_id=row['statement_id'],
                        value_date=row['value_date'],
                        currency=row['currency'],
                        amount=row['amount'],
                        dr_cr=row['dr_cr'],
                        description=row['description'],
                        reference=row['reference']
                    )
                }

            return {'found': False, 'match_type': 'none', 'nostro_entry': None}

    def add_nostro_entry(self, entry: StatementEntry) -> bool:
        """Add new nostro statement entry."""
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    INSERT INTO nostro_statements 
                    (statement_id, value_date, currency, amount, dr_cr, description, reference)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.statement_id, entry.value_date, entry.currency,
                    entry.amount, entry.dr_cr, entry.description, entry.reference
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding nostro entry: {e}")
            return False

    def add_vostro_entry(self, entry: StatementEntry) -> bool:
        """Add new vostro statement entry."""
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    INSERT INTO vostro_statements 
                    (statement_id, value_date, currency, amount, dr_cr, description, reference)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.statement_id, entry.value_date, entry.currency,
                    entry.amount, entry.dr_cr, entry.description, entry.reference
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding vostro entry: {e}")
            return False


class SQLiteLedgerRepository(LedgerRepository):
    """SQLite implementation of LedgerRepository."""

    def __init__(self, db_path: str = "data/bank_data.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure database and tables exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS ledger_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT NOT NULL,
                    value_date TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    counterparty TEXT NOT NULL,
                    reference TEXT NOT NULL,
                    return_reason TEXT NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
            ''')

    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get_ledger_entries(self) -> List[LedgerEntry]:
        """Get all ledger entries."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM ledger_entries')
            rows = cursor.fetchall()
            return [
                LedgerEntry(
                    transaction_id=row['transaction_id'],
                    value_date=row['value_date'],
                    currency=row['currency'],
                    amount=row['amount'],
                    counterparty=row['counterparty'],
                    reference=row['reference'],
                    return_reason=row['return_reason']
                ) for row in rows
            ]

    def get_entry_by_reference(self, reference: str) -> Optional[LedgerEntry]:
        """Get ledger entry by reference."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM ledger_entries WHERE reference = ?',
                (reference,)
            )
            row = cursor.fetchone()
            if row:
                return LedgerEntry(
                    transaction_id=row['transaction_id'],
                    value_date=row['value_date'],
                    currency=row['currency'],
                    amount=row['amount'],
                    counterparty=row['counterparty'],
                    reference=row['reference'],
                    return_reason=row['return_reason']
                )
        return None

    def add_ledger_entry(self, entry: LedgerEntry) -> bool:
        """Add new ledger entry."""
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    INSERT INTO ledger_entries 
                    (transaction_id, value_date, currency, amount, counterparty, reference, return_reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.transaction_id, entry.value_date, entry.currency,
                    entry.amount, entry.counterparty, entry.reference, entry.return_reason
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding ledger entry: {e}")
            return False

    def update_entry_status(self, reference: str, status: str) -> bool:
        """Update entry status."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    'UPDATE ledger_entries SET status = ? WHERE reference = ?',
                    (status, reference)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating entry status: {e}")
            return False


class SQLiteCustomerRepository(CustomerRepository):
    """SQLite implementation of CustomerRepository."""

    def __init__(self, db_path: str = "data/bank_data.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure database and tables exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    account_name TEXT NOT NULL,
                    account_number TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    ledger_balance TEXT NOT NULL,
                    available_balance TEXT NOT NULL,
                    account_status TEXT NOT NULL,
                    email TEXT NOT NULL
                )
            ''')

    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get_customer_by_account(self, account_number: str) -> Optional[Customer]:
        """Get customer by account number."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM customers WHERE account_number = ?',
                (account_number,)
            )
            row = cursor.fetchone()
            if row:
                return Customer(
                    customer_name=row['customer_name'],
                    account_name=row['account_name'],
                    account_number=row['account_number'],
                    account_type=row['account_type'],
                    ledger_balance=row['ledger_balance'],
                    available_balance=row['available_balance'],
                    account_status=row['account_status'],
                    email=row['email']
                )
        return None

    def get_customer_by_iban(self, iban: str) -> Optional[Customer]:
        """Get customer by IBAN."""
        # For now, treat IBAN same as account number
        return self.get_customer_by_account(iban)

    def get_all_customers(self) -> List[Customer]:
        """Get all customers."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM customers')
            rows = cursor.fetchall()
            return [
                Customer(
                    customer_name=row['customer_name'],
                    account_name=row['account_name'],
                    account_number=row['account_number'],
                    account_type=row['account_type'],
                    ledger_balance=row['ledger_balance'],
                    available_balance=row['available_balance'],
                    account_status=row['account_status'],
                    email=row['email']
                ) for row in rows
            ]

    def suggest_alternate_account(self, original_account: str) -> Optional[str]:
        """Suggest alternate active account for customer."""
        with self._get_connection() as conn:
            # Get customer info from original account
            cursor = conn.execute(
                'SELECT customer_name FROM customers WHERE account_number = ?',
                (original_account,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            customer_name = row['customer_name']

            # Find another active account for the same customer
            cursor = conn.execute(
                'SELECT account_number FROM customers WHERE customer_name = ? AND account_number != ? AND account_status = "Active" LIMIT 1',
                (customer_name, original_account)
            )
            row = cursor.fetchone()
            return row['account_number'] if row else None


class SQLiteAuditRepository(AuditRepository):
    """SQLite implementation of AuditRepository."""

    def __init__(self, db_path: str = "data/bank_data.db", reports_dir: str = "csv_reports"):
        self.db_path = db_path
        self.reports_dir = reports_dir
        self._ensure_db_exists()
        os.makedirs(reports_dir, exist_ok=True)

    def _ensure_db_exists(self):
        """Ensure database and tables exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT,
                    event_type TEXT NOT NULL,
                    event_data TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    details TEXT
                )
            ''')

    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def add_audit_event(self, event: Dict[str, Any]) -> bool:
        """Add audit event."""
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    INSERT INTO audit_events 
                    (transaction_id, event_type, event_data, timestamp, user_id, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    event.get('transaction_id'),
                    event.get('event_type', 'unknown'),
                    json.dumps(event.get('event_data', {})),
                    event.get('timestamp', datetime.now().isoformat()),
                    str(event.get('user_id', 'system')),
                    str(event.get('details', ''))
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding audit event: {e}")
            return False

    def get_audit_events(self, transaction_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit events, optionally filtered by transaction ID."""
        with self._get_connection() as conn:
            if transaction_id:
                cursor = conn.execute(
                    'SELECT * FROM audit_events WHERE transaction_id = ? ORDER BY timestamp',
                    (transaction_id,)
                )
            else:
                cursor = conn.execute(
                    'SELECT * FROM audit_events ORDER BY timestamp')

            rows = cursor.fetchall()
            return [
                {
                    'id': row['id'],
                    'transaction_id': row['transaction_id'],
                    'event_type': row['event_type'],
                    'event_data': json.loads(row['event_data']) if row['event_data'] else {},
                    'timestamp': row['timestamp'],
                    'user_id': row['user_id'],
                    'details': row['details']
                } for row in rows
            ]

    def save_run_report(self, run_id: str, report_data: Dict[str, Any]) -> str:
        """Save run report and return file path."""
        try:
            file_path = os.path.join(self.reports_dir, f"{run_id}.json")
            temp_file_path = file_path + ".tmp"

            # Write to temporary file first to avoid corruption
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2,
                          ensure_ascii=False, default=str)

            # Atomic move to final location
            import shutil
            shutil.move(temp_file_path, file_path)

            print(f"Successfully saved run report: {file_path}")
            return file_path
        except Exception as e:
            print(f"Error saving run report: {e}")
            # Clean up temp file if it exists
            temp_file_path = os.path.join(
                self.reports_dir, f"{run_id}.json.tmp")
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
            return ""

    def get_run_report(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run report by ID."""
        try:
            file_path = os.path.join(self.reports_dir, f"{run_id}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading run report: {e}")
        return None

    def record_balance_change(self, transaction_id: str, account_number: str,
                              operation: str, amount: float, currency: str,
                              balance_before: str, balance_after: str,
                              reference: str = "", description: str = "") -> bool:
        """Record balance change in audit log."""
        event = {
            'transaction_id': transaction_id,
            'event_type': 'balance_change',
            'event_data': {
                'account_number': account_number,
                'operation': operation,
                'amount': amount,
                'currency': currency,
                'balance_before': balance_before,
                'balance_after': balance_after,
                'reference': reference,
                'description': description
            },
            'timestamp': datetime.now().isoformat(),
            'user_id': 'system',
            'details': f"Account {account_number} {operation} {amount} {currency}"
        }
        return self.add_audit_event(event)


# Factory function to create repository instances
def create_repositories(db_path: str = "data/bank_data.db", reports_dir: str = "csv_reports"):
    """Create SQLite repository instances."""
    return {
        'accounts': SQLiteAccountRepository(db_path),
        'statements': SQLiteStatementRepository(db_path),
        'ledger': SQLiteLedgerRepository(db_path),
        'customers': SQLiteCustomerRepository(db_path),
        'audit': SQLiteAuditRepository(db_path, reports_dir)
    }
