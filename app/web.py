from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from flask_cors import CORS
import io
import os
import json
import uuid
import pathlib
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any
from app.graph import build_graph
from app.utils.csv_repositories import create_repositories
from app.agents.loggerAg import run_prep_logger

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Use csv_reports directory instead of runs
REPORTS_DIR = pathlib.Path("csv_reports")
REPORTS_DIR.mkdir(exist_ok=True)

# Use cases directory for storing generated cases
CASES_DIR = pathlib.Path("cases")
CASES_DIR.mkdir(exist_ok=True)

# Case mapping for test scenarios
CASE_SCENARIOS = {
    "CASE-001-MATCHED-NOSTRO": ("test_scenario_1_matched_nostro.xml", "test_scenario_1_matched_nostro_pacs008.xml"),
    "CASE-002-FCA-REFUND": ("test_scenario_2_fca_refund.xml", "test_scenario_2_fca_refund_pacs008.xml"),
    "CASE-003-AUD-MANUAL": ("test_scenario_3_aud_payment.xml", "test_scenario_3_aud_payment_pacs008.xml"),
    "CASE-004-HIGH-FX": ("test_scenario_4_high_fx_loss.xml", "test_scenario_4_high_fx_loss_pacs008.xml"),
    "CASE-005-UNMATCHED": ("test_scenario_5_unmatched_nostro.xml", "test_scenario_5_unmatched_nostro_pacs008.xml"),
    "CASE-006-LOW-FX": ("test_scenario_6_low_fx_loss.xml", "test_scenario_6_low_fx_loss_pacs008.xml"),
    "CASE-007-HIGH-NO-FCA": ("test_scenario_7_high_fx_no_fca.xml", "test_scenario_7_high_fx_no_fca_pacs008.xml"),
    "CASE-008-HIGH-WITH-FCA": ("test_scenario_8_high_fx_with_fca.xml", "test_scenario_8_high_fx_with_fca_pacs008.xml"),
}


def invoke_graph(pacs004_text: str, pacs008_text: str, fx_loss_aud: float, non_branch: bool, sanctions: bool, case_id: str = None):
    """Invoke the graph pipeline with the new agent-based workflow."""
    graph = build_graph()
    return graph.invoke({
        "pacs004_xml": pacs004_text,
        "pacs008_xml": pacs008_text,
        "fx_loss_aud": fx_loss_aud,
        "non_branch": non_branch,
        "sanctions": sanctions,
        "case_id": case_id,
    })


def load_run(run_id: str):
    """Load run report from csv_reports directory."""
    p = REPORTS_DIR / f"{run_id}.json"
    if not p.exists():
        return None

    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as e:
        print(f"Warning: Corrupted JSON file {p}: {e}")
        # Try to find a backup or return None
        return None
    except Exception as e:
        print(f"Error reading file {p}: {e}")
        return None


def parse_pacs_xml(xml_content: str, message_type: str):
    """Parse PACS XML and extract relevant information."""
    try:
        root = ET.fromstring(xml_content)

        # Common namespace handling - try multiple namespace versions
        if message_type == 'pacs004':
            # Try different PACS004 namespace versions
            ns_versions = [
                'urn:iso:std:iso:20022:tech:xsd:pacs.004.001.09',
                'urn:iso:std:iso:20022:tech:xsd:pacs.004.001.08',
                'urn:iso:std:iso:20022:tech:xsd:pacs.004.001.07'
            ]
        else:
            # Try different PACS008 namespace versions
            ns_versions = [
                'urn:iso:std:iso:20022:tech:xsd:pacs.008.001.12',
                'urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08',
                'urn:iso:std:iso:20022:tech:xsd:pacs.008.001.07'
            ]

        # Find working namespace by trying to find a common element
        namespaces = None
        for ns_version in ns_versions:
            test_ns = {'ns': ns_version}
            test_elem = root.find(
                './/ns:MsgId', test_ns) if message_type == 'pacs004' else root.find('.//ns:MsgId', test_ns)
            if test_elem is not None:
                namespaces = test_ns
                break

        # Fallback to default if no namespace found
        if namespaces is None:
            namespaces = {
                'ns': 'urn:iso:std:iso:20022:tech:xsd:pacs.004.001.08' if message_type == 'pacs004' else 'urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08'
            }

        data = {}

        if message_type == 'pacs004':
            # Parse PACS.004 (Payment Return)
            data['message_id'] = root.find(
                './/ns:MsgId', namespaces).text if root.find('.//ns:MsgId', namespaces) is not None else None
            data['transaction_id'] = root.find(
                './/ns:RtrId', namespaces).text if root.find('.//ns:RtrId', namespaces) is not None else None
            data['return_reason'] = root.find(
                './/ns:Cd', namespaces).text if root.find('.//ns:Cd', namespaces) is not None else None

            # Extract UETR and E2E ID from original transaction reference
            uetr_elem = root.find('.//ns:OrgnlUETR', namespaces)
            data['uetr'] = uetr_elem.text if uetr_elem is not None and uetr_elem.text else None
            if not data['uetr']:
                # Fallback to OrgnlTxId if UETR not found
                txid_elem = root.find('.//ns:OrgnlTxId', namespaces)
                data['uetr'] = txid_elem.text if txid_elem is not None and txid_elem.text else None

            e2e_elem = root.find('.//ns:OrgnlEndToEndId', namespaces)
            data['e2e'] = e2e_elem.text if e2e_elem is not None and e2e_elem.text else None

            # Amount and currency - PACS.004 uses RtrdIntrBkSttlmAmt
            amt_elem = root.find('.//ns:RtrdIntrBkSttlmAmt', namespaces)
            if amt_elem is not None:
                data['amount'] = amt_elem.text
                data['currency'] = amt_elem.get('Ccy', 'USD')
            else:
                # Fallback to original transaction amount
                amt_elem = root.find('.//ns:Amt', namespaces)
                if amt_elem is not None:
                    data['amount'] = amt_elem.text
                    data['currency'] = amt_elem.get('Ccy', 'USD')

            # Customer information from original transaction reference
            debtor_elem = root.find('.//ns:OrgnlTxRef/ns:Dbtr', namespaces)
            if debtor_elem is not None:
                data['debtor_name'] = debtor_elem.find(
                    './/ns:Nm', namespaces).text if debtor_elem.find('.//ns:Nm', namespaces) is not None else None
                # Get account from DbtrAcct
                acct_elem = root.find(
                    './/ns:OrgnlTxRef/ns:DbtrAcct/ns:Id/ns:IBAN', namespaces)
                if acct_elem is not None:
                    data['debtor_account'] = acct_elem.text
                else:
                    # Fallback to other ID types
                    id_elem = root.find(
                        './/ns:OrgnlTxRef/ns:Dbtr/ns:Id/ns:OrgId/ns:Othr/ns:Id', namespaces)
                    if id_elem is not None:
                        data['debtor_account'] = id_elem.text

        elif message_type == 'pacs008':
            # Parse PACS.008 (FI to FI Customer Credit Transfer)
            data['message_id'] = root.find(
                './/ns:MsgId', namespaces).text if root.find('.//ns:MsgId', namespaces) is not None else None
            data['transaction_id'] = root.find(
                './/ns:TxId', namespaces).text if root.find('.//ns:TxId', namespaces) is not None else None

            # Extract UETR and E2E ID from PmtId
            uetr_elem = root.find('.//ns:PmtId/ns:UETR', namespaces)
            data['uetr'] = uetr_elem.text if uetr_elem is not None and uetr_elem.text else None
            if not data['uetr']:
                # Fallback to TxId if UETR not found
                txid_elem = root.find('.//ns:PmtId/ns:TxId', namespaces)
                data['uetr'] = txid_elem.text if txid_elem is not None and txid_elem.text else None

            e2e_elem = root.find('.//ns:PmtId/ns:EndToEndId', namespaces)
            data['e2e'] = e2e_elem.text if e2e_elem is not None and e2e_elem.text else None

            # Amount and currency
            amt_elem = root.find('.//ns:IntrBkSttlmAmt', namespaces)
            if amt_elem is not None:
                data['amount'] = amt_elem.text
                data['currency'] = amt_elem.get('Ccy', 'USD')

            # Customer information
            debtor_elem = root.find('.//ns:Dbtr', namespaces)
            if debtor_elem is not None:
                data['debtor_name'] = debtor_elem.find(
                    './/ns:Nm', namespaces).text if debtor_elem.find('.//ns:Nm', namespaces) is not None else None
                data['debtor_account'] = debtor_elem.find(
                    './/ns:Id', namespaces).text if debtor_elem.find('.//ns:Id', namespaces) is not None else None

            creditor_elem = root.find('.//ns:Cdtr', namespaces)
            if creditor_elem is not None:
                data['creditor_name'] = creditor_elem.find(
                    './/ns:Nm', namespaces).text if creditor_elem.find('.//ns:Nm', namespaces) is not None else None
                data['creditor_account'] = creditor_elem.find(
                    './/ns:Id', namespaces).text if creditor_elem.find('.//ns:Id', namespaces) is not None else None

        return data

    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        return {}
    except Exception as e:
        print(f"Error parsing PACS XML: {e}")
        return {}


