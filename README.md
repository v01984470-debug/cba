# CBA Unified Refund Processing System

A comprehensive, agent-based payment refund processing system implementing the D1-D9 decision flow from `refund_flow_.md`. This system processes ISO 20022 PACS.004 and PACS.008 messages using a unified web interface with CSV-based data management and full audit trail.

## 🌟 Key Features

### **Agent Graph Pipeline**

- **🔍 Investigator Agent**: Parse PACS messages, validate customers, calculate FX loss
- **✅ Verifier Agent**: MT940 reconciliation, sequence checks, compliance validation
- **💰 Refund Agent**: Execute D1-D9 decision flow with CSV operations
- **📋 Log Verifier Agent**: Consolidate audit events, save reports to csv_reports/
- **📞 Communications Agent**: Generate customer/branch notification templates

### **D1-D9 Decision Flow Implementation**

```
D1: Foreign currency? → D2 (YES) or D6 (NO)
D2: Nostro found? → D3 (YES) or D4 (NO)
D3: FCA refund? → FCA flow (YES) or standard (NO) → D7
D4: Nostro after SCR? → D3 (YES) or D7 (NO)
D5: Markets? → email/QF/close
D6: Debit authority? → Vostro (YES) or OB (NO) → D7
D7: Branch payment? → branch SAIT (YES) or client (NO) → D8
D8: Markets? → D9 (NO) or email/QF/close (YES)
D9: Valid email? → send refund or adhoc → QF/close
```

### **Repository Pattern (SQLite-Ready)**

- Abstract repository interfaces for easy database migration
- CSV implementations for current data management
- Account, Statement, Ledger, Customer, and Audit repositories

### **Comprehensive CSV Operations**

- Debit nostro/vostro/OB accounts with balance updates
- Credit FCA/client/branch accounts with full traceability
- MT940-style statement entries with proper references
- Real-time balance tracking with before/after states

## 🚀 Quick Start

### **Prerequisites**

- Python 3.8 or higher
- Windows 10+ / macOS / Linux

### **Installation**

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Start the application**:
   ```bash
   python app/web.py
   ```
4. **Access the web interface**: http://localhost:5000

### **Using the System**

1. **Upload PACS Messages**: Upload PACS.004 and PACS.008 XML files
2. **Run Processing**: Click "Run Investigation" to execute the agent pipeline
3. **View Results**: Navigate through tabs to see:
   - **Investigation Details**: Eligibility and validation results
   - **Account Operations**: Detailed debit/credit operations with balances
   - **Detailed Process Overview**: Complete decision flow
   - **Interactive Agent Graph**: Visual workflow representation
   - **Communication**: Customer and branch notification templates

## 📊 Data Structure

### **CSV Files (data/ directory)**

- `bank_accounts.csv`: Account details, balances, types (Nostro/Vostro/OB/Customer)
- `customer_data.csv`: Customer information and account mappings
- `internal_ledger.csv`: Transaction ledger with references
- `nostro_statement.csv`: Nostro account statements with MT940 references
- `vostro_statement.csv`: Vostro account statements
- `audit_log.csv`: Complete audit trail

### **Reports (csv_reports/ directory)**

- All processing reports saved as JSON files
- Includes decision paths, account operations, audit events
- Accessible via web interface and API endpoints

## 🏗️ Architecture

### **Agent Workflow**

```
Investigator → Verifier → Refund → Log Verifier → Communications
```

### **Repository Pattern**

```python
# Abstract interfaces
AccountRepository, StatementRepository, LedgerRepository,
CustomerRepository, AuditRepository

# CSV implementations
CSVAccountRepository, CSVStatementRepository, CSVLedgerRepository,
CSVCustomerRepository, CSVAuditRepository
```

### **Decision Engine Operations**

- **Nostro Debit**: Update balance + append statement entry with MT940 refs
- **Vostro Debit**: Check camt.029 authority, update balance + statement
- **OB Debit**: Fallback when vostro authority denied
- **FCA Credit**: Same-name validation, balance update
- **Client Credit**: Original account credit with balance tracking
- **Branch Credit**: BSB-based routing for branch payments

## 🧪 Test Scenarios

Run comprehensive test scenarios:

```bash
python tests/refund_scenarios.py
```

### **Test Cases**

