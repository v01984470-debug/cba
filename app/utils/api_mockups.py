"""
API Mockup Services for Enhanced Refund Process
Provides mock implementations of external system APIs for development and testing.
"""

import json
import time
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class MockResponse:
    """Mock API response structure."""
    status_code: int
    data: Dict[str, Any]
    headers: Dict[str, str] = None
    response_time: float = 0.1


class APIMockupService:
    """Base class for API mockup services."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.response_time = random.uniform(
            0.1, 0.5)  # Simulate network latency

    def _simulate_delay(self):
        """Simulate network delay."""
        time.sleep(self.response_time)

    def _generate_mock_response(self, status_code: int, data: Dict[str, Any]) -> MockResponse:
        """Generate a mock API response."""
        self._simulate_delay()
        return MockResponse(
            status_code=status_code,
            data=data,
            headers={"Content-Type": "application/json"},
            response_time=self.response_time
        )


class SwiftIntellimatchMockup(APIMockupService):
    """Mockup for Swift Intellimatch API."""

    def __init__(self):
        super().__init__("https://mock-swift-intellimatch.cba.com")
        self.documents_db = self._initialize_documents_db()

    def _initialize_documents_db(self) -> Dict[str, Dict]:
        """Initialize mock documents database."""
        return {
            "e8b2f9c4-0e7d-4b8a-8c7c-4f5d6e7f8a9b": {
                "swift_confirmation": {
                    "sc_reference": "SC-20241201-EUR-003",
                    "nostro_account": "DEUTDEFFXXX",
                    "correspondent_bank": "DEUTSCHE BANK AG",
                    "amount": "970.00",
                    "currency": "EUR",
                    "value_date": "2024-12-01",
                    "status": "CONFIRMED"
                },
                "supporting_documents": [
                    {
                        "type": "NOSTRO_STATEMENT",
                        "reference": "NOSTRO-EUR-20241201",
                        "status": "ATTACHED",
                        "file_size": "1.8MB"
                    },
                    {
                        "type": "FX_RATE_CONFIRMATION",
                        "reference": "FX-EUR-AUD-20241201",
                        "rate": "1.6500",
                        "status": "ATTACHED"
                    }
                ]
            },
            "12345678-1234-1234-1234-123456789012": {
                "swift_confirmation": {
                    "sc_reference": "SC-20241201-USD-001",
                    "nostro_account": "CHASUS33XXX",
                    "correspondent_bank": "JPMORGAN CHASE BANK",
                    "amount": "9950.00",
                    "currency": "USD",
                    "value_date": "2024-12-01",
                    "status": "CONFIRMED"
                },
                "supporting_documents": [
                    {
                        "type": "NOSTRO_STATEMENT",
                        "reference": "NOSTRO-USD-20241201",
                        "status": "ATTACHED",
                        "file_size": "2.5MB"
                    },
                    {
                        "type": "FX_RATE_CONFIRMATION",
                        "reference": "FX-USD-AUD-20241201",
                        "rate": "1.4850",
                        "status": "ATTACHED"
                    }
                ]
            },
            "87654321-4321-4321-4321-210987654321": {
                "swift_confirmation": {
                    "sc_reference": "SC-20241201-EUR-002",
                    "nostro_account": "DEUTDEFFXXX",
                    "correspondent_bank": "DEUTSCHE BANK AG",
                    "amount": "8500.00",
                    "currency": "EUR",
                    "value_date": "2024-12-01",
                    "status": "CONFIRMED"
                },
                "supporting_documents": [
                    {
                        "type": "NOSTRO_STATEMENT",
                        "reference": "NOSTRO-EUR-20241201",
                        "status": "ATTACHED"
                    }
                ]
            },
            "a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6": {
                "swift_confirmation": {
                    "sc_reference": "SC-20250115-USD-001",
                    "nostro_account": "CHASUS33XXX",
                    "correspondent_bank": "JPMORGAN CHASE BANK",
                    "amount": "2475.00",
                    "currency": "USD",
                    "value_date": "2025-01-15",
                    "status": "CONFIRMED"
                },
                "supporting_documents": [
                    {
                        "type": "NOSTRO_STATEMENT",
                        "reference": "NOSTRO-USD-20250115",
                        "status": "ATTACHED",
                        "file_size": "2.1MB"
                    },
                    {
                        "type": "FX_RATE_CONFIRMATION",
                        "reference": "FX-USD-AUD-20250115",
                        "rate": "1.5120",
                        "status": "ATTACHED"
                    }
                ]
            },
            "b2c3d4e5-6f7g-8h9i-0j1k-l2m3n4o5p6q7": {
                "swift_confirmation": {
                    "sc_reference": "SC-20250120-GBP-001",
                    "nostro_account": "BARCGB22XXX",
                    "correspondent_bank": "BARCLAYS BANK PLC",
                    "amount": "1485.00",
                    "currency": "GBP",
                    "value_date": "2025-01-20",
                    "status": "CONFIRMED"
                },
                "supporting_documents": [
                    {
                        "type": "NOSTRO_STATEMENT",
                        "reference": "NOSTRO-GBP-20250120",
                        "status": "ATTACHED",
                        "file_size": "1.9MB"
                    },
                    {
                        "type": "FX_RATE_CONFIRMATION",
                        "reference": "FX-GBP-AUD-20250120",
                        "rate": "1.9500",
                        "status": "ATTACHED"
                    }
                ]
            },
            "c3d4e5f6-7g8h-9i0j-1k2l-m3n4o5p6q7r8": {
                "swift_confirmation": {
                    "sc_reference": "SC-20250125-JPY-001",
                    "nostro_account": "SMBCJPJTXXX",
                    "correspondent_bank": "SUMITOMO MITSUI BANKING CORPORATION",
                    "amount": "495000.00",
                    "currency": "JPY",
                    "value_date": "2025-01-25",
                    "status": "CONFIRMED"
                },
                "supporting_documents": [
                    {
                        "type": "NOSTRO_STATEMENT",
                        "reference": "NOSTRO-JPY-20250125",
                        "status": "ATTACHED",
                        "file_size": "3.2MB"
                    },
                    {
                        "type": "FX_RATE_CONFIRMATION",
                        "reference": "FX-JPY-AUD-20250125",
                        "rate": "0.0101",
                        "status": "ATTACHED"
                    }
                ]
            },
            "d4e5f6g7-8h9i-0j1k-2l3m-n4o5p6q7r8s9": {
                "swift_confirmation": {
                    "sc_reference": "SC-20250130-CHF-001",
                    "nostro_account": "UBSWCHZHXXX",
                    "correspondent_bank": "UBS SWITZERLAND AG",
                    "amount": "485.00",
                    "currency": "CHF",
                    "value_date": "2025-01-30",
                    "status": "CONFIRMED"
                },
                "supporting_documents": [
                    {
                        "type": "NOSTRO_STATEMENT",
                        "reference": "NOSTRO-CHF-20250130",
                        "status": "ATTACHED",
                        "file_size": "1.7MB"
                    },
                    {
                        "type": "FX_RATE_CONFIRMATION",
                        "reference": "FX-CHF-AUD-20250130",
                        "rate": "1.7000",
                        "status": "ATTACHED"
                    }
                ]
            }
        }

    def get_documents(self, uetr: str) -> MockResponse:
        """Get Swift Intellimatch documents for a UETR."""
        if uetr in self.documents_db:
            return self._generate_mock_response(200, {
                "success": True,
                "uetr": uetr,
                "documents": self.documents_db[uetr],
                "retrieved_at": datetime.now().isoformat()
            })
        else:
            return self._generate_mock_response(404, {
                "success": False,
                "error": "Documents not found",
                "uetr": uetr
            })

    def attach_documents(self, uetr: str, documents: Dict[str, Any]) -> MockResponse:
        """Attach documents to a UETR."""
        self.documents_db[uetr] = documents
        return self._generate_mock_response(201, {
            "success": True,
            "uetr": uetr,
            "documents_attached": len(documents),
            "attached_at": datetime.now().isoformat()
        })


class CommSeeMockup(APIMockupService):
    """Mockup for CommSee API."""

    def __init__(self):
        super().__init__("https://mock-commsee.cba.com")
        self.customers_db = self._initialize_customers_db()
        self.fca_accounts_db = self._initialize_fca_accounts_db()

    def _initialize_customers_db(self) -> Dict[str, Dict]:
        """Initialize mock customers database."""
        return {
            "ABC CORPORATION PTY LTD": {
                "customer_id": "CUST-123456789",
                "account_relationship": "PRIMARY",
                "kyc_status": "CURRENT",
                "aml_status": "CLEAR",
                "verification_date": "2024-11-01T00:00:00Z"
            },
            "XYZ TRADING PTY LTD": {
                "customer_id": "CUST-987654321",
                "account_relationship": "PRIMARY",
                "kyc_status": "CURRENT",
                "aml_status": "CLEAR",
                "verification_date": "2024-10-15T00:00:00Z"
            }
        }

    def _initialize_fca_accounts_db(self) -> Dict[str, Dict]:
        """Initialize mock FCA accounts database."""
        return {
            "ABC CORPORATION PTY LTD": {
                "USD": {
                    "account_number": "FCA-USD-123456789",
                    "account_holder": "ABC CORPORATION PTY LTD",
                    "currency": "USD",
                    "status": "ACTIVE",
                    "available_balance": "25000.00",
                    "account_type": "FOREIGN_CURRENCY_ACCOUNT"
                },
                "EUR": {
                    "account_number": "FCA-EUR-123456789",
                    "account_holder": "ABC CORPORATION PTY LTD",
                    "currency": "EUR",
                    "status": "ACTIVE",
                    "available_balance": "15000.00",
                    "account_type": "FOREIGN_CURRENCY_ACCOUNT"
                }
            },
            "XYZ TRADING PTY LTD": {
                "EUR": {
                    "account_number": "FCA-EUR-987654321",
                    "account_holder": "XYZ TRADING PTY LTD",
                    "currency": "EUR",
                    "status": "ACTIVE",
                    "available_balance": "50000.00",
                    "account_type": "FOREIGN_CURRENCY_ACCOUNT"
                }
            }
        }

    def verify_customer(self, customer_name: str) -> MockResponse:
        """Verify customer information."""
        if customer_name in self.customers_db:
            return self._generate_mock_response(200, {
                "success": True,
                "customer": self.customers_db[customer_name],
                "verified_at": datetime.now().isoformat()
            })
        else:
            return self._generate_mock_response(404, {
                "success": False,
                "error": "Customer not found",
                "customer_name": customer_name
            })

    def get_fca_account(self, customer_name: str, currency: str) -> MockResponse:
        """Get FCA account for customer and currency."""
        if customer_name in self.fca_accounts_db and currency in self.fca_accounts_db[customer_name]:
            return self._generate_mock_response(200, {
                "success": True,
                "fca_account": self.fca_accounts_db[customer_name][currency],
                "retrieved_at": datetime.now().isoformat()
            })
        else:
            return self._generate_mock_response(404, {
                "success": False,
                "error": "FCA account not found",
                "customer_name": customer_name,
                "currency": currency
            })

    def verify_account_holder_match(self, fca_account: str, original_account: str) -> MockResponse:
        """Verify account holder name match."""
        # Simulate name matching logic
        match_score = random.uniform(0.85, 1.0)
        is_match = match_score > 0.9

        return self._generate_mock_response(200, {
            "success": True,
            "account_holder_match": is_match,
            "match_score": match_score,
            "fca_account": fca_account,
            "original_account": original_account,
            "verified_at": datetime.now().isoformat()
        })

    def attach_commsee_note(self, customer_id: str, note: str) -> MockResponse:
        """Attach note in CommSee."""
        return self._generate_mock_response(201, {
            "success": True,
            "customer_id": customer_id,
            "note": note,
            "attached_at": datetime.now().isoformat()
        })


class PaymentSystemMockup(APIMockupService):
    """Mockup for Payment System API."""

    def __init__(self):
        super().__init__("https://mock-payments.cba.com")
        self.transactions_db = {}
        self.nostro_accounts_db = self._initialize_nostro_accounts_db()

    def _initialize_nostro_accounts_db(self) -> Dict[str, Dict]:
        """Initialize mock nostro accounts database."""
        return {
            "CHASUS33XXX": {
                "account_number": "CHASUS33XXX",
                "currency": "USD",
                "bank_name": "JPMORGAN CHASE BANK",
                "available_balance": "5000000.00",
                "status": "ACTIVE"
            },
            "DEUTDEFFXXX": {
                "account_number": "DEUTDEFFXXX",
                "currency": "EUR",
                "bank_name": "DEUTSCHE BANK AG",
                "available_balance": "3000000.00",
                "status": "ACTIVE"
            },
            "GB29NWBK60161331926819": {
                "account_number": "GB29NWBK60161331926819",
                "currency": "GBP",
                "bank_name": "NATWEST BANK",
                "available_balance": "2000000.00",
                "status": "ACTIVE"
            }
        }

    def verify_nostro_item(self, uetr: str, amount: str, currency: str, value_date: str) -> MockResponse:
        """Verify nostro item exists."""
        # Simulate nostro reconciliation
        found = random.choice([True, True, True, False])  # 75% success rate

        if found:
            nostro_item = {
                "nostro_reference": f"NOSTRO-{currency}-{datetime.now().strftime('%Y%m%d')}-001",
                "nostro_account": self._get_nostro_account(currency),
                "amount": amount,
                "currency": currency,
                "value_date": value_date,
                "status": "FOUND"
            }
            return self._generate_mock_response(200, {
                "success": True,
                "found": True,
                "nostro_item": nostro_item,
                "verified_at": datetime.now().isoformat()
            })
        else:
            return self._generate_mock_response(404, {
                "success": False,
                "found": False,
                "error": "Nostro item not found",
                "uetr": uetr
            })

    def process_transaction(self, transaction_data: Dict[str, Any]) -> MockResponse:
        """Process payment transaction."""
        transaction_id = f"TXN-REFUND-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        # Simulate transaction processing
        success = random.choice(
            [True, True, True, True, False])  # 80% success rate

        if success:
            transaction = {
                "transaction_id": transaction_id,
                "debit_account": transaction_data.get("debit_account"),
                "credit_account": transaction_data.get("credit_account"),
                "amount": transaction_data.get("amount"),
                "currency": transaction_data.get("currency"),
                "sndr_reference": transaction_data.get("sndr_reference"),
                "e2e_reference": transaction_data.get("e2e_reference"),
                "value_date": transaction_data.get("value_date"),
                "status": "PROCESSED",
                "timestamp": datetime.now().isoformat()
            }

            self.transactions_db[transaction_id] = transaction

            return self._generate_mock_response(201, {
                "success": True,
                "transaction": transaction,
                "processed_at": datetime.now().isoformat()
            })
        else:
            return self._generate_mock_response(500, {
                "success": False,
                "error": "Transaction processing failed",
                "transaction_id": transaction_id
            })

    def _get_nostro_account(self, currency: str) -> str:
        """Get nostro account for currency."""
        nostro_mapping = {
            "USD": "CHASUS33XXX",
            "EUR": "DEUTDEFFXXX",
            "GBP": "GB29NWBK60161331926819",
            "JPY": "JP91BKPT00000000000001",
            "CAD": "CA89370400440532013000",
            "CHF": "CHASCHZZXXX"
        }
        return nostro_mapping.get(currency, f"NOSTRO-{currency}-XXX")


class QFCaseManagementMockup(APIMockupService):
    """Mockup for QF Case Management API."""

    def __init__(self):
        super().__init__("https://mock-qf.cba.com")
        self.cases_db = {}
        self.refund_lists_db = {}

    def create_case(self, case_data: Dict[str, Any]) -> MockResponse:
        """Create new case in QF."""
        case_id = f"CASE-REFUND-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        case = {
            "case_id": case_id,
            "status": "OPEN",
            "created_date": datetime.now().isoformat(),
            "case_owner": "REFUND-TEAM-001",
            "priority": case_data.get("priority", "MEDIUM"),
            "case_data": case_data
        }

        self.cases_db[case_id] = case

        return self._generate_mock_response(201, {
            "success": True,
            "case": case,
            "created_at": datetime.now().isoformat()
        })

    def update_case(self, case_id: str, updates: Dict[str, Any]) -> MockResponse:
        """Update case in QF."""
        if case_id in self.cases_db:
            self.cases_db[case_id].update(updates)
            self.cases_db[case_id]["last_updated"] = datetime.now().isoformat()

            return self._generate_mock_response(200, {
                "success": True,
                "case": self.cases_db[case_id],
                "updated_at": datetime.now().isoformat()
            })
        else:
            return self._generate_mock_response(404, {
                "success": False,
                "error": "Case not found",
                "case_id": case_id
            })

    def close_case(self, case_id: str, closure_reason: str) -> MockResponse:
        """Close case in QF."""
        if case_id in self.cases_db:
            self.cases_db[case_id].update({
                "status": "CLOSED",
                "closure_reason": closure_reason,
                "closure_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            })

            return self._generate_mock_response(200, {
                "success": True,
                "case": self.cases_db[case_id],
                "closed_at": datetime.now().isoformat()
            })
        else:
            return self._generate_mock_response(404, {
                "success": False,
                "error": "Case not found",
                "case_id": case_id
            })

    def generate_refund_list(self, list_data: Dict[str, Any]) -> MockResponse:
        """Generate refund list."""
        list_id = f"LIST-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        refund_list = {
            "list_id": list_id,
            "list_type": list_data.get("list_type", "DAILY"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_items": list_data.get("total_items", 1),
            "total_amount": list_data.get("total_amount"),
            "currency": list_data.get("currency"),
            "recipients": list_data.get("recipients", []),
            "distribution": list_data.get("distribution", ["EMAIL"]),
            "generated_at": datetime.now().isoformat()
        }

        self.refund_lists_db[list_id] = refund_list

        return self._generate_mock_response(201, {
            "success": True,
            "refund_list": refund_list,
            "generated_at": datetime.now().isoformat()
        })

    def send_notification(self, notification_data: Dict[str, Any]) -> MockResponse:
        """Send notification to customer/branch."""
        notification_id = f"NOTIF-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        notification = {
            "notification_id": notification_id,
            "type": notification_data.get("type", "REFUND_PROCESSED"),
            "recipient": notification_data.get("recipient"),
            "message": notification_data.get("message"),
            "status": "SENT",
            "sent_at": datetime.now().isoformat()
        }

        return self._generate_mock_response(201, {
            "success": True,
            "notification": notification,
            "sent_at": datetime.now().isoformat()
        })


class NostroReconciliationMockup(APIMockupService):
    """Mockup for Nostro Reconciliation API."""

    def __init__(self):
        super().__init__("https://mock-nostro.cba.com")
        self.nostro_items_db = self._initialize_nostro_items_db()

    def _initialize_nostro_items_db(self) -> Dict[str, Dict]:
        """Initialize mock nostro items database."""
        return {
            "e8b2f9c4-0e7d-4b8a-8c7c-4f5d6e7f8a9b": {
                "nostro_reference": "NOSTRO-EUR-20241201-003",
                "nostro_account": "DEUTDEFFXXX",
                "amount": "970.00",
                "currency": "EUR",
                "value_date": "2024-12-01",
                "status": "FOUND",
                "correspondent_bank": "DEUTSCHE BANK AG"
            },
            "12345678-1234-1234-1234-123456789012": {
                "nostro_reference": "NOSTRO-USD-20241201-001",
                "nostro_account": "CHASUS33XXX",
                "amount": "9950.00",
                "currency": "USD",
                "value_date": "2024-12-01",
                "status": "FOUND",
                "correspondent_bank": "JPMORGAN CHASE BANK"
            },
            "87654321-4321-4321-4321-210987654321": {
                "nostro_reference": "NOSTRO-EUR-20241201-002",
                "nostro_account": "DEUTDEFFXXX",
                "amount": "8500.00",
                "currency": "EUR",
                "value_date": "2024-12-01",
                "status": "FOUND",
                "correspondent_bank": "DEUTSCHE BANK AG"
            },
            "a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6": {
                "nostro_reference": "NOSTRO-USD-20250115-001",
                "nostro_account": "CHASUS33XXX",
                "amount": "2475.00",
                "currency": "USD",
                "value_date": "2025-01-15",
                "status": "FOUND",
                "correspondent_bank": "JPMORGAN CHASE BANK"
            },
            "b2c3d4e5-6f7g-8h9i-0j1k-l2m3n4o5p6q7": {
                "nostro_reference": "NOSTRO-GBP-20250120-001",
                "nostro_account": "BARCGB22XXX",
                "amount": "1485.00",
                "currency": "GBP",
                "value_date": "2025-01-20",
                "status": "FOUND",
                "correspondent_bank": "BARCLAYS BANK PLC"
            },
            "c3d4e5f6-7g8h-9i0j-1k2l-m3n4o5p6q7r8": {
                "nostro_reference": "NOSTRO-JPY-20250125-001",
                "nostro_account": "SMBCJPJTXXX",
                "amount": "495000.00",
                "currency": "JPY",
                "value_date": "2025-01-25",
                "status": "FOUND",
                "correspondent_bank": "SUMITOMO MITSUI BANKING CORPORATION"
            },
            "d4e5f6g7-8h9i-0j1k-2l3m-n4o5p6q7r8s9": {
                "nostro_reference": "NOSTRO-CHF-20250130-001",
                "nostro_account": "UBSWCHZHXXX",
                "amount": "485.00",
                "currency": "CHF",
                "value_date": "2025-01-30",
                "status": "FOUND",
                "correspondent_bank": "UBS SWITZERLAND AG"
            }
        }

    def find_nostro_item(self, uetr: str, amount: str, currency: str, value_date: str) -> MockResponse:
        """Find nostro item by criteria."""
        if uetr in self.nostro_items_db:
            nostro_item = self.nostro_items_db[uetr]
            return self._generate_mock_response(200, {
                "success": True,
                "found": True,
                "nostro_item": nostro_item,
                "searched_at": datetime.now().isoformat()
            })
        else:
            return self._generate_mock_response(404, {
                "success": False,
                "found": False,
                "error": "Nostro item not found",
                "search_criteria": {
                    "uetr": uetr,
                    "amount": amount,
                    "currency": currency,
                    "value_date": value_date
                }
            })

    def escalate_to_nostro_operations(self, escalation_data: Dict[str, Any]) -> MockResponse:
        """Escalate to Nostro Operations team."""
        escalation_id = f"ESC-NOSTRO-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        escalation = {
            "escalation_id": escalation_id,
            "priority": "HIGH",
            "assigned_team": "NOSTRO_OPERATIONS",
            "escalation_data": escalation_data,
            "escalated_at": datetime.now().isoformat(),
            "resolution_required_by": (datetime.now() + timedelta(days=1)).isoformat()
        }

        return self._generate_mock_response(201, {
            "success": True,
            "escalation": escalation,
            "escalated_at": datetime.now().isoformat()
        })


# Global mockup service instances
swift_intellimatch_mockup = SwiftIntellimatchMockup()
commsee_mockup = CommSeeMockup()
payment_system_mockup = PaymentSystemMockup()
qf_case_management_mockup = QFCaseManagementMockup()
nostro_reconciliation_mockup = NostroReconciliationMockup()


def get_mockup_service(service_name: str) -> APIMockupService:
    """Get mockup service instance by name."""
    services = {
        "swift_intellimatch": swift_intellimatch_mockup,
        "commsee": commsee_mockup,
        "payment_system": payment_system_mockup,
        "qf_case_management": qf_case_management_mockup,
        "nostro_reconciliation": nostro_reconciliation_mockup
    }
    return services.get(service_name)