def get_transaction_reference(pacs004_data: dict, pacs008_data: dict):
    """Extract transaction reference (UETR or E2E ID) from PACS data."""
    # Extract transaction identifiers from both messages
    # Handle both string and None values
    p004_uetr = (pacs004_data.get('uetr') or '').strip(
    ) if pacs004_data.get('uetr') else ''
    p008_uetr = (pacs008_data.get('uetr') or '').strip(
    ) if pacs008_data.get('uetr') else ''
    p004_e2e = (pacs004_data.get('e2e') or '').strip(
    ) if pacs004_data.get('e2e') else ''
    p008_e2e = (pacs008_data.get('e2e') or '').strip(
    ) if pacs008_data.get('e2e') else ''

    # Use UETR if available, otherwise use E2E ID
    transaction_ref = p004_uetr or p008_uetr or p004_e2e or p008_e2e

    return transaction_ref if transaction_ref else None


def check_for_duplicate_case(pacs004_data: dict, pacs008_data: dict, case_id: str = None):
    """Check if a case already exists based on transaction reference or case ID."""
    # Get transaction reference from PACS data
    transaction_ref = get_transaction_reference(pacs004_data, pacs008_data)

    # Debug logging
    print(
        f"DEBUG duplicate check - transaction_ref: {repr(transaction_ref)}, case_id: {case_id}")
    print(
        f"DEBUG - PACS004 uetr: {repr(pacs004_data.get('uetr'))}, e2e: {repr(pacs004_data.get('e2e'))}")
    print(
        f"DEBUG - PACS008 uetr: {repr(pacs008_data.get('uetr'))}, e2e: {repr(pacs008_data.get('e2e'))}")

    # If no transaction reference and no case ID provided, can't check
    if not transaction_ref and not case_id:
        print(f"DEBUG: No transaction reference or case ID found, skipping duplicate check")
        return {'is_duplicate': False}

    # Check all existing case files
    for case_file in CASES_DIR.glob("*.json"):
        try:
            with open(case_file, 'r', encoding='utf-8') as f:
                case_data = json.load(f)

            existing_case_id = case_data.get('case_id', '')

            # Check if case ID already exists
            if case_id and existing_case_id == case_id:
                return {
                    'is_duplicate': True,
                    'reason': 'case_id',
                    'existing_case_id': existing_case_id,
                    'existing_status': case_data.get('status'),
                    'existing_created_at': case_data.get('created_at')
                }

            # Check if transaction reference already exists
            if transaction_ref:
                existing_pacs004 = case_data.get('pacs004_data', {})
                existing_pacs008 = case_data.get('pacs008_data', {})
                existing_transaction_ref = get_transaction_reference(
                    existing_pacs004, existing_pacs008)

                print(
                    f"DEBUG comparing - existing_ref: {repr(existing_transaction_ref)}, new_ref: {repr(transaction_ref)}")

                # Normalize both references for comparison (strip whitespace, case-insensitive)
                if existing_transaction_ref and transaction_ref:
                    if existing_transaction_ref.strip().lower() == transaction_ref.strip().lower():
                        print(
                            f"DEBUG: DUPLICATE FOUND - transaction reference matches: {transaction_ref}")
                        return {
                            'is_duplicate': True,
                            'reason': 'transaction_ref',
                            'existing_case_id': existing_case_id,
                            'existing_status': case_data.get('status'),
                            'existing_created_at': case_data.get('created_at')
                        }
        except Exception as e:
            print(f"Error checking case file {case_file}: {e}")
            continue

    return {'is_duplicate': False}


def generate_case_id(pacs004_data: dict, pacs008_data: dict):
    """Generate a unique case ID based on PACS data."""
    # Create a unique identifier based on transaction data
    transaction_id = pacs004_data.get(
        'transaction_id') or pacs008_data.get('transaction_id')
    amount = pacs004_data.get('rtr_amount') or pacs008_data.get('amount', '0')
    currency = pacs004_data.get(
        'rtr_ccy') or pacs008_data.get('ccy', 'USD')

    # Generate timestamp-based suffix
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Create case ID
    case_id = f"CASE-{timestamp}-{currency}{amount}-{uuid.uuid4().hex[:8].upper()}"

    return case_id


