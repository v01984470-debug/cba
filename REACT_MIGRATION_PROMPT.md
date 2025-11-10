# React Frontend Migration Prompt

## Overview

This document provides a comprehensive guide for rebuilding the Payment Refund Investigations system—currently implemented with Flask server-side templates and HTML—as a fully React-based frontend application. The backend Flask API will remain unchanged; only the frontend needs to be rebuilt using React.

---

## Current Application Architecture

### **Backend (Flask - Keep As-Is)**

- **Framework**: Flask (Python)
- **Location**: `app/web.py` and `app/graph.py`
- **Port**: 5000
- **CORS**: Enabled for all routes
- **Data Storage**:
  - Cases stored in `cases/` directory as JSON files
  - Reports stored in `csv_reports/` directory as JSON files
  - CSV data files in `data/` directory

### **Frontend (Current - To Be Replaced)**

- **Technology**: Server-side rendered HTML templates
- **Templates Location**: `app/templates/`
  - `index.html` - Main upload interface with case management
  - `report.html` - Detailed processing report with tabs
  - `simulation.html` - Agent flow visualization page
- **Styling**: Inline CSS within HTML files
- **JavaScript**: Vanilla JS with DOM manipulation

---

## Application Features & Functionality

### **1. Main Dashboard (index.html)**

#### **Mode Toggle**

- **Manual Mode** (default): Single case selection mode
  - Shows file upload section
  - Radio button selection for cases
  - Processes one case at a time
- **Automated Mode**: Multiple case selection mode
  - Hides file upload section
  - Checkbox selection for cases
  - Processes multiple cases sequentially

#### **File Upload Section (Manual Mode Only)**

- **PACS File Upload**
  - Upload multiple PACS.004 files
  - Upload corresponding PACS.008 files
  - File count validation (must match)
  - Preview of selected files
- **Email Preview Generation**
  - Shows generated email previews after upload
  - Each preview includes:
    - PACS pair filenames
    - Debtor name and amount
    - Generated email subject, recipient, and body
  - Checkbox selection for each preview
  - Select All / Deselect All buttons
  - Create Selected Cases button
- **Email Preview List**
  - Displays formatted email containers
  - Shows MT103 message body
  - Includes PACS pair information

#### **Case Management Section**

- **Cases Table**
  - Columns: Select, Case ID, Description, Amount, Currency, Status, Report, Created, Actions
  - Case Status Indicators:
    - 📋 To Do (generated)
    - ⚙️ In Progress (processing)
    - ✅ Completed (has run_id)
  - Status-based styling with color coding
  - Radio buttons (Manual Mode) or Checkboxes (Automated Mode)
  - Clickable Case IDs (opens report in new tab if completed)
  - View Report button (only for completed cases)
- **Case Actions**
  - View Case (opens email modal)
  - Delete Case (with confirmation)
  - Process Selected Case(s)
  - Select All Cases / Deselect All Cases
  - Delete All Cases (with confirmation)

#### **Email Preview Modal**

- Displays full email details:
  - From: CBA Refund System <refunds@cba.com.au>
  - To: Intelli Processing
  - Subject: Email subject from case data
  - Reference: Case ID
  - Date: Case creation timestamp
  - MT103 Message Body: Full formatted message
- Actions:
  - Process Case button
  - Save Draft button (placeholder)
- Modal functionality:
  - Click outside to close
  - Escape key to close
  - Close button (×)

#### **UI Components**

- **Toast Notification System**
  - Success, Error, Info toast types
  - Auto-dismiss after 5 seconds
  - Positioned at top-right
  - Smooth animations
- **Status Badges**
  - Color-coded status indicators
  - Animated transitions on state changes
- **Loading States**
  - Button loading indicators
  - Processing animations

### **2. Report View (report.html)**

#### **Page Structure**

- **Header Section**
  - Title: "Payment Refund Investigations"
  - Back button: "← Back to Investigation"
  - Subtitle: "Intelligent Payment Processing System"
  - Case ID display: Shows the associated case ID

#### **6-Step Progress Bar**

The report page features a **6-step progress bar** that controls the main content display. Each step is clickable and shows different information:

1. **Step 1: Case Investigation Starts** (Logger Agent)

   - Shows Logger Agent status and output
   - Displays: Case ID, UETR, E2E ID, Debtor Name, Debtor IBAN, Amount, Return Reason, Reason Info

2. **Step 2: Investigator Agent**

   - Shows Investigation Agent status and detailed output
   - Displays: UETR, E2E ID, IBAN, Return Reason, Reason Info, Auto Refund Eligible, Customer Valid, Cross Checks, Currency Mismatch

3. **Step 3: Verifier Agent**

   - Shows Verifier Agent status and validation results
   - Displays: Reconciliation OK, Sequence OK, Cross Checks OK, CSV Validation OK, Non Branch OK, Sanctions OK, FX Loss Within Limit, Nostro Match Found, Process Flow OK, Decision, Decision Reason

4. **Step 4: Communications Agent**

   - Shows Communications Agent status and notification details
   - Displays: Templates Generated, Customer Notification, Branch Advisory, Ops Advisory Priority, Decision Summary, Account Ops Count

5. **Step 5: Investigation Report** (Tabbed Interface)

   - Shows comprehensive report with **5 tabs**:
     - **Investigation Details**
     - **Detailed Process Overview**
     - **Interactive Agent Graph**
     - **Communication**
     - **Account Operations**

6. **Step 6: Case Final Status**
   - Shows final case status and closure details
   - Displays: Final Decision, Refund Status, Reason, Description, Case Status, Case Closure Summary, Next Actions

#### **Step 5 - Tabbed Report Interface**

##### **Tab 1: Investigation Details**

**Content Structure:**

- **Workflow Verdict Section**

  - Refund status badge
  - Manual Review Required indicator
  - Enhanced status
  - Final Verdict

