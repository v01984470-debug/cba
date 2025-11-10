"""
Debit Authority Management System
Handles camt.029 and MT199 debit authority requests and responses.
"""

import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from lxml import etree


@dataclass
class DebitAuthorityRequest:
    """Debit authority request structure."""
    request_id: str
    case_id: str
    uetr: str
    creditor_agent_bic: str
    amount: float
    currency: str
    reason: str
    request_date: str
    status: str = "PENDING"


@dataclass
class DebitAuthorityResponse:
    """Debit authority response structure."""
    response_id: str
    request_id: str
    approved: bool
    response_details: str
    response_date: str
    status: str


class DebitAuthorityManager:
    """Manages debit authority requests and responses."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.requests_file = f"{data_dir}/debit_authority_requests.json"
        self.responses_file = f"{data_dir}/debit_authority_responses.json"

    def load_requests(self) -> List[Dict]:
        """Load debit authority requests from file."""
        try:
            with open(self.requests_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error loading requests: {e}")
            return []

    def save_requests(self, requests: List[Dict]):
        """Save debit authority requests to file."""
        try:
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving requests: {e}")

    def load_responses(self) -> List[Dict]:
        """Load debit authority responses from file."""
        try:
            with open(self.responses_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error loading responses: {e}")
            return []

    def save_responses(self, responses: List[Dict]):
        """Save debit authority responses to file."""
        try:
            with open(self.responses_file, 'w', encoding='utf-8') as f:
                json.dump(responses, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving responses: {e}")

    def create_camt029_request(self, return_reference: str, uetr: str, creditor_agent_bic: str,
                               amount: float, currency: str, reason: str, reason_info: str = "") -> Dict:
        """Create camt.029 debit authority request."""
        request_id = f"AUTHREQ-CBA-{datetime.now().strftime('%Y%m%d')}-{return_reference[-6:]}"

        # Create camt.029 XML structure
        camt029_xml = self._generate_camt029_xml(
            request_id, return_reference, uetr, creditor_agent_bic,
            amount, currency, reason, reason_info
        )

        request = {
            'request_id': request_id,
            'request_type': 'camt.029',
            'case_id': return_reference,
            'uetr': uetr,
            'creditor_agent_bic': creditor_agent_bic,
            'amount': amount,
            'currency': currency,
            'reason': reason,
            'reason_info': reason_info,
            'xml_content': camt029_xml,
            'request_date': datetime.now().isoformat(),
            'status': 'PENDING'
        }

        # Save to file
        requests = self.load_requests()
        requests.append(request)
        self.save_requests(requests)

        return request

    def create_mt199_request(self, return_reference: str, uetr: str, creditor_agent_bic: str,
                             amount: float, currency: str, reason: str, account_number: str = "") -> Dict:
        """Create MT199 debit authority request."""
        request_id = f"AUTHREQ-CBA-{datetime.now().strftime('%Y%m%d')}-{return_reference[-6:]}"

        # Create MT199 message structure
        mt199_content = self._generate_mt199_content(
            request_id, return_reference, uetr, creditor_agent_bic,
            amount, currency, reason, account_number
        )

        request = {
            'request_id': request_id,
            'request_type': 'MT199',
            'case_id': return_reference,
            'uetr': uetr,
            'creditor_agent_bic': creditor_agent_bic,
            'amount': amount,
            'currency': currency,
            'reason': reason,
            'account_number': account_number,
            'mt199_content': mt199_content,
            'request_date': datetime.now().isoformat(),
            'status': 'PENDING'
        }

        # Save to file
        requests = self.load_requests()
        requests.append(request)
        self.save_requests(requests)

        return request

    def process_authority_response(self, request_id: str, approved: bool,
                                   response_details: str = "", response_type: str = "camt.029") -> Dict:
        """Process debit authority response."""
        response_id = f"AUTHRESP-{datetime.now().strftime('%Y%m%d')}-{request_id[-6:]}"

        # Find the original request
        requests = self.load_requests()
        original_request = None
        for req in requests:
            if req['request_id'] == request_id:
                original_request = req
                break

        if not original_request:
            raise ValueError(f"Request {request_id} not found")

        # Create response
        if response_type == "camt.029":
            response_xml = self._generate_camt029_response(
                response_id, request_id, approved, response_details, original_request
            )
        else:  # MT199
            response_xml = self._generate_mt199_response(
                response_id, request_id, approved, response_details, original_request
            )

        response = {
            'response_id': response_id,
            'request_id': request_id,
            'approved': approved,
            'response_details': response_details,
            'response_type': response_type,
            'xml_content': response_xml,
            'response_date': datetime.now().isoformat(),
            'status': 'APPROVED' if approved else 'REJECTED'
        }

        # Save response
        responses = self.load_responses()
        responses.append(response)
        self.save_responses(responses)

        # Update request status
        for req in requests:
            if req['request_id'] == request_id:
                req['status'] = 'RESPONDED'
                req['response_id'] = response_id
                break
        self.save_requests(requests)

        return response

    def get_pending_requests(self) -> List[Dict]:
        """Get all pending debit authority requests."""
        requests = self.load_requests()
        return [req for req in requests if req['status'] == 'PENDING']

    def get_request_by_id(self, request_id: str) -> Optional[Dict]:
        """Get debit authority request by ID."""
        requests = self.load_requests()
        for req in requests:
            if req['request_id'] == request_id:
                return req
        return None

    def get_response_by_request_id(self, request_id: str) -> Optional[Dict]:
        """Get debit authority response by request ID."""
        responses = self.load_responses()
        for resp in responses:
            if resp['request_id'] == request_id:
                return resp
        return None

    def _generate_camt029_xml(self, request_id: str, case_id: str, uetr: str,
                              creditor_agent_bic: str, amount: float, currency: str,
                              reason: str, reason_info: str) -> str:
        """Generate camt.029 XML content."""
        xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.029.001.12">
    <RsltnOfInvstgtn>
        <Assgnmt>
            <Id>{request_id}</Id>
            <Assgnr>
                <Agt>
                    <FinInstnId>
                        <BICFI>CBAAUS2SXXX</BICFI>
                    </FinInstnId>
                </Agt>
            </Assgnr>
            <Assgne>
                <Agt>
                    <FinInstnId>
                        <BICFI>{creditor_agent_bic}</BICFI>
                    </FinInstnId>
                </Agt>
            </Assgne>
        </Assgnmt>
        <Case>
            <Id>{case_id}</Id>
        </Case>
        <Justfn>
            <Cd>AUTH</Cd>
        </Justfn>
        <AddtlInf>
            Please confirm if CBAAUS2SXXX is authorized to debit {currency} Nostro/Vostro account for return payment {case_id} (UETR: {uetr}) amount {currency} {amount:.2f}. Reason: {reason_info or reason}.
        </AddtlInf>
    </RsltnOfInvstgtn>
</Document>"""
        return xml_template

    def _generate_camt029_response(self, response_id: str, request_id: str, approved: bool,
                                   response_details: str, original_request: Dict) -> str:
        """Generate camt.029 response XML."""
        status = "Confirmed" if approved else "Rejected"
        creditor_bic = original_request['creditor_agent_bic']

        xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.029.001.12">
    <RsltnOfInvstgtn>
        <Assgnmt>
            <Id>{response_id}</Id>
            <Assgnr>
                <Agt>
                    <FinInstnId>
                        <BICFI>{creditor_bic}</BICFI>
                    </FinInstnId>
                </Agt>
            </Assgnr>
            <Assgne>
                <Agt>
                    <FinInstnId>
                        <BICFI>CBAAUS2SXXX</BICFI>
                    </FinInstnId>
                </Agt>
            </Assgne>
        </Assgnmt>
        <Case>
            <Id>{original_request['case_id']}</Id>
        </Case>
        <Sts>
            <Conf>{status}</Conf>
        </Sts>
        <AddtlInf>
            {response_details or (f"Debit authority {'confirmed' if approved else 'rejected'} for {original_request['currency']} Nostro/Vostro account held with {creditor_bic}. {'You may proceed with refund for ' + original_request['case_id'] if approved else 'Refund cannot proceed.'}")}
        </AddtlInf>
    </RsltnOfInvstgtn>