def generate_email_content(pacs004_data: dict, pacs008_data: dict, case_id: str, pacs004_content: str = None, pacs008_content: str = None):
    """Generate email content using the logger agent."""
    try:
        # If we have the original XML content, use it directly
        if pacs004_content and pacs008_content:
            state = {
                "pacs004_xml": pacs004_content,
                "pacs008_xml": pacs008_content,
                "case_id": case_id
            }

            # Run logger agent to generate email
            result = run_prep_logger(state)

            if result and "prep_logger" in result and result["prep_logger"].get("email_payload"):
                # Extract email data from the logger agent result
                email_payload = result["prep_logger"]["email_payload"]
                return {
                    "case_id": case_id,
                    "email_subject": email_payload.get("subject", "return of funds"),
                    "email_recipient": "Intelli Processing",
                    "email_body": email_payload.get("body", ""),
                    "transaction_ref": email_payload.get("reference", ""),
                    "generated_at": result["prep_logger"].get("processing_timestamp", datetime.now().isoformat())
                }

        # Fallback email generation with better data extraction
        return generate_fallback_email(pacs004_data, pacs008_data, case_id, pacs004_content, pacs008_content)

    except Exception as e:
        print(f"Error generating email with logger agent: {e}")
        import traceback
        traceback.print_exc()
        return generate_fallback_email(pacs004_data, pacs008_data, case_id, pacs004_content, pacs008_content)


def generate_fallback_email(pacs004_data: dict, pacs008_data: dict, case_id: str, pacs004_content: str = None, pacs008_content: str = None):
    """Generate fallback email content if logger agent fails."""
    # Try to extract data from XML content directly if parsed data is empty
    amount = pacs004_data.get('amount') or pacs008_data.get('amount', '0')
    currency = pacs004_data.get(
        'currency') or pacs008_data.get('currency', 'USD')
    debtor_name = pacs004_data.get(
        'debtor_name') or pacs008_data.get('debtor_name', 'CUSTOMER')

    # If we still don't have data, try to extract from XML content
    if (not amount or amount == '0') and pacs004_content:
        try:
            import re
            # Extract amount from RtrdIntrBkSttlmAmt
            amount_match = re.search(
                r'<RtrdIntrBkSttlmAmt[^>]*>([^<]+)</RtrdIntrBkSttlmAmt>', pacs004_content)
            if amount_match:
                amount = amount_match.group(1)

            # Extract currency from RtrdIntrBkSttlmAmt
            currency_match = re.search(
                r'<RtrdIntrBkSttlmAmt[^>]*Ccy="([^"]+)"', pacs004_content)
            if currency_match:
                currency = currency_match.group(1)

            # Extract debtor name
            debtor_match = re.search(
                r'<Dbtr>\s*<Nm>([^<]+)</Nm>', pacs004_content)
            if debtor_match:
                debtor_name = debtor_match.group(1)
        except Exception as e:
            print(f"Error extracting data from XML: {e}")

    # Generate MT103 format email
    now = datetime.now()
    value_date = now.strftime("%y%m%d")
    transaction_ref = f"TXN-{case_id.split('-')[-1]}-{now.strftime('%H%M%S')}"

    email_body = f"""Reference: {case_id}
Subject: return of funds
Transaction reference: {transaction_ref}

:20:{transaction_ref}
:23B:CRED
:32A:{value_date}{currency}{amount},00
:33B:{currency}{amount},00
:50K:{debtor_name}
:52A:BOSPGBPMXXXX
:57A:CBAAU2SXXXX
:59A:CBAAU2SXXXX
:71F:{currency}0,00
:71F:USD0,00
:72:/BEN/99
/R99/MS01/MREF/{transaction_ref}/TEX
/MREF/OL_REFERENCE
/TEXT/IT/BENE ACC CLOSED"""

    return {
        "case_id": case_id,
        "email_subject": "return of funds",
        "email_recipient": "Intelli Processing",
        "email_body": email_body,
        "transaction_ref": transaction_ref,
        "generated_at": now.isoformat()
    }


def save_case(case_data: dict):
    """Save case data to file."""
    case_file = CASES_DIR / f"{case_data['case_id']}.json"
    temp_file = case_file.with_suffix('.json.tmp')

    try:
        # Write to temporary file first to avoid corruption
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(case_data, f, indent=2, ensure_ascii=False, default=str)

        # Atomic move to final location
        temp_file.replace(case_file)
    except Exception as e:
        print(f"Error saving case {case_data['case_id']}: {e}")
        # Clean up temp file if it exists
        if temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass
        raise