- **Key Checks Section**

  - Sanctions: Passed/Failed
  - CSV Validation: Passed/Failed
  - Cross-Message: Passed/Failed
  - FX ≤ 300: Yes/No

- **Reason & Context Section**

  - Reason code (e.g., AC01)
  - Description
  - MT103 status

- **Transaction Summary Section**

  - UETR
  - End-to-End ID
  - Customer IBAN
  - Return Amount (with currency)
  - MT103 Status
  - FX Loss (AUD)
  - Channel Type
  - Sanctions Check
  - Auto-Refund Eligibility
  - Refund Decision
  - Notification
  - Final Status
  - Pending Until (date)
  - Case Type

- **Return Analysis Section**

  - Reason Code
  - Description
  - Action Required
  - Refund Note

- **Processing Outcomes Section**

  - Foreign Currency: Detected/Not Detected
  - Nostro Verification: Status
  - FCA Processing: Status
  - Payment: Status
  - Case Management: Status
  - Case Closure: Status

- **Eligibility Checklist Section**

  - AUD Refund: Yes/No/Not AUD
  - FX Loss Limit: Within/Exceeds
  - Channel Type: Branch/Non-branch
  - Sanctions: Passed/Failed
  - Sequence Check: Passed/Failed
  - Cross-Message Validation: Passed/Failed
  - Customer Validation: Passed/Failed

- **FX Details Section**
  - Currency Received
  - Original Amount
  - Returned Amount
  - Original Amount (AUD)
  - Returned Amount (AUD)
  - FX Rate (USD → AUD)
  - FX Loss

##### **Tab 2: Detailed Process Overview**

**Content Structure:**

- **Visual Decision Flow Section**

  - Pre-Flow Checklist visual flow diagram
  - Start → Email Rejection → Correct Payment → MT103/202 → Not AUD Payment → FX ≤ $300 → Manual Review

- **Refund Decision Tree (D1-D9) Section**

  - D1: FCY? (Foreign Currency?)
  - D2: Nostro?
  - D3: FCA?
  - D4: MT103/202?
  - D5: Amendment?
  - D6: No Charges?
  - D7: Branch?
  - D8: Markets?
  - D9: Email?
  - Each decision shows: Yes/No/N/A and outcome

- **Detailed Agent Results Section**

  - **Logger Agent** (Prepared)

    - Subject
    - Reference
    - Recipient (masked)
    - Email Body (MT103 format)

  - **Investigation Agent** (PASS/FAIL)

    - UETR
    - E2E ID
    - IBAN
    - Return Reason
    - Reason Info
    - Auto Refund Eligible
    - Customer Valid
    - Cross Checks
    - Currency Mismatch

  - **Actioning Agent** (Overview)

    - **FX Calculation**

      - Original Amount
      - Returned Amount
      - Original AUD
      - Returned AUD
      - FX Loss AUD
      - Exceeds $300
      - FCA Account Found
      - Calculation Method

    - **Checklist**

      - Email Rejection
      - Correct Payment
      - Has MT103/202
      - AUD Payment
      - Amendment Sent
      - CBA FCA Return
      - No Funds Due Charges
      - Return Reason Clear
      - Manual Review Required

    - **Nostro**

      - Match Found
      - Match Type
      - Nostro Entry

    - **Refund (D1–D9)**
      - Can Process
      - Final Action
      - Account Operations count
      - Credit Account IBAN

  - **Verifier Agent** (PASS/FAIL)

    - Reconciliation OK
    - Sequence OK
    - Cross Checks OK
    - CSV Validation OK
    - Non Branch OK
    - Sanctions OK
    - FX Loss Within Limit
    - Nostro Match Found
    - Process Flow OK

  - **Communications Agent** (PREPARED)
    - Templates Generated count
    - Customer Notification
    - Branch Advisory
    - Ops Advisory Priority
    - Decision Summary
    - Account Ops Count

##### **Tab 3: Interactive Agent Graph**

**Content Structure:**

- Interactive visual graph showing agent flow
- Hover tooltips showing data flowing through each agent
- Agent nodes:
  - 📝 Logger Agent (Data Preparation) - Completed
  - 🔍 Investigation Agent (Eligibility & Validation) - Completed
  - ⚙️ Actioning Agent (Processing & Decision) - Completed
    - Sub-agents: 💱 FX, ✅ Checklist, 🏦 Nostro, 💰 Refund
  - ✅ Verifier Agent (Final Validation) - Completed
  - 📧 Communications Agent (Notifications) - Completed
- Visual flow connections between agents
- Status indicators (✓ Completed, ⏳ Processing, etc.)

##### **Tab 4: Communication**

**Content Structure:**

- **Email Template Display**
  - To: Customer email (masked or full)
  - From: refunds@cba.com.au
  - Subject: Refund status email subject
  - Email Body: Full formatted customer notification email
    - Includes transaction details (UETR, Amount, Reason, FX Loss, Status)
    - Action Required section (if applicable)
    - Support contact information
    - Closing signature

##### **Tab 5: Account Operations**

**Content Structure:**

- **Balance Changes Summary Table**
  - Columns: Account, Type, Currency, Balance Before, Operation, Amount, Balance After, Net Change
  - Shows all account operations (DEBIT and CREDIT)
- **Detailed Operations Section**
  - Each operation shows:
    - Operation Type: DEBIT or CREDIT
    - Amount (with currency)
    - Account Name/IBAN
    - Balance Before
    - Balance After
    - Reference (E2E ID or transaction reference)
  - Grouped by operation type with visual distinction

#### **Step 6 - Case Final Status**

**Content Structure:**

- **Final Status Card**

  - Status indicator (✓ Completed, ⏳ Pending, etc.)
  - Description text

