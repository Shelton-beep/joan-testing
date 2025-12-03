## Zero-Trust Anomaly Detection Platform (Backend + Next.js Frontend)

### 1. Overview

This repository contains an end‑to‑end **Zero‑Trust Anomaly Detection** platform for authentication logs:

- **Backend (Python / FastAPI)** under `backend/`

  - Trained Isolation Forest–based anomaly model, scaler and preprocessing.
  - REST API for **real‑time login scoring** and **analytics**.
  - Zero‑Trust policy: any `event_label != "normal"` is treated as an anomaly.
  - **Email alerts** on anomalous logins.
  - Real‑time event logging to `backend/data/realtime_events.csv`.

- **Frontend (Next.js / TypeScript)** under `frontend/`
  - **Landing page** at `/` explaining the system.
  - **User login UI** at `/user` that calls the backend `/predict` endpoint.
  - **SOC / admin dashboard** at `/dashboard` that visualises metrics, time series, locations and detailed events using the same data as the backend.

For a full written project narrative and business context, see `backend/PROJECT_REPORT.md`.

### 2. Project Structure

- **`backend/`**

  - `anomaly_api.py` – FastAPI application exposing:
    - `POST /predict` – score a single login event, send email alert on anomaly, append to `realtime_events.csv`.
    - `GET /events` – JSON list of events from `auth_logs_raw.csv` + `realtime_events.csv` (supports `limit`).
    - `GET /metrics` – aggregated metrics (`total`, `anomalies`, `anomalyRate`, `avgMttdMinutes`) plus series and breakdowns.
  - `model_training.ipynb` – data exploration, feature engineering and model training notebook.
  - `data/auth_logs_raw.csv` – baseline synthetic authentication dataset.
  - `data/realtime_events.csv` – **runtime** log of scored logins from the UI (created/appended by `/predict`).
  - `data/processed/` – derived features and preprocessing pipeline (ignored in git by default).
  - `isoforest_model.pkl`, `scaler.pkl` – trained anomaly model and feature scaler.
  - `producer.py` – optional Kafka producer for streaming auth events (if you use `docker-compose.yml`).
  - `docker-compose.yml` – local Kafka/ZooKeeper stack (optional).
  - `EMAIL_SETUP.md` – configuration details for SMTP / email alerts.
  - `requirements.txt` – Python backend dependencies.

- **`frontend/`**
  - `src/app/page.tsx` – marketing-style **landing page**, with entry points to user and admin flows.
  - `src/app/user/page.tsx` – **user login UI**:
    - Captures `user_id`, `device_id`, `ip_address`, `location`, `resource_accessed`,
      `login_success`, `bytes_transferred`, `password`.
    - Sends JSON to `POST /predict` on the backend and displays **model decision** (`NORMAL` / `ANOMALY`).
  - `src/app/dashboard/page.tsx` – **SOC dashboard**:
    - Uses React Query + custom hooks (`useEvents`, `useStats`, `useShap`) to talk to the backend.
    - Shows key KPIs, login events over time, anomalies by type, location analytics, SHAP explainability,
      and a filterable / sortable events table.
  - `src/hooks/` – React hooks for filters and API data.
  - `src/lib/api.ts` – frontend API client (respects `NEXT_PUBLIC_BACKEND_URL` or falls back to `http://<host>:8000`).
  - `src/components/ui/` – small shadcn‑style UI primitives (`Card`, `Badge`, `Accordion`).

### 3. Backend Setup

1. **Clone and enter the repo**

```bash
git clone <your-repo-url>.git
cd joan-testing
```

2. **Create and activate a Python environment**

You can use `conda` (e.g. your existing `llms` env) or a plain venv:

```bash
cd backend
python -m venv .venv        # or: conda create -n llms python=3.11
source .venv/bin/activate   # on macOS/Linux
# .venv\Scripts\activate    # on Windows
pip install -r requirements.txt
```

3. **(Optional) Train or refresh the model**

Open `backend/model_training.ipynb` in Jupyter/VS Code and run it to:

- Load `data/auth_logs_raw.csv`.
- Engineer features and fit the Isolation Forest.
- Save `isoforest_model.pkl` and `scaler.pkl`.

4. **Start the FastAPI backend**

If you are using a **conda** environment (e.g. `llms`):

```bash
cd backend
conda run -n llms python -m uvicorn anomaly_api:app --host 0.0.0.0 --port 8000
```

If you are using a **virtualenv / venv** and have it activated:

```bash
cd backend
python -m uvicorn anomaly_api:app --host 0.0.0.0 --port 8000
```

Key endpoints:

- `POST /predict` – score a single login event, send email alert on anomaly, log to `data/realtime_events.csv`.
- `GET /events?limit=0` – all historical + real‑time events.
- `GET /metrics` – global metrics and series for dashboards.

### 4. Frontend (Next.js) Setup

1. **Install dependencies**

```bash
cd frontend
npm install
```

2. **Configure backend URL (optional)**

By default the frontend will call `http://<current-host>:8000`.  
To override, create `frontend/.env.local`:

```bash
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
```

3. **Run the Next.js dev server**

```bash
cd frontend
npm run dev
```

Then open:

- `http://localhost:3000/` – landing page.
- `http://localhost:3000/user` – user login UI (calls `/predict`).
- `http://localhost:3000/dashboard` – SOC dashboard (consumes `/events` and `/metrics`).

### 5. How the End‑to‑End System Works

- **Data & model**

  - Historical auth data lives in `backend/data/auth_logs_raw.csv`.
  - `model_training.ipynb` prepares features and trains the Isolation Forest and scaler.
  - `anomaly_api.py` loads both and enforces a Zero‑Trust rule (`event_label != "normal"` → anomaly).

- **Real‑time scoring**

  - Frontend `/user` form sends a JSON login event to `POST /predict`.
  - Backend:
    - Scores the event with the Isolation Forest.
    - Classifies as `"normal"` or `"anomaly"`.
    - Sends an **email alert** when an anomaly is found.
    - Appends a row to `backend/data/realtime_events.csv` tagged with the decision.

- **Dashboards**
  - Backend helper `_load_events_df()` merges:
    - Historical `auth_logs_raw.csv`
    - Real‑time `realtime_events.csv`
  - `/metrics` and `/events` feed both:
    - The legacy Streamlit views (if you re‑add them) and
    - The **Next.js dashboard** at `/dashboard`, which:
      - Shows filtered KPIs (total events, anomalies, anomaly rate, MTTD).
      - Renders login events over time (by date) and anomalies by type.
      - Provides location‑level analytics and a filterable event table.

### 6. Email Alert Configuration

Email alerts are sent when anomalies are detected by the backend.

Create a `.env` file (not committed to git) with:

```bash
EMAIL_USER="your_gmail_address@gmail.com"
EMAIL_PASSWORD="your_16_char_app_password"
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
```

See `backend/EMAIL_SETUP.md` for detailed guidance on configuring Gmail / SMTP securely.

### 7. GitHub Notes

- Large derived artifacts and secrets are ignored via `.gitignore`:
  - `backend/data/processed/`, `*.pkl`, `*.joblib`, `.env`, etc.
- Before pushing, double‑check:
  - No secrets are committed (especially `.env`, API keys, or real email passwords).
  - `requirements.txt` and `frontend/package.json` reflect the dependencies you’re using.

Example initialisation for a new GitHub repo:

```bash
git init
git add .
git commit -m "Initial commit: Zero-Trust anomaly detection platform"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```