def load_case(case_id: str):
    """Load case data from file."""
    case_file = CASES_DIR / f"{case_id}.json"
    if case_file.exists():
        with open(case_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def list_cases():
    """List all generated cases."""
    cases = []
    for case_file in CASES_DIR.glob("*.json"):
        try:
            with open(case_file, 'r', encoding='utf-8') as f:
                case_data = json.load(f)
                cases.append(case_data)
        except Exception as e:
            print(f"Error loading case {case_file}: {e}")
            continue

    # Sort by creation date descending
    cases.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return cases


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/simulation")
def simulation():
    """Simulation page for agent flow visualization."""
    return render_template("simulation.html")


@app.route("/run", methods=["POST"])
def run_flow():
    """Process refund using the new graph pipeline."""
    try:
        # Get form parameters
        fx_loss = float(request.form.get("fx_loss_aud", "0") or 0)
        non_branch = request.form.get("non_branch") == "on"
        sanctions = request.form.get("sanctions") == "on"
        case_id = request.form.get("case_id")

        print(f"DEBUG: case_id: {case_id}")

        # Load XML files based on case_id
        if case_id and case_id in CASE_SCENARIOS:
            p4_filename, p8_filename = CASE_SCENARIOS[case_id]
            print(f"DEBUG: Loading case files: {p4_filename}, {p8_filename}")

            try:
                with open(os.path.join("samples", p4_filename), "r", encoding="utf-8") as f:
                    p4_text = f.read()
                with open(os.path.join("samples", p8_filename), "r", encoding="utf-8") as f:
                    p8_text = f.read()
                print(f"DEBUG: Successfully loaded case files for {case_id}")
            except FileNotFoundError as e:
                print(f"DEBUG: Case files not found: {e}")
                return redirect(url_for("index"))
        else:
            # Fallback to default files if no case_id or invalid case_id
            print("DEBUG: Using default sample files")
            with open(os.path.join("samples", "pacs004_matched.xml"), "r", encoding="utf-8") as f:
                p4_text = f.read()
            with open(os.path.join("samples", "pacs008_matched.xml"), "r", encoding="utf-8") as f:
                p8_text = f.read()
            case_id = "DEFAULT"

        print(
            f"DEBUG: About to invoke graph with case_id={case_id}, fx_loss={fx_loss}, non_branch={non_branch}, sanctions={sanctions}")

        # Invoke graph pipeline
        try:
            print("DEBUG: About to invoke graph...")
            res = invoke_graph(p4_text, p8_text, fx_loss,
                               non_branch, sanctions, case_id)
            print(
                f"DEBUG: Graph result keys: {list(res.keys()) if res else 'None'}")
            print(
                f"DEBUG: Graph result run_id: {res.get('run_id') if res else 'None'}")
        except Exception as graph_error:
            print(f"DEBUG: Graph invocation failed: {str(graph_error)}")
            import traceback
            traceback.print_exc()
            return redirect(url_for("index"))

        # Get run_id from the result (set by log_verifier agent)
        run_id = res.get("run_id")
        if not run_id:
            print("DEBUG: No run_id found in result, redirecting to index")
            return redirect(url_for("index"))

        print(f"DEBUG: Redirecting to report with run_id: {run_id}")
        return redirect(url_for("report", run_id=run_id))

    except Exception as e:
        # Handle errors gracefully
        print(f"DEBUG: Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for("index"))


@app.route("/report")
@app.route("/report/<run_id>")
def report(run_id: str | None = None):
    """Display refund processing report."""
    if not run_id:
        return redirect(url_for("index"))
    res = load_run(run_id)
    if not res:
        return redirect(url_for("index"))

    # Get mode parameter from query string
    mode = request.args.get('mode', 'manual')

    return render_template("report.html", result=res, mode=mode)


@app.route("/test-scenarios")
def test_scenarios():
    """Display test scenarios page."""
    return render_template("index.html", show_test_scenarios=True)


@app.route("/api/run/<run_id>")
def api_get_run(run_id: str):
    """API endpoint to get run data as JSON."""
    res = load_run(run_id)
    if not res:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(res)


@app.route("/api/reports")
def api_list_reports():
    """API endpoint to list all reports."""
    reports = []
    for file_path in REPORTS_DIR.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reports.append({
                    "run_id": file_path.stem,
                    "timestamp": data.get("timestamp", ""),
                    "transaction_id": data.get("transaction_id", ""),
                    "can_process": data.get("summary", {}).get("can_process", False),
                    "reason": data.get("summary", {}).get("reason", "")
                })
        except Exception:
            continue

    # Sort by timestamp descending
    reports.sort(key=lambda x: x["timestamp"], reverse=True)
    return jsonify(reports)


@app.route("/upload", methods=["POST"])
def upload_pacs_files():
    """Handle PACS XML file uploads and generate cases."""
    try:
        # Get uploaded files
        pacs004_files = request.files.getlist('pacs004_files')
        pacs008_files = request.files.getlist('pacs008_files')

        if not pacs004_files or not pacs008_files:
            return jsonify({
                "success": False,
                "message": "Both PACS.004 and PACS.008 files are required"
            }), 400

        if len(pacs004_files) != len(pacs008_files):
            return jsonify({
                "success": False,
                "message": "Number of PACS.004 and PACS.008 files must match"
            }), 400

        generated_cases = []

        # Process each file pair
        for i, (pacs004_file, pacs008_file) in enumerate(zip(pacs004_files, pacs008_files)):
            try:
                # Read file contents
                pacs004_content = pacs004_file.read().decode('utf-8')
                pacs008_content = pacs008_file.read().decode('utf-8')

                # Parse XML data
                pacs004_data = parse_pacs_xml(pacs004_content, 'pacs004')
                pacs008_data = parse_pacs_xml(pacs008_content, 'pacs008')

                # Generate case ID first
                case_id = generate_case_id(pacs004_data, pacs008_data)

                # Check for duplicate case (by transaction reference or case ID)
                duplicate_check = check_for_duplicate_case(
                    pacs004_data, pacs008_data, case_id)
                if duplicate_check['is_duplicate']:
                    print(
                        f"Transaction reference exists, or Case Id exists - existing case: {duplicate_check['existing_case_id']}")
                    continue

                # Generate email content
                email_data = generate_email_content(
                    pacs004_data, pacs008_data, case_id, pacs004_content, pacs008_content)

                # Create case data
                # Use amount from email data if available, otherwise fall back to parsed data
                email_amount = email_data.get('email_payload', {}).get(
                    'amount') if email_data.get('email_payload') else None
                email_currency = email_data.get('email_payload', {}).get(
                    'currency') if email_data.get('email_payload') else None

                case_data = {
                    "case_id": case_id,
                    "description": f"PACS Upload {i+1} - {pacs004_data.get('debtor_name', 'Unknown Customer')}",
                    "amount": str(email_amount) if email_amount is not None else (pacs004_data.get('amount') or pacs008_data.get('amount', '0')),
                    "currency": email_currency or pacs004_data.get('currency') or pacs008_data.get('currency', 'USD'),
                    "status": "generated",
                    "created_at": datetime.now().isoformat(),
                    "pacs004_data": pacs004_data,
                    "pacs008_data": pacs008_data,
                    "email_data": email_data,
                    "pacs004_content": pacs004_content,
                    "pacs008_content": pacs008_content
                }

                # Save case
                save_case(case_data)

                # Add to response (without full content for performance)
                response_case = {
                    "case_id": case_data["case_id"],
                    "description": case_data["description"],
                    "amount": case_data["amount"],
                    "currency": case_data["currency"],
                    "status": case_data["status"],
                    "created_at": case_data["created_at"],
                    "email_subject": email_data.get("email_subject"),
                    "email_recipient": email_data.get("email_recipient"),
                    "email_body": email_data.get("email_body")
                }

                generated_cases.append(response_case)

            except Exception as e:
                print(f"Error processing file pair {i+1}: {e}")
                continue

        if not generated_cases:
            return jsonify({
                "success": False,
                "message": "Failed to process any file pairs"
            }), 400

        return jsonify({
            "success": True,
            "cases": generated_cases,
            "message": f"Successfully generated {len(generated_cases)} case(s)"
        })

    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({
            "success": False,
            "message": f"Upload failed: {str(e)}"
        }), 500


@app.route("/upload-pacs-preview", methods=["POST"])
def upload_pacs_preview():
    """Handle PACS XML file uploads and generate email previews without creating cases."""
    try:
        # Get uploaded files
        pacs004_files = request.files.getlist('pacs004_files')
        pacs008_files = request.files.getlist('pacs008_files')

        if not pacs004_files or not pacs008_files:
            return jsonify({
                "success": False,
                "message": "Both PACS.004 and PACS.008 files are required"
            }), 400

        if len(pacs004_files) != len(pacs008_files):
            return jsonify({
                "success": False,
                "message": "Number of PACS.004 and PACS.008 files must match"
            }), 400

        email_previews = []

        # Process each file pair
        for i, (pacs004_file, pacs008_file) in enumerate(zip(pacs004_files, pacs008_files)):
            try:
                # Read file contents
                pacs004_content = pacs004_file.read().decode('utf-8')
                pacs008_content = pacs008_file.read().decode('utf-8')

                # Parse XML data
                pacs004_data = parse_pacs_xml(pacs004_content, 'pacs004')
                pacs008_data = parse_pacs_xml(pacs008_content, 'pacs008')

                # Generate temporary case ID for email generation
                temp_case_id = f"TEMP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{i+1}"

                # Generate email content
                email_data = generate_email_content(
                    pacs004_data, pacs008_data, temp_case_id, pacs004_content, pacs008_content)

                # Create email preview data
                email_preview = {
                    "index": i + 1,
                    "pacs004_filename": pacs004_file.filename,
                    "pacs008_filename": pacs008_file.filename,
                    "debtor_name": pacs004_data.get('debtor_name', 'Unknown Customer'),
                    "amount": pacs004_data.get('amount') or pacs008_data.get('amount', '0'),
                    "currency": pacs004_data.get('currency') or pacs008_data.get('currency', 'USD'),
                    "email_subject": email_data.get("email_subject"),
                    "email_recipient": email_data.get("email_recipient"),
                    "email_body": email_data.get("email_body"),
                    "pacs004_data": pacs004_data,
                    "pacs008_data": pacs008_data,
                    "pacs004_content": pacs004_content,
                    "pacs008_content": pacs008_content,
                    "email_data": email_data
                }

                email_previews.append(email_preview)

            except Exception as e:
                print(f"Error processing file pair {i+1}: {e}")
                continue

        if not email_previews:
            return jsonify({
                "success": False,
                "message": "Failed to process any file pairs"
            }), 400

        return jsonify({
            "success": True,
            "email_previews": email_previews,
            "message": f"Successfully processed {len(email_previews)} PACS pair(s)"
        })

    except Exception as e:
        print(f"Upload preview error: {e}")
        return jsonify({
            "success": False,
            "message": f"Upload failed: {str(e)}"
        }), 500


@app.route("/create-cases-from-emails", methods=["POST"])
def create_cases_from_emails():
    """Create cases from email preview data."""
    try:
        data = request.get_json()
        selected_indices = data.get('selected_indices', [])
        email_previews = data.get('email_previews', [])

        if not selected_indices or not email_previews:
            return jsonify({
                "success": False,
                "message": "No email previews selected for case creation"
            }), 400

        created_cases = []

        for index in selected_indices:
            try:
                # Find the email preview data
                email_preview = next(
                    (ep for ep in email_previews if ep['index'] == index), None)
                if not email_preview:
                    continue

                # Generate actual case ID first
                case_id = generate_case_id(
                    email_preview['pacs004_data'], email_preview['pacs008_data'])

                # Check for duplicate case (by transaction reference or case ID)
                duplicate_check = check_for_duplicate_case(
                    email_preview['pacs004_data'], email_preview['pacs008_data'], case_id)
                if duplicate_check['is_duplicate']:
                    print(
                        f"Transaction reference exists, or Case Id exists - existing case: {duplicate_check['existing_case_id']}")
                    continue

                # Create case data
                case_data = {
                    "case_id": case_id,
                    "description": f"PACS Upload {index} - {email_preview['debtor_name']}",
                    "amount": email_preview['amount'],
                    "currency": email_preview['currency'],
                    "status": "generated",
                    "created_at": datetime.now().isoformat(),
                    "pacs004_data": email_preview['pacs004_data'],
                    "pacs008_data": email_preview['pacs008_data'],
                    "email_data": email_preview['email_data'],
                    "pacs004_content": email_preview['pacs004_content'],
                    "pacs008_content": email_preview['pacs008_content']
                }

                # Save case
                save_case(case_data)

                # Add to response
                response_case = {
                    "case_id": case_data["case_id"],
                    "description": case_data["description"],
                    "amount": case_data["amount"],
                    "currency": case_data["currency"],
                    "status": case_data["status"],
                    "created_at": case_data["created_at"],
                    "email_subject": email_preview['email_subject'],
                    "email_recipient": email_preview['email_recipient'],
                    "email_body": email_preview['email_body']
                }

                created_cases.append(response_case)

            except Exception as e:
                print(f"Error creating case for index {index}: {e}")
                continue

        if not created_cases:
            return jsonify({
                "success": False,
                "message": "Failed to create any cases"
            }), 400

        return jsonify({
            "success": True,
            "cases": created_cases,
            "message": f"Successfully created {len(created_cases)} case(s)"
        })

    except Exception as e:
        print(f"Create cases error: {e}")
        return jsonify({
            "success": False,
            "message": f"Case creation failed: {str(e)}"
        }), 500


def process_single_case(case_id: str) -> Dict[str, Any]:
    """Process a single case through the refund investigation workflow."""
    try:
        # Load case data
        case_data = load_case(case_id)
        if not case_data:
            raise Exception(f"Case {case_id} not found")

        # Update case status
        case_data["status"] = "processing"
        save_case(case_data)

        # Process through the graph pipeline
        result = invoke_graph(
            pacs004_text=case_data["pacs004_content"],
            pacs008_text=case_data["pacs008_content"],
            fx_loss_aud=0.0,  # Default value
            non_branch=True,  # Default value
            sanctions=True,   # Default value
            case_id=case_id
        )

        # Update case with result
        case_data["status"] = "completed"
        case_data["run_id"] = result.get("run_id")
        case_data["processed_at"] = datetime.now().isoformat()
        save_case(case_data)

        # Create a serializable result by extracting only the essential data
        serializable_result = {
            "run_id": result.get("run_id"),
            "success": True,
            "timestamp": datetime.now().isoformat()
        }

        return {
            "case_id": case_id,
            "run_id": result.get("run_id"),
            "status": "completed",
            "result": serializable_result
        }

    except Exception as e:
        print(f"Error processing case {case_id}: {e}")
        # Update case status to failed
        case_data = load_case(case_id)
        if case_data:
            case_data["status"] = "failed"
            case_data["error"] = str(e)
            save_case(case_data)

        return {
            "case_id": case_id,
            "status": "failed",
            "error": str(e)
        }


@app.route("/process-cases", methods=["POST"])
def process_selected_cases():
    """Process selected cases through the refund investigation workflow."""
    try:
        case_ids = request.form.getlist('case_ids')

        if not case_ids:
            return jsonify({
                "success": False,
                "message": "No cases selected for processing"
            }), 400

        # For single case, use original logic
        if len(case_ids) == 1:
            result = process_single_case(case_ids[0])
            if result["status"] == "completed":
                return jsonify({
                    "success": True,
                    "message": "Case processed successfully",
                    "processed_cases": [result]
                })
            else:
                return jsonify({
                    "success": False,
                    "message": f"Case processing failed: {result.get('error', 'Unknown error')}"
                }), 400

        # Sequential processing for multiple cases
        processed_cases = []
        failed_cases = []

        for case_id in case_ids:
            result = process_single_case(case_id)
            if result["status"] == "completed":
                processed_cases.append(result)
            else:
                failed_cases.append(result)

        if not processed_cases:
            return jsonify({
                "success": False,
                "message": "Failed to process any cases",
                "failed_cases": failed_cases
            }), 400

        return jsonify({
            "success": True,
            "message": f"Successfully processed {len(processed_cases)} case(s)",
            "processed_cases": processed_cases,
            "failed_cases": failed_cases
        })

    except Exception as e:
        print(f"Process cases error: {e}")
        return jsonify({
            "success": False,
            "message": f"Processing failed: {str(e)}"
        }), 500


@app.route("/api/cases")
def api_list_cases():
    """API endpoint to list all generated cases."""
    try:
        cases = list_cases()
        # Return only essential data for the frontend
        response_cases = []
        for case in cases:
            response_cases.append({
                "case_id": case["case_id"],
                "description": case["description"],
                "amount": case["amount"],
                "currency": case["currency"],
                "status": case["status"],
                "created_at": case["created_at"],
                # Include run_id for processed cases
                "run_id": case.get("run_id"),
                "email_subject": case.get("email_data", {}).get("email_subject"),
                "email_recipient": case.get("email_data", {}).get("email_recipient"),
                "email_body": case.get("email_data", {}).get("email_body")
            })

        return jsonify(response_cases)

    except Exception as e:
        print(f"Error listing cases: {e}")
        return jsonify({"error": "Failed to list cases"}), 500


@app.route("/api/cases/<case_id>")
def api_get_case(case_id: str):
    """API endpoint to get specific case data."""
    try:
        case_data = load_case(case_id)
        if not case_data:
            return jsonify({"error": "Case not found"}), 404

        return jsonify(case_data)

    except Exception as e:
        print(f"Error getting case {case_id}: {e}")
        return jsonify({"error": "Failed to get case"}), 500


@app.route("/api/cases/<case_id>", methods=["DELETE"])
def api_delete_case(case_id: str):
    """API endpoint to delete a case."""
    try:
        case_file = CASES_DIR / f"{case_id}.json"
        if case_file.exists():
            case_file.unlink()
            return jsonify({"success": True, "message": "Case deleted successfully"})
        else:
            return jsonify({"error": "Case not found"}), 404

    except Exception as e:
        print(f"Error deleting case {case_id}: {e}")
        return jsonify({"error": "Failed to delete case"}), 500


@app.route("/api/cases", methods=["DELETE"])
def api_delete_all_cases():
    """API endpoint to delete all cases."""
    try:
        deleted_count = 0
        for case_file in CASES_DIR.glob("*.json"):
            try:
                case_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting case file {case_file}: {e}")
                continue

        return jsonify({
            "success": True,
            "message": f"Successfully deleted {deleted_count} case(s)"
        })

    except Exception as e:
        print(f"Error deleting all cases: {e}")
        return jsonify({"error": "Failed to delete all cases"}), 500


@app.route("/api/pacs-pairs")
def api_list_pacs_pairs():
    """API endpoint to list available PACS file pairs from samples directory."""
    try:
        SAMPLES_DIR = pathlib.Path("samples")
        if not SAMPLES_DIR.exists():
            return jsonify({"pairs": []})

        pairs = []

        # Find all PACS.004 files (files that don't end with _pacs008.xml)
        pacs004_files = [
            f for f in SAMPLES_DIR.glob("*.xml")
            if not f.name.endswith("_pacs008.xml")
        ]

        for pacs004_file in pacs004_files:
            # Try to find matching PACS.008 file
            base_name = pacs004_file.stem

            # Try different naming patterns
            possible_pacs008_names = []

            # Pattern 1: base_name_pacs008.xml (most common)
            possible_pacs008_names.append(f"{base_name}_pacs008.xml")

            # Pattern 2: Special case for pacs004_matched.xml -> pacs008_matched.xml
            if "pacs004_matched" in pacs004_file.name.lower():
                possible_pacs008_names.append("pacs008_matched.xml")

            # Pattern 3: Replace pacs004 with pacs008 in filename
            if "pacs004" in pacs004_file.name.lower():
                possible_pacs008_names.append(
                    pacs004_file.name.replace("pacs004", "pacs008")
                    .replace("PACS004", "pacs008")
                )

            # Find matching PACS.008 file
            pacs008_file = None
            for pattern in possible_pacs008_names:
                candidate = SAMPLES_DIR / pattern
                if candidate.exists():
                    pacs008_file = candidate
                    break

            if pacs008_file:
                # Construct paths - use the actual file paths from glob results
                # These paths are already relative to cwd
                # Convert to string and normalize slashes for cross-platform compatibility
                pacs004_path = str(pacs004_file).replace('\\', '/')
                pacs008_path = str(pacs008_file).replace('\\', '/')

                # Try to extract some metadata
                try:
                    pacs004_content = pacs004_file.read_text(encoding='utf-8')
                    pacs004_data = parse_pacs_xml(pacs004_content, 'pacs004')

                    pacs008_content = pacs008_file.read_text(encoding='utf-8')
                    pacs008_data = parse_pacs_xml(pacs008_content, 'pacs008')

                    pairs.append({
                        "id": f"{pacs004_file.name}_{pacs008_file.name}",
                        "pacs004_filename": pacs004_file.name,
                        "pacs008_filename": pacs008_file.name,
                        "pacs004_path": pacs004_path,
                        "pacs008_path": pacs008_path,
                        "debtor_name": pacs004_data.get('debtor_name') or pacs008_data.get('debtor_name', 'Unknown'),
                        "amount": pacs004_data.get('amount') or pacs008_data.get('amount', '0'),
                        "currency": pacs004_data.get('currency') or pacs008_data.get('currency', 'USD'),
                        "display_name": f"{pacs004_file.stem} / {pacs008_file.stem}"
                    })
                except Exception as e:
                    print(
                        f"Error parsing pair {pacs004_file.name}/{pacs008_file.name}: {e}")
                    # Still add the pair even if parsing fails
                    pairs.append({
                        "id": f"{pacs004_file.name}_{pacs008_file.name}",
                        "pacs004_filename": pacs004_file.name,
                        "pacs008_filename": pacs008_file.name,
                        "pacs004_path": pacs004_path,
                        "pacs008_path": pacs008_path,
                        "debtor_name": "Unknown",
                        "amount": "0",
                        "currency": "USD",
                        "display_name": f"{pacs004_file.stem} / {pacs008_file.stem}"
                    })

        return jsonify({"pairs": pairs})

    except Exception as e:
        print(f"Error listing PACS pairs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to list PACS pairs: {str(e)}"}), 500


@app.route("/api/generate-email-preview-from-files", methods=["POST"])
def api_generate_email_preview_from_files():
    """API endpoint to generate email previews from selected file paths."""
    try:
        data = request.get_json()
        pacs004_path = data.get('pacs004_path')
        pacs008_path = data.get('pacs008_path')

        if not pacs004_path or not pacs008_path:
            return jsonify({
                "success": False,
                "message": "Both PACS.004 and PACS.008 file paths are required"
            }), 400

        # Read file contents - resolve paths relative to current working directory
        pacs004_file = pathlib.Path(pacs004_path).resolve()
        pacs008_file = pathlib.Path(pacs008_path).resolve()

        if not pacs004_file.exists() or not pacs008_file.exists():
            return jsonify({
                "success": False,
                "message": f"One or both files not found: {pacs004_path}, {pacs008_path}"
            }), 404

        pacs004_content = pacs004_file.read_text(encoding='utf-8')
        pacs008_content = pacs008_file.read_text(encoding='utf-8')

        # Parse XML data
        pacs004_data = parse_pacs_xml(pacs004_content, 'pacs004')
        pacs008_data = parse_pacs_xml(pacs008_content, 'pacs008')

        # Generate temporary case ID for email generation
        temp_case_id = f"TEMP-{datetime.now().strftime('%Y%m%d%H%M%S')}-1"

        # Generate email content
        email_data = generate_email_content(
            pacs004_data, pacs008_data, temp_case_id, pacs004_content, pacs008_content
        )

        # Create email preview data
        # Extract debtor name from both PACS004 and PACS008 (same logic as case creation)
        debtor_name = pacs004_data.get('debtor_name') or pacs008_data.get(
            'debtor_name', 'Unknown Customer')
        email_preview = {
            "index": 1,
            "pacs004_filename": pacs004_file.name,
            "pacs008_filename": pacs008_file.name,
            "debtor_name": debtor_name,
            "amount": pacs004_data.get('amount') or pacs008_data.get('amount', '0'),
            "currency": pacs004_data.get('currency') or pacs008_data.get('currency', 'USD'),
            "email_subject": email_data.get("email_subject"),
            "email_recipient": email_data.get("email_recipient"),
            "email_body": email_data.get("email_body"),
            "pacs004_data": pacs004_data,
            "pacs008_data": pacs008_data,
            "pacs004_content": pacs004_content,
            "pacs008_content": pacs008_content,
            "email_data": email_data,
            "pacs004_path": pacs004_path,
            "pacs008_path": pacs008_path
        }

        return jsonify({
            "success": True,
            "email_previews": [email_preview],
            "message": f"Successfully generated email preview"
        })

    except Exception as e:
        print(f"Error generating email preview from files: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Failed to generate email preview: {str(e)}"
        }), 500