- **Final Decision Section**

  - Large verdict badge: "✅ APPROVE AND PROCESS REFUND" or other status
  - Final Case Status details:
    - Refund Status: Approved/Pending/Rejected
    - Reason: Description
    - Description of Reason: Code/Status
    - Case Status: Closed/Open/Pending

- **Case Closure Summary Section**
  - Case Closure Status: Success message or status
  - Next Actions: What happens next or required actions

#### **Report Data Structure**

The report is a JSON object with the following structure (based on API `/api/report/<identifier>`):

```typescript
interface ReportData {
  run_id: string;
  timestamp: string;
  transaction_id: string; // E2E ID
  uetr: string;
  case_id?: string;

  // Step 1: Logger Agent
  prep_logger?: {
    case_id?: string;
    email_payload?: {
      subject: string;
      body: string;
      reference: string;
    };
    email_recipient?: string;
    processing_timestamp?: string;
  };

  // Step 2: Investigation Agent
  investigation?: {
    summary: {
      uetr?: string;
      e2e_id?: string;
      customer_account?: string; // IBAN
      return_reason?: string; // e.g., AC01
      return_reason_info?: string;
      auto_refund_eligible?: boolean;
      customer_valid?: boolean;
      cross_checks?: string; // OK/FAIL
      currency_mismatch?: boolean;
    };
    eligibility?: {
      // Eligibility check results
    };
    cross_checks?: {
      // Cross-check results
    };
  };

  // Step 3: Verifier Agent
  verification?: {
    verifier_summary?: {
      checks?: {
        nostro_match_found?: boolean;
        match_type?: string;
        nostro_entry?: string;
      };
    };
    reconciliation_ok?: boolean;
    sequence_ok?: boolean;
    cross_checks_ok?: boolean;
    csv_validation_ok?: boolean;
    non_branch_ok?: boolean;
    sanctions_ok?: boolean;
    fx_loss_within_limit?: boolean;
    nostro_match_found?: boolean;
    process_flow_ok?: boolean;
    decision?: string; // approve_and_process, resend_to_investigator, human_intervention
    decision_reason?: string;
  };

  // Step 4: Communications Agent
  communications?: {
    email_payload?: {
      subject?: string;
      body?: string;
      to?: string;
      from?: string;
    };
    email_recipient?: string;
    templates_generated?: number;
    customer_notification?: string;
    branch_advisory?: string;
    ops_advisory_priority?: string;
    decision_summary?: string;
  };

  // Actioning Agent (shown in Tab 2)
  fx_calculation?: {
    original_amount?: number;
    returned_amount?: number;
    original_aud?: number;
    returned_aud?: number;
    fx_loss_aud?: number;
    exceeds_300?: boolean;
    fca_account_found?: boolean;
    calculation_method?: string;
  };

  flow_checklist?: {
    email_rejection?: boolean;
    correct_payment?: boolean;
    has_mt103_202?: boolean;
    aud_payment?: boolean;
    amendment_sent?: boolean;
    cba_fca_return?: boolean;
    no_funds_due_charges?: boolean;
    return_reason_clear?: boolean;
    manual_review_required?: boolean;
  };

  // Step 5 - Tab 5: Account Operations
  account_operations?: Array<{
    operation_type: "DEBIT" | "CREDIT";
    account_name?: string;
    account_iban: string;
    account_type?: string; // Nostro, Vostro, Other, etc.
    amount: number;
    currency: string;
    balance_before: number;
    balance_after: number;
    reference?: string; // E2E ID or transaction reference
  }>;

  // Decision flow results
  refund_decision?: {
    can_process?: boolean;
    final_action?: string;
    credit_account_iban?: string;
  };

  // Step 6: Final Status
  summary?: {
    can_process?: boolean;
    reason?: string;
    final_status?: string; // PENDING_5_BUSINESS_DAYS, etc.
    pending_until?: string; // ISO date
    case_type?: string; // FX Loss - No FCA Account, etc.
    refund_status?: string; // Approved, Pending, etc.
    case_status?: string; // Closed, Open, Pending
    case_closure_status?: string;
    next_actions?: string;
  };

  // PACS data
  parsed_pacs004?: {
    amount?: string;
    currency?: string;
    // ... other PACS.004 fields
  };

  parsed_pacs008?: {
    amount?: string;
    currency?: string;
    // ... other PACS.008 fields
  };
}
```

### **3. Simulation/Processing View (simulation.html)**

#### **Agent Flow Visualization**

- **Progress Bar**
  - 5-step cylindrical progress indicator
  - Step numbers (1-5) with active/completed states
  - Visual progress fill
  - Clickable steps (highlight corresponding agent section)
- **Agent Flow Steps**
  - Logger Agent (Step 1)
  - Investigation Agent (Step 2)
  - Actioning Agent (Step 3)
  - Verifier Agent (Step 4)
  - Communications Agent (Step 5)
- **Agent Cards**
  - Each agent displays:
    - Step number badge
    - Agent icon
    - Agent name and description
    - Status badge (Pending/Processing/Completed)
    - Output/result section
  - Progressive reveal animation
  - Scroll to active agent
  - Highlight on step click
- **Progress Tracking**
  - Real-time progress percentage
  - Status text updates
  - Completion button (redirects to report)

#### **Agent Processing States**

- **Pending**: Gray, inactive
- **Processing**: Yellow, animated pulse
- **Completed**: Green, static

---

## API Endpoints Reference

### **Case Management Endpoints**

#### `GET /api/cases`

- **Description**: List all generated cases
- **Response**: Array of case objects

```typescript
interface Case {
  case_id: string;
  description: string;
  amount: string;
  currency: string;
  status: "generated" | "processing" | "completed" | "failed";
  created_at: string; // ISO format
  run_id?: string; // Only if processed
  email_subject?: string;
  email_recipient?: string;
  email_body?: string;
}
```

