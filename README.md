## Zero-Trust Anomaly Detection in Authentication Logs

### 1. Overview

This project implements a **Zero-Trust Anomaly Detection System** for authentication logs.  
It uses multiple machine learning models (Isolation Forest, One-Class SVM, Autoencoder) to detect:

- Impossible travel
- Off-hours logins
- Multiple failed logins
- Large data transfers
- Unusual resource access

The solution includes:

- `model_training.ipynb` – data exploration, feature engineering, and model training
- `anomaly_api.py` – FastAPI service for real-time anomaly detection
- `login_ui.py` – Streamlit login simulator with explainability and email alerts
- `dashboard/app.py` – Streamlit dashboard for monitoring and analysis
- `producer.py` – Kafka event producer for simulated auth logs

For a full project narrative, see `PROJECT_REPORT.md`.

### 2. Project Structure

Key files and directories:

- `model_training.ipynb` – training notebook
- `anomaly_api.py` – REST API for `/predict`
- `login_ui.py` – interactive login simulator UI
- `dashboard/app.py` – monitoring dashboard
- `producer.py` – Kafka log producer
- `data/auth_logs_raw.csv` – example authentication dataset
- `data/realtime_events.csv` – events logged from the UI (created at runtime)
- `isoforest_model.pkl`, `scaler.pkl` – trained model and scaler artifacts
- `docker-compose.yml` – local Kafka/ZooKeeper stack
- `EMAIL_SETUP.md` – notes for configuring email alerts
- `PROJECT_REPORT.md` – detailed project report

### 3. Setup

1. **Clone the repository**

```bash
git clone <your-repo-url>.git
cd joan-testing
```

2. **Create and activate a virtual environment** (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate  # on macOS/Linux
# .venv\Scripts\activate   # on Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **(Optional) Start Kafka stack**

```bash
docker-compose up -d
```

### 4. Running the Components

**1. Train or refresh the model (optional)**

Open `model_training.ipynb` in Jupyter/VS Code, run the cells to:

- load `data/auth_logs_raw.csv`
- engineer features
- train the Isolation Forest / other models
- persist `isoforest_model.pkl` and `scaler.pkl` in the project root

**2. Start the API**

```bash
uvicorn anomaly_api:app --host 0.0.0.0 --port 8000
```

**3. Run the Login UI**

```bash
streamlit run login_ui.py
```

This simulates logins, calls the FastAPI `/predict` endpoint, explains decisions (via SHAP), and logs events to `data/realtime_events.csv`.

**4. Run the Dashboard**

```bash
cd dashboard
streamlit run app.py
```

The dashboard can:

- load the default dataset (`data/auth_logs_raw.csv`)  
- merge in real-time events from `data/realtime_events.csv`  
- visualize anomalies over time, by type, and by location  
- show key metrics (anomaly rate, MTTD, etc.)

**5. (Optional) Run the Kafka producer**

With Kafka running via `docker-compose.yml`:

```bash
python producer.py
```

This will send random auth events to the `auth_events` topic that `anomaly_api.py` can consume.

### 5. Email Alert Configuration

Email alerts are sent when anomalies are detected (from both `login_ui.py` and `anomaly_api.py`).

Create a `.env` file in the project root with:

```bash
EMAIL_USER="your_gmail_address@gmail.com"
EMAIL_PASSWORD="your_16_char_app_password"
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
```

Notes:

- Use a **Gmail App Password**, not your normal password.
- Ensure 2-Step Verification is enabled on the Google account.
- See `EMAIL_SETUP.md` for more detailed guidance.

### 6. Notes for GitHub

- Large derived artifacts (`data/processed/`, `*.pkl`, `*.joblib`) and environment files (`.env`) are ignored via `.gitignore`.
- Before pushing, you may want to:
  - regenerate `isoforest_model.pkl` and `scaler.pkl` if you reran training
  - verify that no secrets are committed (especially `.env` or hard-coded passwords)

Once this is in place, you can initialize git and push to GitHub:

```bash
git init
git add .
git commit -m "Initial commit: Zero-Trust anomaly detection project"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```


