# CBA Unified Refund Processing System

Modern case management for ISO 20022 refund investigations, backed by an agent-driven Flask pipeline and a React operations console. The system orchestrates PACS.004 / PACS.008 message reconciliation, decisioning, audit logging, and MT103-style email generation.

## Highlights

- **Agent orchestration:** `investigator`, `verifier`, `refund`, `logverifier`, and `comms` agents execute the D1–D9 flow defined in `refund_flow_.md`.
- **Structured data layer:** CSV repositories (`app/utils/csv_repositories.py`) and helpers manage balances, ledgers, and statements while remaining swappable with the SQLite adapters.
- **Case lifecycle automation:** Case files, duplicate detection, processing status, and JSON reports are coordinated through Flask endpoints (`cases/`, `csv_reports/`).
- **React front end:** The `FrontendReact` app exposes dashboards for PACS pair intake, case queues, email preview, processing, and report review, replacing the legacy Flask templates.

## System Architecture

- **Backend (`app/`)**
  - Flask service in `app/web.py` exposes case management APIs, PACS ingestion routes, and report download endpoints.
  - Agent graph (`app/graph.py`) bundles the investigation, verification, refund, logging, and communication agents.
  - Utilities in `app/utils/` cover ISO parsing, FX loss calculations, MT103 rendering, repository abstractions, and audit logging.
- **Frontend (`FrontendReact/`)**
  - Vite + React + TypeScript UI with light/dark theming, toasts, and modal-driven review flows.
  - `services.ts` calls the Flask API via `API_BASE_URL` (default `http://localhost:5000`).
- **Persistent artifacts**
  - `cases/` contains generated case JSON dossiers.
  - `csv_reports/` stores run outputs, including decision traces and account operations.
  - `data/` supplies seed CSVs for accounts, customers, ledgers, statements, and audit trails.

## Getting Started

### 1. Backend setup

```bash
python -m venv .venv
.venv\Scripts\activate              # On Windows
pip install -r requirements.txt
python app/web.py                   # Runs on http://localhost:5000
```

Environment variables are read from `.env` if present. The server enables CORS so the React dev server can call it directly.

### 2. Frontend setup

```bash
cd FrontendReact
npm install
npm run dev                         # Opens http://localhost:5173
```

Configure `API_BASE_URL` in `FrontendReact/constants.ts` if your backend runs on a different host/port. For production builds run `npm run build` and serve the `dist/` output with your preferred static host.

### 3. Processing workflow

1. Launch both servers.
2. In the React dashboard, switch between **Manual** or **Automated** queues.
3. Upload PACS.004 / PACS.008 pairs or reuse bundled samples from `samples/`.
4. Generate email previews, create cases, and process them. Duplicate case IDs or transaction references are flagged server-side.
5. Open the report viewer for decision flow, account operations, audit summaries, and generated MT103 content.

## Key Directories & Data

- `data/`: CSV sources for accounts, customers, ledger, statements, audit log, and FX references.
- `cases/`: Serialized case metadata, inputs, and status.
- `csv_reports/`: JSON reports keyed by run ID.
- `samples/`: Reference PACS scenarios for demos and regression checks.

## API Surface (Flask)

- `POST /upload-pacs-preview` – stage PACS files and return MT103 email previews.
- `POST /create-cases-from-emails` – persist cases from selected previews.
- `GET /api/cases` / `GET /api/cases/<case_id>` – list and inspect case metadata.
- `POST /process-cases` – trigger agent processing for selected case IDs.
- `GET /api/reports` / `GET /api/report/<identifier>` – list and fetch report payloads.
- `POST /api/regenerate-email` – rerun MT103 email generation for a processed run.
- Additional helper routes (`/api/pacs-pairs`, `/api/create-case-from-files`, etc.) power dashboard workflows.

## Project Structure (abridged)

```
cba/
├── app/
│   ├── agents/
│   │   ├── investigator.py       # Parse PACS, validate customers, FX loss
│   │   ├── verifier.py           # MT940 reconciliation & compliance checks
│   │   ├── refund.py             # D1–D9 decision engine
│   │   ├── logverifier.py        # Audit aggregation & report shaping
│   │   ├── comms.py              # MT103 / notification payloads
│   │   └── loggerAg.py           # Email generation helper
│   ├── utils/                    # CSV repositories, FX utilities, XML parsers, etc.
│   ├── graph.py                  # Agent graph wiring
│   └── web.py                    # Flask application entry point
├── FrontendReact/                # React + Vite dashboard
├── cases/                        # Case JSON dossiers
├── csv_reports/                  # Investigation outputs
├── data/                         # Seed CSV datasets & SQLite placeholder
├── samples/                      # Example PACS files
├── refund_flow_.md               # Decision flow reference
├── flow_.md                      # Legacy pipeline notes
└── README.md
```

## Support & Troubleshooting

- Ensure both servers are running and reachable (CORS errors usually mean the backend is offline).
- Report JSON corruption warnings from `app/web.py` indicate partially written report files; remove the affected JSON in `csv_reports/` and rerun the case.
- Use the dashboard’s delete controls or remove files from `cases/` / `csv_reports/` manually to reset state.
- Update `data/` CSVs cautiously—balances and audit trails rely on consistent headers.

---

With the React dashboard and agent pipeline running together, you can ingest PACS investigations end-to-end, review case history, and ship MT103 notifications in one flow. Happy processing! 🚀