#### `GET /api/cases/<case_id>`

- **Description**: Get full details of a specific case
- **Response**: Complete case object with PACS data and email data
- **Status Codes**: 200 (success), 404 (not found), 500 (error)

#### `DELETE /api/cases/<case_id>`

- **Description**: Delete a specific case
- **Response**: `{ success: boolean, message: string }`
- **Status Codes**: 200 (success), 404 (not found), 500 (error)

### **Report Endpoints**

#### `GET /api/report/<identifier>`

- **Description**: Get report data by run_id or case_id
- **Parameters**: `identifier` can be either a run_id or case_id
- **Response**: Complete report JSON object
- **Status Codes**: 200 (success), 404 (not found), 400 (case not processed), 500 (error)

#### `GET /api/reports`

- **Description**: List all available reports
- **Response**: Array of report summaries

```typescript
interface ReportSummary {
  run_id: string;
  timestamp: string;
  transaction_id: string;
  can_process: boolean;
  reason: string;
}
```

### **Processing Endpoints**

#### `POST /upload-pacs-preview`

- **Description**: Upload PACS files and generate email previews (no case creation)
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `pacs004_files`: File[] (multiple)
  - `pacs008_files`: File[] (multiple, must match count)
- **Response**:

```typescript
{
  success: boolean;
  message: string;
  email_previews?: Array<{
    index: number;
    pacs004_filename: string;
    pacs008_filename: string;
    debtor_name: string;
    amount: string;
    currency: string;
    email_subject: string;
    email_recipient: string;
    email_body: string;
    pacs004_data: {...};
    pacs008_data: {...};
    pacs004_content: string;
    pacs008_content: string;
    email_data: {...};
  }>;
}
```

#### `POST /create-cases-from-emails`

- **Description**: Create cases from email preview data
- **Content-Type**: `application/json`
- **Request Body**:

```typescript
{
  selected_indices: number[];
  email_previews: EmailPreview[];
}
```

- **Response**:

```typescript
{
  success: boolean;
  message: string;
  cases?: Case[];
}
```

#### `POST /process-cases`

- **Description**: Process one or more cases through the workflow
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `case_ids`: string[] (can be single or multiple)
- **Response**:

```typescript
{
  success: boolean;
  message: string;
  processed_cases?: Array<{
    case_id: string;
    run_id: string;
    status: "completed";
    result: {
      run_id: string;
      success: boolean;
      timestamp: string;
    };
  }>;
  failed_cases?: Array<{
    case_id: string;
    status: "failed";
    error: string;
  }>;
}
```

### **Page Routes**

#### `GET /`

- **Description**: Main dashboard (serves index.html in current implementation)
- **React Route**: `/` or `/dashboard`

#### `GET /report/<run_id>`

- **Description**: Report view page
- **Query Parameters**:
  - `mode`: "manual" | "automated" (optional)
  - `case_id`: string (optional)
- **React Route**: `/report/:runId`

#### `GET /simulation`

- **Description**: Agent flow simulation page
- **Query Parameters**: `run_id`: string (required)
- **React Route**: `/simulation?runId=:runId`

---

## React Implementation Requirements

### **Technology Stack Recommendations**

- **React**: 18.x or later
- **TypeScript**: For type safety
- **Routing**: React Router v6
- **State Management**:
  - React Context API for global state
  - React Query / TanStack Query for server state
- **HTTP Client**: Axios or Fetch API
- **UI Component Library** (Optional):
  - Material-UI (MUI) or
  - Ant Design or
  - Chakra UI or
  - Tailwind CSS + Headless UI
- **Form Handling**: React Hook Form
- **File Upload**: react-dropzone or custom implementation
- **Toast Notifications**: react-toastify or similar
- **Modal**: react-modal or similar