@app.route("/api/create-case-from-files", methods=["POST"])
def api_create_case_from_files():
    """API endpoint to create a case directly from selected file paths."""
    try:
        data = request.get_json()
        pacs004_path = data.get('pacs004_path')
        pacs008_path = data.get('pacs008_path')

        if not pacs004_path or not pacs008_path:
            return jsonify({
                "success": False,
                "message": "Both PACS.004 and PACS.008 file paths are required"
            }), 400

        # Read file contents - resolve paths relative to current working directory
        pacs004_file = pathlib.Path(pacs004_path).resolve()
        pacs008_file = pathlib.Path(pacs008_path).resolve()

        if not pacs004_file.exists() or not pacs008_file.exists():
            return jsonify({
                "success": False,
                "message": f"One or both files not found: {pacs004_path}, {pacs008_path}"
            }), 404

        pacs004_content = pacs004_file.read_text(encoding='utf-8')
        pacs008_content = pacs008_file.read_text(encoding='utf-8')

        # Parse XML data
        pacs004_data = parse_pacs_xml(pacs004_content, 'pacs004')
        pacs008_data = parse_pacs_xml(pacs008_content, 'pacs008')

        # Generate case ID first
        case_id = generate_case_id(pacs004_data, pacs008_data)

        # Check for duplicate case (by transaction reference or case ID)
        duplicate_check = check_for_duplicate_case(
            pacs004_data, pacs008_data, case_id)
        if duplicate_check['is_duplicate']:
            return jsonify({
                "success": False,
                "message": f"Transaction reference exists, or Case Id exists - existing case: {duplicate_check['existing_case_id']}",
                "is_duplicate": True,
                "existing_case_id": duplicate_check['existing_case_id']
            }), 400

        # Generate email content
        email_data = generate_email_content(
            pacs004_data, pacs008_data, case_id, pacs004_content, pacs008_content
        )

        # Create case data
        debtor_name = pacs004_data.get('debtor_name') or pacs008_data.get(
            'debtor_name', 'Unknown Customer')
        case_data = {
            "case_id": case_id,
            "description": f"PACS File Pair - {debtor_name}",
            "amount": pacs004_data.get('amount') or pacs008_data.get('amount', '0'),
            "currency": pacs004_data.get('currency') or pacs008_data.get('currency', 'USD'),
            "status": "generated",
            "created_at": datetime.now().isoformat(),
            "pacs004_data": pacs004_data,
            "pacs008_data": pacs008_data,
            "email_data": email_data,
            "pacs004_content": pacs004_content,
            "pacs008_content": pacs008_content,
            "pacs004_filename": pacs004_file.name,
            "pacs008_filename": pacs008_file.name
        }

        # Save case
        save_case(case_data)

        # Return response
        response_case = {
            "case_id": case_data["case_id"],
            "description": case_data["description"],
            "amount": case_data["amount"],
            "currency": case_data["currency"],
            "status": case_data["status"],
            "created_at": case_data["created_at"],
            "email_subject": email_data.get("email_subject"),
            "email_recipient": email_data.get("email_recipient"),
            "email_body": email_data.get("email_body")
        }

        return jsonify({
            "success": True,
            "case": response_case,
            "message": f"Successfully created case {case_id}"
        })

    except Exception as e:
        print(f"Error creating case from files: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Failed to create case: {str(e)}"
        }), 500