</Document>"""
        return xml_template

    def _generate_mt199_content(self, request_id: str, case_id: str, uetr: str,
                                creditor_agent_bic: str, amount: float, currency: str,
                                reason: str, account_number: str) -> str:
        """Generate MT199 message content."""
        mt199_template = f"""{{1:F01CBAAUS2SXXXX0000000000}}{{2:I199{creditor_agent_bic}XXXXN}}{{4:
:20:DEBITAUTHREQ{datetime.now().strftime('%Y%m%d')}
:21:{case_id}
:79:Please confirm if CBAAUS2SXXX has debit authority on {currency} Nostro account {account_number} held with {creditor_agent_bic}. This is in relation to a return payment refund to customer. Reference UETR {uetr}. Amount: {currency} {amount:.2f}. Reason: {reason}.
-}}"""
        return mt199_template

    def _generate_mt199_response(self, response_id: str, request_id: str, approved: bool,
                                 response_details: str, original_request: Dict) -> str:
        """Generate MT199 response message."""
        creditor_bic = original_request['creditor_agent_bic']
        case_id = original_request['case_id']

        if approved:
            message = f"Confirmed. CBAAUS2SXXX is authorized to debit {original_request['currency']} Nostro account held with {creditor_bic} for return payment purposes."
        else:
            message = f"Rejected. CBAAUS2SXXX is not authorized to debit {original_request['currency']} Nostro account held with {creditor_bic}."

        mt199_template = f"""{{1:F01{creditor_bic}XXXX0000000000}}{{2:I199CBAAUS2SXXXXN}}{{4:
:20:DEBITAUTHRESP{datetime.now().strftime('%Y%m%d')}
:21:{case_id}
:79:{message}
-}}"""
        return mt199_template


# Global debit authority manager instance
debit_authority_manager = DebitAuthorityManager()


def check_debit_authority(p004_data: Dict) -> Dict:
    """
    Check debit authority for Vostro account.
    Simplified implementation for testing.
    """
    try:
        # For testing purposes, simulate authority check
        # In real implementation, this would check actual authority records

        # Simple logic: approve for certain BICs, reject others
        creditor_bic = p004_data.get("cdtr_agent_bic", "")
        currency = p004_data.get("rtr_ccy", "")
        amount = float(p004_data.get("rtr_amount", 0))

        # Mock authority check - approve for common test BICs
        approved_bics = ["CHASUS33XXX", "DEUTDEFF", "BNPAFRPP", "UBSWCHZH"]

        if creditor_bic in approved_bics:
            return {
                "authorized": True,
                "reason": f"Authority confirmed for {creditor_bic}",
                "bic": creditor_bic,
                "currency": currency,
                "amount": amount
            }
        else:
            return {
                "authorized": False,
                "reason": f"No authority for {creditor_bic}",
                "bic": creditor_bic,
                "currency": currency,
                "amount": amount
            }

    except Exception as e:
        return {
            "authorized": False,
            "reason": f"Authority check failed: {str(e)}",
            "error": str(e)
        }