### **Project Structure**

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Modal.tsx
│   │   │   ├── Toast.tsx
│   │   │   ├── Spinner.tsx
│   │   │   ├── Button.tsx
│   │   │   └── Badge.tsx
│   │   ├── dashboard/
│   │   │   ├── CaseDashboard.tsx
│   │   │   ├── CaseTable.tsx
│   │   │   ├── UploadForm.tsx
│   │   │   ├── EmailPreviewList.tsx
│   │   │   ├── EmailPreviewItem.tsx
│   │   │   ├── ModeToggle.tsx
│   │   │   └── CaseViewModal.tsx
│   │   └── report/
│   │       ├── ReportView.tsx
│   │       ├── ReportProgressBar.tsx
│   │       ├── ReportTabs.tsx
│   │       ├── InvestigationDetailsTab.tsx
│   │       ├── ProcessOverviewTab.tsx
│   │       ├── InteractiveAgentGraph.tsx
│   │       ├── CommunicationTab.tsx
│   │       ├── AccountOperationsTab.tsx
│   │       ├── AgentStepContent.tsx
│   │       └── SimulationView.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Report.tsx
│   │   └── Simulation.tsx
│   ├── services/
│   │   ├── apiService.ts
│   │   ├── caseService.ts
│   │   ├── reportService.ts
│   │   └── uploadService.ts
│   ├── hooks/
│   │   ├── useCases.ts
│   │   ├── useReports.ts
│   │   ├── useFileUpload.ts
│   │   └── useToast.ts
│   ├── types/
│   │   ├── case.types.ts
│   │   ├── report.types.ts
│   │   └── api.types.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   ├── context/
│   │   ├── AppContext.tsx
│   │   └── ThemeContext.tsx (optional)
│   ├── App.tsx
│   ├── index.tsx
│   └── index.css
├── public/
├── package.json
├── tsconfig.json
└── vite.config.ts (or webpack.config.js)
```

### **Key Components to Implement**

#### **1. Dashboard Page (`pages/Dashboard.tsx`)**

**Requirements**:

- Implement mode toggle (Manual/Automated)
- Conditionally render upload section based on mode
- Display cases table with proper selection handling
- Handle email preview flow
- Manage case creation and processing
- Real-time status updates

**State Management**:

```typescript
interface DashboardState {
  mode: "manual" | "automated";
  cases: Case[];
  selectedCaseIds: string[];
  emailPreviews: EmailPreview[];
  selectedEmailIndices: number[];
  isLoading: boolean;
  error: string | null;
}
```

**Key Functionality**:

- Load cases on mount
- Handle file upload and preview generation
- Create cases from email previews
- Process selected cases
- Update case status in real-time
- Navigate to report after processing

#### **2. Case Table Component (`components/dashboard/CaseTable.tsx`)**

**Requirements**:

- Render cases in a responsive table
- Support both radio (manual) and checkbox (automated) selection
- Display case status with badges
- Show action buttons (View, Delete)
- Handle row selection
- Link to reports for completed cases
- Update selection based on mode

**Props**:

```typescript
interface CaseTableProps {
  cases: Case[];
  mode: "manual" | "automated";
  selectedCaseIds: string[];
  onSelectionChange: (caseIds: string[]) => void;
  onView: (caseId: string) => void;
  onDelete: (caseId: string) => void;
  onProcess: (caseIds: string[]) => void;
}
```

#### **3. Email Preview List (`components/dashboard/EmailPreviewList.tsx`)**

**Requirements**:

- Display list of email previews
- Allow selection via checkboxes
- Show email content in formatted containers
- Display PACS pair information
- Provide Select All / Deselect All functionality
- Handle case creation from selected previews

**Props**:

```typescript
interface EmailPreviewListProps {
  previews: EmailPreview[];
  selectedIndices: number[];
  onSelectionChange: (indices: number[]) => void;
  onCreateCases: (indices: number[]) => void;
}
```

#### **4. Report View (`pages/Report.tsx`)**

**Requirements**:

- Load report data by run_id or case_id
- Implement **6-step progress bar** that controls content display
- Each step is clickable and shows different content
- Display report in tabbed interface (Step 5)
- Show all report sections based on selected step
- Handle navigation from different contexts
- Support deep linking with URL parameters
- Back button navigation to dashboard

**Route**: `/report/:runId`

**Query Parameters**:

- `mode`: Processing mode context (optional)
- `case_id`: Associated case ID (optional)

**Component Structure**:

```typescript
interface ReportViewState {
  activeStep: 1 | 2 | 3 | 4 | 5 | 6;
  activeTab:
    | "investigation"
    | "process"
    | "graph"
    | "communication"
    | "operations";
  reportData: ReportData | null;
  isLoading: boolean;
  error: string | null;
}
```

**Progress Bar Steps**:

1. **Step 1**: Show Logger Agent details and output
2. **Step 2**: Show Investigation Agent results
3. **Step 3**: Show Verifier Agent validation results
4. **Step 4**: Show Communications Agent notification details
5. **Step 5**: Show tabbed report interface (default active tab: Investigation Details)
6. **Step 6**: Show final case status and closure summary

**Tabbed Interface (Step 5)**:

- **Tab 1: Investigation Details**
  - Multiple sections with structured data
  - Status badges and indicators
  - Tables for checklist items
  - FX calculation details
- **Tab 2: Detailed Process Overview**
  - Visual decision flow diagram
  - D1-D9 decision tree visualization
  - Detailed agent results with expandable sections
- **Tab 3: Interactive Agent Graph**
  - SVG or canvas-based agent flow visualization
  - Interactive hover tooltips
  - Status indicators on agent nodes
- **Tab 4: Communication**
  - Formatted email template display
  - Read-only email preview
- **Tab 5: Account Operations**
  - Balance changes summary table
  - Detailed operations list grouped by type
  - Balance calculations display

#### **Report View Sub-Components**

##### **ReportProgressBar (`components/report/ReportProgressBar.tsx`)**

**Requirements**:

- Render 6-step progress indicator
- Each step is clickable
- Visual active/completed states
- Step labels:
  1. "Case Investigation Starts"
  2. "Investigator Agent"
  3. "Verifier Agent"
  4. "Communications Agent"
  5. "Investigation Report"
  6. "Case Final Status"
- Highlight active step
- Show completion status for each step

**Props**:

```typescript
interface ReportProgressBarProps {
  activeStep: 1 | 2 | 3 | 4 | 5 | 6;
  onStepClick: (step: number) => void;
  completedSteps?: number[]; // Steps that are completed
}
```

##### **ReportTabs (`components/report/ReportTabs.tsx`)**

**Requirements**:

- Render 5 tabs with icons and labels:
  - Investigation Details (default active)
  - Detailed Process Overview
  - Interactive Agent Graph
  - Communication
  - Account Operations
- Tab switching with smooth transitions
- Active tab highlighting
- Content rendering based on active tab

**Props**:

```typescript
interface ReportTabsProps {
  activeTab:
    | "investigation"
    | "process"
    | "graph"
    | "communication"
    | "operations";
  onTabChange: (tab: string) => void;
  reportData: ReportData;
}
```

##### **InvestigationDetailsTab (`components/report/InvestigationDetailsTab.tsx`)**

**Requirements**:

- Render all sections from Tab 1: Investigation Details
- Format data with proper badges and indicators
- Display tables for structured data
- Show status indicators with color coding
- Handle empty/null values gracefully

**Props**:

```typescript
interface InvestigationDetailsTabProps {
  reportData: ReportData;
}
```

##### **ProcessOverviewTab (`components/report/ProcessOverviewTab.tsx`)**

**Requirements**:

- Render visual decision flow diagram
- Display D1-D9 decision tree with outcomes
- Show detailed agent results with expandable sections
- Format agent outputs consistently
- Visual flow indicators

**Props**:

```typescript
interface ProcessOverviewTabProps {
  reportData: ReportData;
}
```

##### **InteractiveAgentGraph (`components/report/InteractiveAgentGraph.tsx`)**

**Requirements**:

- Render SVG or canvas-based agent flow visualization
- Display agent nodes with icons and labels
- Show connections between agents
- Hover tooltips with agent data
- Status indicators (Completed, Processing, Pending)
- Sub-agent visualization for Actioning Agent

**Props**:

```typescript
interface InteractiveAgentGraphProps {
  reportData: ReportData;
}
```

##### **CommunicationTab (`components/report/CommunicationTab.tsx`)**

**Requirements**:

- Display formatted email template
- Show To, From, Subject fields
- Render email body with proper formatting
- Mask sensitive information if needed
- Read-only display

**Props**:

```typescript
interface CommunicationTabProps {
  reportData: ReportData;
}
```

##### **AccountOperationsTab (`components/report/AccountOperationsTab.tsx`)**

**Requirements**:

- Render balance changes summary table
- Display detailed operations grouped by type
- Format currency values properly
- Show balance calculations
- Visual distinction between DEBIT and CREDIT operations

**Props**:

```typescript
interface AccountOperationsTabProps {
  reportData: ReportData;
}
```

##### **AgentStepContent (`components/report/AgentStepContent.tsx`)**

**Requirements**:

- Render content for Steps 1-4 and Step 6
- Display agent-specific information
- Format output data consistently
- Show agent status and icon
- Handle different agent types

**Props**:

```typescript
interface AgentStepContentProps {
  step: 1 | 2 | 3 | 4 | 6;
  reportData: ReportData;
}
```

#### **5. Simulation View (`pages/Simulation.tsx`)**

**Requirements**:

- Display agent flow visualization
- Show progress bar with 5 steps
- Animate agent processing
- Display agent outputs
- Handle step highlighting on click
- Redirect to report on completion

**Route**: `/simulation?runId=:runId`

**Agent Flow Configuration**:

```typescript
const AGENT_STEPS = [
  { step: 1, id: "logger", name: "Logger Agent", icon: "📝", duration: 2000 },
  {
    step: 2,
    id: "investigator",
    name: "Investigation Agent",
    icon: "🔍",
    duration: 3000,
  },
  {
    step: 3,
    id: "actioning",
    name: "Actioning Agent",
    icon: "⚙️",
    duration: 4000,
  },
  {
    step: 4,
    id: "verifier",
    name: "Verifier Agent",
    icon: "✅",
    duration: 2500,
  },
  {
    step: 5,
    id: "communications",
    name: "Communications Agent",
    icon: "📧",
    duration: 2500,
  },
];
```

### **API Service Implementation**

#### **Base API Service (`services/apiService.ts`)**

```typescript
const API_BASE_URL = "http://localhost:5000";