@app.route("/api/report/<identifier>")
def api_get_report_by_identifier(identifier: str):
    """API endpoint to get report data by case_id or run_id."""
    try:
        # First, try to load as a run_id directly
        report_data = load_run(identifier)
        run_id = identifier if report_data else None

        # If not found as run_id, try as case_id
        if not report_data:
            case_data = load_case(identifier)
            if not case_data:
                return jsonify({"error": "Case or report not found"}), 404

            # Check if the case has been processed and has a run_id
            run_id = case_data.get("run_id")
            if not run_id:
                return jsonify({"error": "Case has not been processed yet"}), 400

            # Load the report using the run_id
            report_data = load_run(run_id)
            if not report_data:
                return jsonify({"error": "Report not found"}), 404

        # Check if email needs to be generated (same logic as report route)
        if run_id and report_data:
            comm_notification = report_data.get("communications", {}).get(
                "communication_templates", {}).get("customer_notification", {})
            if not comm_notification.get("html_body") or comm_notification.get("generated_by") != "gemini":
                # Generate email if it doesn't exist or wasn't generated by Gemini
                try:
                    from app.utils.gemini_email import generate_customer_email

                    # Extract data from report
                    p004 = report_data.get("parsed_data", {}).get(
                        "pacs004", {}) or report_data.get("parsed_pacs004", {})
                    p008 = report_data.get("parsed_data", {}).get(
                        "pacs008", {}) or report_data.get("parsed_pacs008", {})
                    refund = report_data.get(
                        "refund_decision", {}) or report_data.get("summary", {})
                    elig = report_data.get("investigation", {}).get(
                        "eligibility", {}) or report_data.get("investigator_eligibility", {})

                    # Get customer data from CSV validation if available
                    csv_validation = report_data.get(
                        "investigation", {}).get("csv_validation", {})
                    customer_record = csv_validation.get(
                        "customer", {}) if csv_validation else {}

                    # Handle customer record if it's an object
                    if customer_record and hasattr(customer_record, "__dict__"):
                        customer_record = customer_record.__dict__
                    elif not isinstance(customer_record, dict):
                        customer_record = {}

                    recipient_name = customer_record.get(
                        "account_holder_name") or p008.get("dbtr_name", "Customer")
                    recipient_email = customer_record.get(
                        "email") or p008.get("dbtr_email", "")
                    uetr = p004.get("uetr", p004.get("e2e", "N/A"))
                    return_amount = str(p004.get("rtr_amount", ""))
                    return_currency = p004.get("rtr_ccy", "")
                    reason_code = p004.get("rsn", "")
                    reason_info = p004.get("rsn_info", "")
                    fx_loss_aud = elig.get("fx_loss_aud") if elig else None
                    status = "Refund Processed" if refund.get(
                        "can_process") else "Refund Pending"

                    # Determine action required
                    action_required = "No action required. Your refund has been processed successfully." if refund.get("can_process") else (
                        "Our systems indicate the account number provided is incorrect. To proceed with the refund, please provide the correct account details." if reason_code == "AC01" else (
                            "Our systems indicate the original IBAN is no longer valid. To proceed with the refund, please provide an alternate active account number." if reason_code == "AC04" else (
                                "This case requires manual review due to currency mismatch." if reason_code == "CURR" else (
                                    "This case requires manual review due to FX loss exceeding the threshold." if elig and not elig.get(
                                        "fx_loss_within_limit", True) else "We are reviewing your case and will update you shortly."
                                )
                            )
                        )
                    )

                    # Generate email
                    email_data = generate_customer_email(
                        recipient_name=recipient_name,
                        recipient_email=recipient_email,
                        uetr=uetr,
                        return_amount=return_amount,
                        return_currency=return_currency,
                        reason_code=reason_code,
                        reason_info=reason_info,
                        fx_loss_aud=fx_loss_aud,
                        status=status,
                        action_required=action_required,
                        variation_mode=False
                    )

                    # Update the report data with generated email
                    if "communications" not in report_data:
                        report_data["communications"] = {}
                    if "communication_templates" not in report_data["communications"]:
                        report_data["communications"]["communication_templates"] = {}
                    report_data["communications"]["communication_templates"]["customer_notification"] = {
                        "recipient": recipient_name,
                        "email": recipient_email,
                        "subject": email_data.get("subject", f"Refund Processing Update - {p004.get('e2e', '')}"),
                        "body": email_data.get("body", ""),
                        "html_body": email_data.get("html_body", ""),
                        "status": "processed" if refund.get("can_process") else "pending",
                        "amount": return_amount,
                        "currency": return_currency,
                        "reference": p004.get("e2e", ""),
                        "uetr": uetr,
                        "account_operations": refund.get("account_operations", []),
                        "generated_by": email_data.get("generated_by", "gemini")
                    }

                    # Save the updated report
                    try:
                        report_file = REPORTS_DIR / f"{run_id}.json"
                        with open(report_file, 'w', encoding='utf-8') as f:
                            json.dump(report_data, f, indent=2,
                                      ensure_ascii=False, default=str)
                        print(
                            f"DEBUG: Auto-generated and saved email for run_id {run_id}")
                    except Exception as save_error:
                        print(
                            f"Warning: Could not save updated email to report: {save_error}")
                except Exception as e:
                    print(
                        f"Warning: Could not auto-generate email in API endpoint: {e}")
                    import traceback
                    traceback.print_exc()

        return jsonify(report_data)

    except Exception as e:
        print(f"Error getting report for identifier {identifier}: {e}")
        return jsonify({"error": f"Failed to get report: {str(e)}"}), 500


