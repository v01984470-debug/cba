"""
Repository interfaces for data access layer.
Abstract interfaces that can be implemented with CSV, SQLite, or other backends.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Account:
    """Bank account data structure."""
    account_number: str
    account_name: str
    account_type: str
    currency: str
    country: str
    debit_credit_authority: str
    reconciliation_type: str
    gl_code: str
    opening_balance: str
    last_reconciled_date: str
    cost_center: str
    account_status: str


@dataclass
class StatementEntry:
    """Statement entry data structure."""
    statement_id: str
    value_date: str
    currency: str
    amount: str
    dr_cr: str
    description: str
    reference: str


@dataclass
class LedgerEntry:
    """Internal ledger entry data structure."""
    transaction_id: str
    value_date: str
    currency: str
    amount: str
    counterparty: str
    reference: str
    return_reason: str


@dataclass
class Customer:
    """Customer data structure."""
    customer_name: str
    account_name: str
    account_number: str
    account_type: str
    ledger_balance: str
    available_balance: str
    account_status: str
    email: str


class AccountRepository(ABC):
    """Abstract interface for bank account operations."""

    @abstractmethod
    def get_account(self, account_number: str) -> Optional[Account]:
        """Get account by account number."""
        pass

    @abstractmethod
    def get_accounts_by_type(self, account_type: str) -> List[Account]:
        """Get all accounts of a specific type."""
        pass

    @abstractmethod
    def get_nostro_account_for_currency(self, currency: str) -> Optional[str]:
        """Get nostro account number for a currency."""
        pass

    @abstractmethod
    def update_account_balance(self, account_number: str, amount: float, operation: str) -> bool:
        """Update account balance (debit/credit)."""
        pass

    @abstractmethod
    def get_all_accounts(self) -> List[Account]:
        """Get all accounts."""
        pass


class StatementRepository(ABC):
    """Abstract interface for statement operations."""

    @abstractmethod
    def get_nostro_entries(self) -> List[StatementEntry]:
        """Get all nostro statement entries."""
        pass

    @abstractmethod
    def get_vostro_entries(self) -> List[StatementEntry]:
        """Get all vostro statement entries."""
        pass

    @abstractmethod
    def find_nostro_match(self, reference: str, uetr: str, amount: float, currency: str) -> Dict[str, Any]:
        """Find matching nostro entry (exact or partial)."""
        pass

    @abstractmethod
    def add_nostro_entry(self, entry: StatementEntry) -> bool:
        """Add new nostro statement entry."""
        pass

    @abstractmethod
    def add_vostro_entry(self, entry: StatementEntry) -> bool:
        """Add new vostro statement entry."""
        pass


class LedgerRepository(ABC):
    """Abstract interface for internal ledger operations."""

    @abstractmethod
    def get_ledger_entries(self) -> List[LedgerEntry]:
        """Get all ledger entries."""
        pass

    @abstractmethod
    def get_entry_by_reference(self, reference: str) -> Optional[LedgerEntry]:
        """Get ledger entry by reference."""
        pass

    @abstractmethod
    def add_ledger_entry(self, entry: LedgerEntry) -> bool:
        """Add new ledger entry."""
        pass

    @abstractmethod
    def update_entry_status(self, reference: str, status: str) -> bool:
        """Update entry status."""
        pass


class CustomerRepository(ABC):
    """Abstract interface for customer operations."""

    @abstractmethod
    def get_customer_by_account(self, account_number: str) -> Optional[Customer]:
        """Get customer by account number."""
        pass

    @abstractmethod
    def get_customer_by_iban(self, iban: str) -> Optional[Customer]:
        """Get customer by IBAN."""
        pass

    @abstractmethod
    def get_all_customers(self) -> List[Customer]:
        """Get all customers."""
        pass

    @abstractmethod
    def suggest_alternate_account(self, original_account: str) -> Optional[str]:
        """Suggest alternate active account for customer."""
        pass


class AuditRepository(ABC):
    """Abstract interface for audit operations."""

    @abstractmethod
    def add_audit_event(self, event: Dict[str, Any]) -> bool:
        """Add audit event."""
        pass

    @abstractmethod
    def get_audit_events(self, transaction_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit events, optionally filtered by transaction ID."""
        pass

    @abstractmethod
    def save_run_report(self, run_id: str, report_data: Dict[str, Any]) -> str:
        """Save run report and return file path."""
        pass

    @abstractmethod
    def get_run_report(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run report by ID."""
        pass