class ApiService {
  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }

  async uploadFile<T>(endpoint: string, formData: FormData): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiService = new ApiService();
```

#### **Case Service (`services/caseService.ts`)**

```typescript
export const caseService = {
  getAll: () => apiService.get<Case[]>("/api/cases"),

  getById: (caseId: string) => apiService.get<Case>(`/api/cases/${caseId}`),

  delete: (caseId: string) =>
    apiService.delete<{ success: boolean; message: string }>(
      `/api/cases/${caseId}`
    ),

  process: (caseIds: string[]) => {
    const formData = new FormData();
    caseIds.forEach((id) => formData.append("case_ids", id));
    return apiService.uploadFile<ProcessCasesResponse>(
      "/process-cases",
      formData
    );
  },
};
```

#### **Report Service (`services/reportService.ts`)**

```typescript
export const reportService = {
  getById: (identifier: string) =>
    apiService.get<ReportData>(`/api/report/${identifier}`),

  getAll: () => apiService.get<ReportSummary[]>("/api/reports"),
};
```

#### **Upload Service (`services/uploadService.ts`)**

```typescript
export const uploadService = {
  previewEmails: (pacs004Files: File[], pacs008Files: File[]) => {
    const formData = new FormData();
    pacs004Files.forEach((file) => formData.append("pacs004_files", file));
    pacs008Files.forEach((file) => formData.append("pacs008_files", file));
    return apiService.uploadFile<EmailPreviewResponse>(
      "/upload-pacs-preview",
      formData
    );
  },

  createCases: (selectedIndices: number[], emailPreviews: EmailPreview[]) =>
    apiService.post<CreateCasesResponse>("/create-cases-from-emails", {
      selected_indices: selectedIndices,
      email_previews: emailPreviews,
    }),
};
```

### **State Management Strategy**

#### **React Query for Server State**

```typescript
// hooks/useCases.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export const useCases = () => {
  const queryClient = useQueryClient();

  const {
    data: cases,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["cases"],
    queryFn: () => caseService.getAll(),
    refetchInterval: 5000, // Poll every 5 seconds for updates
  });

  const deleteMutation = useMutation({
    mutationFn: caseService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cases"] });
    },
  });

  const processMutation = useMutation({
    mutationFn: caseService.process,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["cases"] });
      return data;
    },
  });

  return {
    cases: cases || [],
    isLoading,
    error,
    deleteCase: deleteMutation.mutate,
    processCases: processMutation.mutate,
    isProcessing: processMutation.isPending,
  };
};
```

#### **Context API for UI State**

```typescript
// context/AppContext.tsx
interface AppContextType {
  mode: "manual" | "automated";
  setMode: (mode: "manual" | "automated") => void;
  selectedCaseIds: string[];
  setSelectedCaseIds: (ids: string[]) => void;
  toast: (message: string, type: "success" | "error" | "info") => void;
}

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [mode, setMode] = useState<"manual" | "automated">("manual");
  const [selectedCaseIds, setSelectedCaseIds] = useState<string[]>([]);

  // Toast implementation

  return (
    <AppContext.Provider
      value={{ mode, setMode, selectedCaseIds, setSelectedCaseIds, toast }}
    >
      {children}
    </AppContext.Provider>
  );
};
```

### **Styling Approach**

#### **Option 1: CSS Modules**

- Create component-specific CSS modules
- Maintain current design aesthetic
- Golden/black color scheme

#### **Option 2: Tailwind CSS**

- Utility-first CSS
- Faster development
- Consistent design system

#### **Option 3: Styled Components**

- Component-scoped styling
- Dynamic styling based on props
- Better TypeScript integration

**Recommended**: Tailwind CSS with custom configuration to match current design:

- Golden gradient: `#ffd700` to `#ffed4e`
- Black header: `#000000` to `#1a1a1a`
- Professional card-based layout