1. **Matched Nostro**: E2E match in MT940 → D1→D2(found)→D3(no)→debit nostro→D7→credit client
2. **Unmatched Nostro**: Partial match → D1→D2(no)→D4(no)→D6(auth YES)→debit vostro→D7→credit client
3. **FCA Same-Name**: D1→D2(found)→D3(FCA YES)→debit nostro→credit FCA→D5→close
4. **Vostro Authority**: D1→D2(no)→D4(no)→D6(auth YES)→debit vostro→D7→credit client
5. **OB Fallback**: D1→D2(no)→D4(no)→D6(auth NO)→debit OB→D7→credit client

## 📁 Project Structure

```
CBA/
├── app/
│   ├── agents/                    # Agent implementations
│   │   ├── investigator.py        # Parse, validate, eligibility
│   │   ├── verifier.py           # MT940 reconciliation, checks
│   │   ├── refund.py             # D1-D9 decision engine
│   │   ├── logger.py             # Audit consolidation, reports
│   │   └── comms.py              # Notification templates
│   ├── templates/
│   │   ├── index.html            # Unified upload interface
│   │   └── report.html           # Tabbed results with account ops
│   ├── utils/
│   │   ├── repositories.py       # Abstract repository interfaces
│   │   ├── csv_repositories.py   # CSV implementations
│   │   ├── refund_decision_engine.py  # D1-D9 logic
│   │   ├── csv_reconciliation.py # MT940 matching
│   │   ├── xml_parsers.py        # PACS parsing
│   │   ├── debit_authority.py    # Camt.029/MT199 authority
│   │   └── audit_logger.py       # Audit trail management
│   ├── graph.py                  # Agent pipeline definition
│   └── web.py                    # Unified Flask server
├── csv_reports/                  # All run JSONs
├── data/                         # CSV data files
├── samples/                      # Test XML files
├── tests/
│   └── refund_scenarios.py       # Test scenarios
├── refund_flow_.md               # Decision flow specification
└── README.md                     # This file
```

## 🔧 API Endpoints

### **Web Interface**

- `GET /`: Main upload interface
- `POST /run`: Process refund with uploaded files
- `GET /report/<run_id>`: View processing report
- `GET /test-scenarios`: Test scenarios interface

### **API Endpoints**

- `GET /api/run/<run_id>`: Get run data as JSON
- `GET /api/reports`: List all reports

## 🎯 Key Processing Features

### **MT940 Reconciliation**

- **Exact Match**: :61: + :86: fields with amount, currency, UETR
- **Partial Match**: :86: field only (missing :61:)
- **No Match**: Escalate to Nostro Operations

### **Account Operations**

- Real-time balance updates in CSV files
- Detailed operation tracking with before/after balances
- MT940-style statement entries with proper references
- Full traceability from PACS.008 ↔ PACS.004 ↔ MT940 ↔ ledger

### **Decision Path Tracking**

- Complete D1-D9 decision flow logging
- Account operation details with amounts and references
- Audit events for each agent and decision point
- Comprehensive reporting in JSON format

## 🔒 Security & Compliance

- **Audit Trail**: Complete audit trail in CSV and JSON formats
- **Data Integrity**: Repository pattern ensures consistent data access
- **Traceability**: Full transaction traceability from XML to final operations
- **Validation**: Comprehensive input validation and error handling

## 🚀 Future Enhancements

### **SQLite Migration**

The repository pattern is designed for easy migration to SQLite:

```python
# Future SQLite implementations
SQLiteAccountRepository, SQLiteStatementRepository,
SQLiteLedgerRepository, SQLiteCustomerRepository, SQLiteAuditRepository
```

### **Additional Features**

- Real-time dashboard with processing statistics
- Batch processing capabilities
- Advanced reporting and analytics
- Integration with external banking systems

## 📞 Support

For issues or questions:

1. Check the test scenarios for expected behavior
2. Review the audit trail in csv_reports/
3. Examine the decision path in the web interface
4. Check the account operations tab for detailed CSV updates

## 🎉 Success Criteria

✅ **Single unified web interface** at http://localhost:5000  
✅ **All reports in csv_reports/** folder  
✅ **Graph pipeline executes D1-D9** correctly  
✅ **Account operations visible in UI** with balances  
✅ **Test scenarios pass** and generate proper reports  
✅ **Code ready for SQLite swap** (repository pattern)

---

**Ready to process refunds with the unified system? Start the application and explore the D1-D9 decision flow!** 🚀
