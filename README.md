# CBA Unified Refund Processing System

🌐 _Agent-guided ISO 20022 investigations with a polished React control center and automated audit trails._

## ✨ Overview

- **Agent pipeline:** `investigator`, `verifier`, `refund`, `logverifier`, and `comms` agents collaborate through the D1–D9 decision journey (`refund_flow_.md`).
- **Modern UI:** The React dashboard (`FrontendReact/`) replaces legacy Flask templates with case queues, PACS pair wizards, and MT103 preview tooling.
- **Data fidelity:** CSV repositories (`app/utils/csv_repositories.py`) power balance tracking, ledger updates, and audit history while remaining swappable with SQLite adapters.
- **End-to-end traceability:** Each run writes a JSON report in `csv_reports/` and a case dossier in `cases/`, tying PACS inputs to FX results and outbound communications.

## 🧭 Quickstart Paths

### 1. One-command setup (recommended)

Run the interactive bootstrapper to create the virtual environment, install backend dependencies, and verify sample data:

```bash
python setup.py
```

What it does for you:
- Checks for Python 3.8+
- Creates `.venv` if missing
- Installs `requirements.txt`
- Creates helper directories and validates sample XMLs  

Next steps are printed at the end, including how to launch servers with or without the batch script.

### 2. Manual backend setup

```bash
python -m venv .venv
.venv\Scripts\activate              # On Windows (use source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python -m app.web                   # Serves the API at http://localhost:5000
```

Environment variables load from `.env` when available. CORS is enabled so the React client can talk to the API during development.

### 3. Frontend dashboard

```bash
cd FrontendReact
npm install
npm run dev                         # Runs on http://localhost:3000
```

The dashboard uses Vite with a custom `3000` dev port and reads the backend base URL from `FrontendReact/constants.ts` (`API_BASE_URL`).

### 4. Windows fast-launch script

Prefer an “everything boot” experience? Use the bundled batch file:

```powershell
start.bat
```

It activates `.venv`, installs frontend dependencies on first run, and opens two terminals:
- **Backend server:** `python -m app.web` on `http://localhost:5000`
- **Frontend server:** `npm run dev` on `http://localhost:3000`  

Close either window to stop that server; the batch console can be closed without interrupting the running services.

## 🔄 Case Processing Flow

1. Launch the backend and frontend.
2. Upload or select PACS.004 / PACS.008 pairs (sample files live in `samples/`).
3. Generate MT103 previews, choose the variants you want, and create cases.
4. Process cases (manual or automated queue). Duplicate transaction references are flagged before re-ingestion.
5. Inspect reports for decision path, balance movements, audit events, and email payloads.

## 🗂️ Key Directories

- `app/agents/` – Agent implementations for investigation, verification, refunds, audit logging, and communications.
- `app/utils/` – CSV repositories, FX helpers, XML parsers, audit utilities, and MT103 rendering.
- `app/graph.py` – Wiring for the LangGraph-style agent pipeline.
- `app/web.py` – Flask application configuring routes for cases, reports, PACS upload, and email generation.
- `FrontendReact/` – React + TypeScript dashboard (Vite config pins the dev port to 3000).
- `cases/` – Persisted case JSON dossiers.
- `csv_reports/` – Run reports containing decision trails and account operations.
- `data/` – Seed CSVs (accounts, customers, ledgers, statements, audit logs).
- `samples/` – ISO 20022 scenarios for demos and regression checks.

## 🔌 Core API Surface (Flask)

- `POST /upload-pacs-preview` – Stage PACS files and return MT103 previews.
- `POST /create-cases-from-emails` – Persist cases from selected previews.
- `GET /api/cases` / `GET /api/cases/<case_id>` – List and inspect case metadata.
- `POST /process-cases` – Trigger agent processing for selected case IDs.
- `GET /api/reports` / `GET /api/report/<identifier>` – Browse and fetch report payloads.
- `POST /api/regenerate-email` – Re-run MT103 generation for completed runs.
- Helper routes (`/api/pacs-pairs`, `/api/create-case-from-files`, etc.) support dashboard workflows.

## 🛠️ Troubleshooting & Tips

- If `start.bat` cannot find `.venv`, run `python setup.py` first.
- Delete stale JSON files from `csv_reports/` if a run report looks corrupted; reprocess the case afterward.
- Keep the CSV headers intact when editing anything in `data/`—repository loaders expect consistent schemas.
- Adjust `API_BASE_URL` if the backend runs on a different host or through a tunnel.
- For production, build the frontend (`npm run build`) and host the `dist/` folder behind your preferred static server.

---

🚀 With the React dashboard, agent pipeline, and automation scripts working together, you can ingest PACS investigations end-to-end, validate FX outcomes, and ship MT103 notifications with confidence.