### **Routing Configuration**

```typescript
// App.tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/report/:runId" element={<Report />} />
        <Route path="/simulation" element={<Simulation />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### **Error Handling**

- Implement error boundaries for component-level errors
- API error handling with user-friendly messages
- Network error detection and retry logic
- Loading states for all async operations
- Toast notifications for success/error states

### **Accessibility Requirements**

- Keyboard navigation support
- ARIA labels for interactive elements
- Focus management for modals
- Screen reader compatibility
- Color contrast compliance (WCAG AA minimum)

---

## Migration Checklist

### **Phase 1: Setup & Infrastructure**

- [ ] Initialize React project (Vite or Create React App)
- [ ] Configure TypeScript
- [ ] Set up routing (React Router)
- [ ] Configure API service layer
- [ ] Set up state management (React Query + Context)
- [ ] Configure build tools
- [ ] Set up environment variables for API URL

### **Phase 2: Core Components**

- [ ] Implement common components (Modal, Toast, Spinner, Button, Badge)
- [ ] Create layout components (Header, Footer, Navigation)
- [ ] Build form components (FileUpload, Select, Checkbox, Radio)
- [ ] Implement table components (CaseTable with selection)

### **Phase 3: Dashboard Page**

- [ ] Implement mode toggle
- [ ] Build file upload section
- [ ] Create email preview list
- [ ] Build case table with selection
- [ ] Implement email modal
- [ ] Add toast notifications
- [ ] Handle case processing flow

### **Phase 4: Report Page**

- [ ] Implement report data loading
- [ ] Create tabbed interface
- [ ] Build report sections (Investigation, Account Operations, etc.)
- [ ] Add navigation handling
- [ ] Implement deep linking

### **Phase 5: Simulation Page**

- [ ] Create agent flow visualization
- [ ] Implement progress bar
- [ ] Build agent cards
- [ ] Add animations and transitions
- [ ] Handle step highlighting

### **Phase 6: Polish & Testing**

- [ ] Responsive design testing
- [ ] Cross-browser compatibility
- [ ] Performance optimization
- [ ] Error handling refinement
- [ ] Accessibility audit
- [ ] User acceptance testing

---

## Key Implementation Details

### **File Upload Handling**

```typescript
const handleFileUpload = async (pacs004Files: File[], pacs008Files: File[]) => {
  if (pacs004Files.length !== pacs008Files.length) {
    toast("PACS.004 and PACS.008 file counts must match", "error");
    return;
  }

  try {
    setIsLoading(true);
    const response = await uploadService.previewEmails(
      pacs004Files,
      pacs008Files
    );
    if (response.success) {
      setEmailPreviews(response.email_previews || []);
      toast(
        `Successfully processed ${response.email_previews?.length} PACS pair(s)!`,
        "success"
      );
    }
  } catch (error) {
    toast(`Upload failed: ${error.message}`, "error");
  } finally {
    setIsLoading(false);
  }
};
```

### **Case Processing Flow**

```typescript
const handleProcessCases = async (caseIds: string[]) => {
  try {
    setIsProcessing(true);
    const response = await caseService.process(caseIds);

    if (response.success && response.processed_cases) {
      // Update local state
      updateCasesStatus(response.processed_cases);

      // Navigate to report for single case
      if (caseIds.length === 1 && response.processed_cases[0]?.run_id) {
        navigate(`/report/${response.processed_cases[0].run_id}`);
      } else {
        // Refresh cases list
        refetchCases();
        toast(
          `Successfully processed ${response.processed_cases.length} case(s)`,
          "success"
        );
      }
    }
  } catch (error) {
    toast(`Processing failed: ${error.message}`, "error");
  } finally {
    setIsProcessing(false);
  }
};
```

### **Real-time Status Updates**

Use React Query's `refetchInterval` or polling to update case status:

```typescript
const { data: cases } = useQuery({
  queryKey: ["cases"],
  queryFn: () => caseService.getAll(),
  refetchInterval: (query) => {
    // Only poll if there are processing cases
    const hasProcessing = query.state.data?.some(
      (c) => c.status === "processing"
    );
    return hasProcessing ? 3000 : false;
  },
});
```

### **URL Parameter Handling**

```typescript
// Report page
const Report = () => {
  const { runId } = useParams<{ runId: string }>();
  const [searchParams] = useSearchParams();
  const mode = searchParams.get("mode") || "manual";
  const caseId = searchParams.get("case_id");

  // Load report data
  const { data: report } = useQuery({
    queryKey: ["report", runId],
    queryFn: () => reportService.getById(runId!),
    enabled: !!runId,
  });

  // ...
};
```

### **6-Step Progress Bar Implementation**

```typescript
// Report page with progress bar
const Report = () => {
  const [activeStep, setActiveStep] = useState<1 | 2 | 3 | 4 | 5 | 6>(5);
  const [activeTab, setActiveTab] = useState<
    "investigation" | "process" | "graph" | "communication" | "operations"
  >("investigation");

  const { data: report } = useQuery({
    queryKey: ["report", runId],
    queryFn: () => reportService.getById(runId!),
    enabled: !!runId,
  });

  const handleStepClick = (step: number) => {
    setActiveStep(step as 1 | 2 | 3 | 4 | 5 | 6);
    // Reset to default tab when switching to Step 5
    if (step === 5) {
      setActiveTab("investigation");
    }
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 1:
        return <AgentStepContent step={1} reportData={report} />;
      case 2:
        return <AgentStepContent step={2} reportData={report} />;
      case 3:
        return <AgentStepContent step={3} reportData={report} />;
      case 4:
        return <AgentStepContent step={4} reportData={report} />;
      case 5:
        return (
          <ReportTabs
            activeTab={activeTab}
            onTabChange={setActiveTab}
            reportData={report}
          />
        );
      case 6:
        return <AgentStepContent step={6} reportData={report} />;
      default:
        return null;
    }
  };

  return (
    <div>
      <ReportProgressBar
        activeStep={activeStep}
        onStepClick={handleStepClick}
        completedSteps={[1, 2, 3, 4, 5, 6]} // Based on report data
      />
      {renderStepContent()}
    </div>
  );
};
```

### **Tabbed Interface Implementation**

```typescript
// ReportTabs component
const ReportTabs = ({
  activeTab,
  onTabChange,
  reportData,
}: ReportTabsProps) => {
  const tabs = [
    { id: "investigation", label: "Investigation Details", icon: "📊" },
    { id: "process", label: "Detailed Process Overview", icon: "📋" },
    { id: "graph", label: "Interactive Agent Graph", icon: "🔗" },
    { id: "communication", label: "Communication", icon: "📧" },
    { id: "operations", label: "Account Operations", icon: "💰" },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case "investigation":
        return <InvestigationDetailsTab reportData={reportData} />;
      case "process":
        return <ProcessOverviewTab reportData={reportData} />;
      case "graph":
        return <InteractiveAgentGraph reportData={reportData} />;
      case "communication":
        return <CommunicationTab reportData={reportData} />;
      case "operations":
        return <AccountOperationsTab reportData={reportData} />;
      default:
        return null;
    }
  };

  return (
    <div>
      <div className="tabs-header">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={activeTab === tab.id ? "active" : ""}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>
      <div className="tabs-content">{renderTabContent()}</div>
    </div>
  );
};
```

---

## Design System Reference

### **Color Palette**

- **Primary Gold**: `#ffd700` (Golden gradient start)
- **Secondary Gold**: `#ffed4e` (Golden gradient end)
- **Black Header**: `#000000` to `#1a1a1a`
- **Success Green**: `#10b981` / `#28a745`
- **Error Red**: `#ef4444` / `#dc3545`
- **Warning Yellow**: `#ffc107` / `#f59e0b`
- **Info Blue**: `#3b82f6` / `#0ea5e9`
- **Background**: `#f6f8fb` / `#ffffff`
- **Text Dark**: `#111827` / `#212529`
- **Text Medium**: `#6b7280` / `#6c757d`
- **Border**: `#e5e7eb` / `#dee2e6`

