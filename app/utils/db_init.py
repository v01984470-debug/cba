"""
Database initialization script for SQLite migration.
"""

import sqlite3
import os
import csv
from typing import Dict, List, Any


def init_database(db_path: str = "data/bank_data.db"):
    """Initialize the SQLite database with all required tables."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        # Create accounts table
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

        # Create nostro_statements table
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

        # Create vostro_statements table
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

        # Create ledger_entries table
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

        # Create customers table
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

        # Create audit_events table
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

        conn.commit()
        print(f"Database initialized at {db_path}")


def migrate_csv_to_sqlite(csv_dir: str = "data", db_path: str = "data/bank_data.db"):
    """Migrate data from CSV files to SQLite database."""

    # Initialize database
    init_database(db_path)

    with sqlite3.connect(db_path) as conn:
        # Migrate bank_accounts.csv
        accounts_file = os.path.join(csv_dir, "bank_accounts.csv")
        if os.path.exists(accounts_file):
            print(f"Migrating {accounts_file}...")
            with open(accounts_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    conn.execute('''
                        INSERT OR REPLACE INTO accounts 
                        (account_number, account_name, account_type, currency, country,
                         debit_credit_authority, reconciliation_type, gl_code, opening_balance,
                         last_reconciled_date, cost_center, account_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('Account Number', ''),
                        row.get('Account Name', ''),
                        row.get('Account Type', ''),
                        row.get('Currency', ''),
                        row.get('Country', ''),
                        row.get('Debit/Credit Authority', ''),
                        row.get('Reconciliation Type', ''),
                        row.get('GL Code', ''),
                        row.get('Opening Balance', ''),
                        row.get('Last Reconciled Date', ''),
                        row.get('Cost Center', ''),
                        row.get('Account Status', '')
                    ))
            print(f"Migrated {accounts_file}")

        # Migrate nostro_statement.csv
        nostro_file = os.path.join(csv_dir, "nostro_statement.csv")
        if os.path.exists(nostro_file):
            print(f"Migrating {nostro_file}...")
            with open(nostro_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    conn.execute('''
                        INSERT INTO nostro_statements 
                        (statement_id, value_date, currency, amount, dr_cr, description, reference)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('Statement ID', ''),
                        row.get('Value Date', ''),
                        row.get('Currency', ''),
                        row.get('Amount', ''),
                        row.get('DR / CR', ''),
                        row.get('Description', ''),
                        row.get('Reference', '')
                    ))
            print(f"Migrated {nostro_file}")

        # Migrate vostro_statement.csv
        vostro_file = os.path.join(csv_dir, "vostro_statement.csv")
        if os.path.exists(vostro_file):
            print(f"Migrating {vostro_file}...")
            with open(vostro_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    conn.execute('''
                        INSERT INTO vostro_statements 
                        (statement_id, value_date, currency, amount, dr_cr, description, reference)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('Statement ID', ''),
                        row.get('Value Date', ''),
                        row.get('Currency', ''),
                        row.get('Amount', ''),
                        row.get('DR / CR', ''),
                        row.get('Description', ''),
                        row.get('Reference', '')
                    ))
            print(f"Migrated {vostro_file}")

        # Migrate internal_ledger.csv
        ledger_file = os.path.join(csv_dir, "internal_ledger.csv")
        if os.path.exists(ledger_file):
            print(f"Migrating {ledger_file}...")
            with open(ledger_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    conn.execute('''
                        INSERT INTO ledger_entries 
                        (transaction_id, value_date, currency, amount, counterparty, reference, return_reason)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('Transaction ID', ''),
                        row.get('Value Date', ''),
                        row.get('Currency', ''),
                        row.get('Amount', ''),
                        row.get('Counterparty', ''),
                        row.get('Reference', ''),
                        row.get('Return Reason', '')
                    ))
            print(f"Migrated {ledger_file}")

        # Migrate customer_data.csv
        customers_file = os.path.join(csv_dir, "customer_data.csv")
        if os.path.exists(customers_file):
            print(f"Migrating {customers_file}...")
            with open(customers_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    conn.execute('''
                        INSERT INTO customers 
                        (customer_name, account_name, account_number, account_type,
                         ledger_balance, available_balance, account_status, email)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('Customer Name', ''),
                        row.get('Account Name', ''),
                        row.get('Account Number', ''),
                        row.get('Account Type', ''),
                        row.get('Ledger Balance', ''),
                        row.get('Available Balance', ''),
                        row.get('Account Status', ''),
                        row.get('e-mail', '')
                    ))
            print(f"Migrated {customers_file}")

        # Migrate audit_log.csv if it exists
        audit_file = os.path.join(csv_dir, "audit_log.csv")
        if os.path.exists(audit_file):
            print(f"Migrating {audit_file}...")
            with open(audit_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    conn.execute('''
                        INSERT INTO audit_events 
                        (transaction_id, event_type, event_data, timestamp, user_id, details)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('Transaction ID', ''),
                        row.get('Event Type', ''),
                        row.get('Event Data', '{}'),
                        row.get('Timestamp', ''),
                        row.get('User ID', ''),
                        row.get('Details', '')
                    ))
            print(f"Migrated {audit_file}")

        conn.commit()
        print("Migration completed successfully!")


def verify_migration(db_path: str = "data/bank_data.db"):
    """Verify that the migration was successful by counting records."""
    with sqlite3.connect(db_path) as conn:
        tables = ['accounts', 'nostro_statements', 'vostro_statements',
                  'ledger_entries', 'customers', 'audit_events']

        print("\nMigration Verification:")
        print("=" * 40)

        for table in tables:
            cursor = conn.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f"{table}: {count} records")

        print("=" * 40)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "migrate":
        migrate_csv_to_sqlite()
        verify_migration()
    else:
        init_database()
        print("Database initialized. Run with 'migrate' argument to migrate CSV data.")