@app.route("/api/regenerate-email", methods=["POST"])
def regenerate_email():
    """API endpoint to regenerate customer notification email using Gemini API."""
    try:
        data = request.get_json()
        run_id = data.get("run_id")

        if not run_id:
            return jsonify({"error": "run_id is required"}), 400

        # Load the report data
        report_data = load_run(run_id)
        if not report_data:
            return jsonify({"error": "Report not found"}), 404

        # Extract data from report
        p004 = report_data.get("parsed_data", {}).get("pacs004", {})
        p008 = report_data.get("parsed_data", {}).get("pacs008", {})
        refund = report_data.get("refund_decision", {}
                                 ) or report_data.get("summary", {})
        elig = report_data.get("investigation", {}).get(
            "eligibility", {}) or report_data.get("investigator_eligibility", {})

        # Get customer data from CSV validation if available
        csv_validation = report_data.get(
            "investigation", {}).get("csv_validation", {})
        customer_record = csv_validation.get(
            "record", {}) if csv_validation else {}

        recipient_name = customer_record.get(
            "account_holder_name") or p008.get("dbtr_name", "Customer")
        recipient_email = customer_record.get(
            "email") or p008.get("dbtr_email", "")
        uetr = p004.get("uetr", p004.get("e2e", "N/A"))
        return_amount = str(p004.get("rtr_amount", ""))
        return_currency = p004.get("rtr_ccy", "")
        reason_code = p004.get("rsn", "")
        reason_info = p004.get("rsn_info", "")
        fx_loss_aud = elig.get("fx_loss_aud") if elig else None
        status = "Refund Processed" if refund.get(
            "can_process") else "Refund Pending"

        # Determine action required
        from app.utils.gemini_email import generate_customer_email

        action_required = "No action required. Your refund has been processed successfully." if refund.get("can_process") else (
            "Our systems indicate the account number provided is incorrect. To proceed with the refund, please provide the correct account details." if reason_code == "AC01" else (
                "Our systems indicate the original IBAN is no longer valid. To proceed with the refund, please provide an alternate active account number." if reason_code == "AC04" else (
                    "This case requires manual review due to currency mismatch." if reason_code == "CURR" else (
                        "This case requires manual review due to FX loss exceeding the threshold." if elig and not elig.get(
                            "fx_loss_within_limit", True) else "We are reviewing your case and will update you shortly."
                    )
                )
            )
        )

        # Generate new email with variation mode enabled
        email_data = generate_customer_email(
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            uetr=uetr,
            return_amount=return_amount,
            return_currency=return_currency,
            reason_code=reason_code,
            reason_info=reason_info,
            fx_loss_aud=fx_loss_aud,
            status=status,
            action_required=action_required,
            variation_mode=True  # Enable variation for regeneration
        )

        return jsonify({
            "success": True,
            "email": {
                "subject": email_data.get("subject", ""),
                "body": email_data.get("body", ""),
                "html_body": email_data.get("html_body", ""),
                "generated_by": email_data.get("generated_by", "template")
            }
        })

    except Exception as e:
        print(f"Error regenerating email: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to regenerate email: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