### **Typography**

- **Font Family**: `"Segoe UI", Tahoma, Geneva, Verdana, sans-serif`
- **Header H1**: `2.4rem`, `font-weight: 600`
- **Header H2**: `1.5rem`, `font-weight: 600`
- **Body**: `1rem`, `font-weight: 400`
- **Small**: `0.8rem` - `0.9rem`

### **Spacing**

- **Card Padding**: `24px` - `32px`
- **Section Gap**: `20px` - `24px`
- **Element Gap**: `8px` - `16px`
- **Border Radius**: `8px` - `12px`

### **Shadows**

- **Card Shadow**: `0 2px 8px rgba(0, 0, 0, 0.1)`
- **Hover Shadow**: `0 4px 12px rgba(0, 0, 0, 0.15)`
- **Modal Shadow**: `0 10px 30px rgba(0, 0, 0, 0.3)`

---

## Testing Strategy

### **Unit Tests**

- Component rendering tests
- Hook tests (custom hooks)
- Utility function tests
- API service tests (mocked)

### **Integration Tests**

- User flow tests (upload → preview → create → process)
- API integration tests
- Routing tests

### **E2E Tests** (Optional)

- Full workflow automation
- Cross-browser testing
- Performance testing

---

## Deployment Considerations

### **Development**

- Proxy API requests through Vite dev server
- Hot module replacement
- Source maps for debugging

### **Production**

- Build optimization
- Environment variable configuration
- Static asset optimization
- API URL configuration

### **Build Configuration**

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
```

---

## Notes & Considerations

1. **Backend Compatibility**: Ensure React app works with existing Flask backend. No backend changes should be required.

2. **CORS**: Backend has CORS enabled, but verify it works with React app origin.

3. **File Upload**: Handle large file uploads gracefully with progress indicators.

4. **Error Messages**: Provide user-friendly error messages, especially for file validation.

5. **Loading States**: Show loading indicators for all async operations.

6. **Responsive Design**: Ensure mobile-friendly layout (current design has some responsive considerations).

7. **Browser Support**: Target modern browsers (Chrome, Firefox, Edge, Safari latest versions).

8. **Performance**: Optimize for large case lists (pagination may be needed for 100+ cases).

9. **Accessibility**: Maintain or improve accessibility compared to current HTML implementation.

10. **Documentation**: Document component APIs and usage patterns as you build.

---

## Getting Started

1. **Review this document** thoroughly
2. **Set up React project** with recommended tooling
3. **Start with common components** (Button, Modal, Toast)
4. **Build Dashboard page** incrementally
5. **Test each feature** as you implement
6. **Iterate based on** user feedback and testing

---

**This prompt provides everything needed to rebuild the frontend as a React application while maintaining all existing functionality and improving the user experience with modern React patterns and best practices.**
