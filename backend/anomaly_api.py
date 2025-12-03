# anomaly_api.py
import threading
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

try:
    from kafka import KafkaConsumer  # type: ignore
except ImportError:
    KafkaConsumer = None

app = FastAPI(title="🧠 Real-Time Zero-Trust Anomaly Detection API")

# Allow the Next.js frontend (and localhost during development) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Local network dev access (Next.js dev server)
        "http://192.168.86.48:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------
# 🧩 Load model and scaler
# ----------------------------------------------------------
iso_model = joblib.load("isoforest_model.pkl")
scaler = joblib.load("scaler.pkl")

features = [
    "user_id",
    "device_id",
    "ip_address",
    "location",
    "login_success",
    "hour",
    "resource_accessed",
    "bytes_transferred",
]

categorical_features = ["user_id", "device_id",
                        "ip_address", "location", "resource_accessed"]

ZERO_TRUST_NORMAL_LABEL = "normal"
ZERO_TRUST_POSITIVE_LABEL = "anomaly"
ADMIN_EMAIL = "zerotrustalliance@gmail.com"

_reference_data_path = Path(__file__).resolve(
).parent / "data" / "auth_logs_raw.csv"
_realtime_events_path = Path(__file__).resolve(
).parent / "data" / "realtime_events.csv"
label_encoders: dict[str, LabelEncoder] = {}

if _reference_data_path.exists():
    reference_df = pd.read_csv(_reference_data_path)
    for col in categorical_features:
        encoder = LabelEncoder()
        label_encoders[col] = encoder.fit(reference_df[col].astype(str))
else:
    for col in categorical_features:
        label_encoders[col] = LabelEncoder()


# ----------------------------------------------------------
# 📊 Helper: load events for metrics
# ----------------------------------------------------------


def _load_events_df() -> pd.DataFrame:
    """
    Load events in a way that mirrors the Streamlit dashboard:
    - Always start from the reference auth_logs_raw.csv if available
    - Optionally append real-time events from realtime_events.csv
    """
    base_df: pd.DataFrame

    if _reference_data_path.exists():
        base_df = pd.read_csv(_reference_data_path)
    else:
        base_df = pd.DataFrame()

    rt_df: pd.DataFrame | None = None
    if _realtime_events_path.exists():
        rt_df = pd.read_csv(_realtime_events_path)

    if base_df.empty and rt_df is None:
        return pd.DataFrame()

    # Align columns between base and realtime before concatenation
    if rt_df is not None:
        all_cols = sorted(set(base_df.columns).union(rt_df.columns))
        base_df = base_df.reindex(columns=all_cols)
        rt_df = rt_df.reindex(columns=all_cols)
        df = pd.concat([base_df, rt_df], ignore_index=True)
    else:
        df = base_df.copy()

    # Normalise timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    else:
        df["timestamp"] = pd.Timestamp.utcnow()

    # Ensure is_anomaly flag.
    # To stay consistent with the Streamlit dashboard, always derive from
    # event_label when available (Zero-Trust: anything != "normal" is anomaly).
    if "event_label" in df.columns:
        df["is_anomaly"] = (
            df["event_label"] != ZERO_TRUST_NORMAL_LABEL
        ).astype(int)
    elif "is_anomaly" in df.columns:
        df["is_anomaly"] = df["is_anomaly"].fillna(0).astype(int)
    else:
        df["is_anomaly"] = 0

    return df

# ----------------------------------------------------------
# 🧠 Preprocessing function
# ----------------------------------------------------------


def preprocess(event: dict):
    """Convert a login event to a scaled feature vector"""
    df = pd.DataFrame([event])

    # Extract hour from access_time
    df["hour"] = pd.to_datetime(
        df["access_time"], errors="coerce").dt.hour.fillna(0)

    # Encode categorical fields (temporary per request)
    for col in categorical_features:
        encoder = label_encoders[col]
        value = df.at[0, col]
        if value is None:
            value = ""
        value = str(value)
        if not hasattr(encoder, "classes_"):
            encoder.fit([value])
        if value not in encoder.classes_:
            encoder.classes_ = np.append(encoder.classes_, value)
        df[col] = encoder.transform(df[col].astype(str))

    X = scaler.transform(df[features])
    return X

# ----------------------------------------------------------
# 📧 Email notification function
# ----------------------------------------------------------


def send_anomaly_alert(event: dict, prediction: str) -> bool:
    """Send email alert to admin when anomaly is detected via API"""
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        email_user = os.getenv("EMAIL_USER", "")
        email_password = os.getenv("EMAIL_PASSWORD", "")

        if not email_user or not email_password:
            print(
                "⚠️ Email credentials not configured. Set EMAIL_USER and EMAIL_PASSWORD environment variables.")
            return False

        # Strip any whitespace and quotes from password (in case .env has quotes)
        email_user = email_user.strip().strip('"').strip("'")
        email_password = email_password.strip().strip('"').strip("'")

        # Debug info (without exposing full password)
        print(f"📧 Attempting to send email from: {email_user}")
        print(f"   Password length: {len(email_password)} characters")
        if len(email_password) < 10:
            print(
                "   ⚠️ WARNING: Password seems too short. Gmail App Passwords are typically 16 characters.")

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"🚨 ZERO-TRUST ALERT: Anomaly Detected via API - {event.get('user_id', 'Unknown User')}"

        # Build email body
        body = f"""
🔒 ZERO-TRUST ANOMALY DETECTION ALERT (API)

Anomalous login activity has been detected via the API endpoint and requires immediate attention.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 EVENT DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
👤 User ID: {event.get('user_id', 'N/A')}
💻 Device ID: {event.get('device_id', 'N/A')}
🌐 IP Address: {event.get('ip_address', 'N/A')}
📍 Location: {event.get('location', 'N/A')}
✅ Login Success: {'Yes' if event.get('login_success') == 1 else 'No'}
📂 Resource Accessed: {event.get('resource_accessed', 'N/A')}
📦 Bytes Transferred: {event.get('bytes_transferred', 0):,} bytes
🕐 Access Time: {event.get('access_time', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 ANOMALY CLASSIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: {prediction.upper()}
Detection Method: Isolation Forest Model

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ RECOMMENDED ACTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Review user account activity and verify legitimacy
2. Check for associated security events in the same time window
3. Consider temporary account suspension if risk is high
4. Investigate device and IP address for known threats
5. Review resource access patterns for this user

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated alert from the Zero-Trust Anomaly Detection API.
Please investigate this event promptly.

"""

        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, ADMIN_EMAIL, text)
        server.quit()

        print(f"📧 Alert email sent to {ADMIN_EMAIL}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        error_msg = str(e)
        if "535" in error_msg or "BadCredentials" in error_msg:
            print(f"❌ Gmail authentication failed for: {email_user}")
            print("   This usually means:")
            print(
                "   1. You're using your regular Gmail password instead of an App Password")
            print("   2. 2-Step Verification is not enabled on this Google account")
            print("   3. The App Password is incorrect or expired")
            print("   4. The App Password was generated for a different account")
            print("   → Steps to fix:")
            print("   1. Go to: https://myaccount.google.com/security")
            print("   2. Enable 2-Step Verification (if not already enabled)")
            print("   3. Go to: https://myaccount.google.com/apppasswords")
            print("   4. Generate a new App Password for 'Mail'")
            print(
                "   5. Update EMAIL_PASSWORD in your .env file with the new 16-character password")
            print(
                f"   → Current password length: {len(email_password)} characters")
        else:
            print(f"❌ Failed to send email alert: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to send email alert: {e}")
        return False


# ----------------------------------------------------------
# 🧾 Kafka consumer for background event stream
# ----------------------------------------------------------
try:
    consumer = (
        KafkaConsumer(
            "auth_events",
            bootstrap_servers="localhost:9092",
            auto_offset_reset="latest",
        )
        if KafkaConsumer
        else None
    )
except Exception as e:  # pragma: no cover
    consumer = None
    print(f"⚠️ Kafka not connected: {e}")


@app.on_event("startup")
def start_consumer():
    """Start Kafka background consumer on startup"""
    if not consumer:
        print("⚠️ Kafka broker not available. Skipping consumer startup.")
        return

    def consume():
        for message in consumer:
            event = json.loads(message.value.decode("utf-8"))
            X = preprocess(event)
            pred = iso_model.predict(X)[0]
            label = "🚨 ANOMALY" if pred == -1 else "✅ NORMAL"
            print(f"{label}: {event['user_id']} from {event['location']}")

    thread = threading.Thread(target=consume, daemon=True)
    thread.start()

# ----------------------------------------------------------
# 🌐 Root route
# ----------------------------------------------------------


@app.get("/")
def home():
    return {
        "status": "running",
        "topic": "auth_events",
        "message": "Use POST /predict to send login events for detection",
    }


@app.get("/metrics")
def metrics():
    """
    Aggregate metrics for dashboard consumption.

    Returns JSON with:
    - metrics: high-level KPIs
    - seriesByHour: time series of total vs anomalies by hour
    - anomalyByType: counts by event_label
    - recentEvents: last few raw events
    """
    df = _load_events_df()
    if df.empty:
        return {
            "metrics": {
                "total": 0,
                "anomalies": 0,
                "anomalyRate": 0.0,
                "avgMttdMinutes": None,
            },
            "seriesByHour": [],
            "anomalyByType": [],
            "recentEvents": [],
        }

    total = int(len(df))
    anomalies = int(df["is_anomaly"].sum())
    anomaly_rate = float((anomalies / total) * 100) if total else 0.0

    # Very simple MTTD approximation using time between anomaly events
    if "timestamp" in df.columns:
        anomaly_times = df[df["is_anomaly"] == 1]["timestamp"].sort_values()
        if len(anomaly_times) > 1:
            deltas = anomaly_times.diff().dropna()
            avg_mttd_minutes = float(
                deltas.mean().total_seconds() / 60.0  # type: ignore[arg-type]
            )
        else:
            avg_mttd_minutes = None
    else:
        avg_mttd_minutes = None

    # Time-series by hour
    if "timestamp" in df.columns:
        df["hour"] = df["timestamp"].dt.strftime("%H:00")
    else:
        df["hour"] = "00:00"

    by_hour = (
        df.groupby("hour")
        .agg(total=("timestamp", "count"), anomalies=("is_anomaly", "sum"))
        .reset_index()
        .sort_values("hour")
    )

    series_by_hour = [
        {
            "hour": str(row["hour"]),
            "total": int(row["total"]),
            "anomalies": int(row["anomalies"]),
        }
        for _, row in by_hour.iterrows()
    ]

    # Breakdown by event label
    if "event_label" in df.columns:
        by_type = (
            df[df["is_anomaly"] == 1]
            .groupby("event_label")
            .size()
            .reset_index(name="value")
        )
        anomaly_by_type = [
            {"name": str(row["event_label"]), "value": int(row["value"])}
            for _, row in by_type.iterrows()
        ]
    else:
        anomaly_by_type = []

    # Recent events
    recent_cols = [
        "timestamp",
        "user_id",
        "location",
        "login_success",
        "resource_accessed",
        "bytes_transferred",
        "event_label",
        "is_anomaly",
    ]
    available_cols = [c for c in recent_cols if c in df.columns]
    recent_df = df.sort_values("timestamp", ascending=False).head(20)

    def _serialize_row_for_recent(row: pd.Series) -> dict:
        out: dict[str, object] = {}
        for col in available_cols:
            value = row.get(col)
            if col == "timestamp" and not pd.isna(value):
                out[col] = pd.to_datetime(value).isoformat()
            elif isinstance(value, (np.integer, np.floating)):
                out[col] = float(value)
            else:
                out[col] = value
        # Ensure is_anomaly is boolean for the frontend
        if "is_anomaly" in out:
            # type: ignore[arg-type]
            out["is_anomaly"] = bool(int(out["is_anomaly"]))
        return out

    recent_events = [
        _serialize_row_for_recent(row) for _, row in recent_df.iterrows()
    ]

    return {
        "metrics": {
            "total": total,
            "anomalies": anomalies,
            "anomalyRate": anomaly_rate,
            "avgMttdMinutes": avg_mttd_minutes,
        },
        "seriesByHour": series_by_hour,
        "anomalyByType": anomaly_by_type,
        "recentEvents": recent_events,
    }


@app.get("/events")
def events(limit: int = 0):
    """
    Return a flat list of recent events for the frontend dashboard.
    This powers filtering, tables and client-side analytics.
    """
    df = _load_events_df()
    if df.empty:
        return {"events": [], "total": 0}

    # Ensure we have a timestamp for sorting and serialisation
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    else:
        df["timestamp"] = pd.Timestamp.utcnow()

    # Sort newest first and apply limit
    df_sorted = df.sort_values("timestamp", ascending=False)
    # If a positive limit is provided, truncate; otherwise return full set
    if limit and limit > 0:
        df_sorted = df_sorted.head(limit)

    cols = [
        "timestamp",
        "user_id",
        "device_id",
        "ip_address",
        "location",
        "login_success",
        "access_time",
        "resource_accessed",
        "bytes_transferred",
        "event_label",
        "is_anomaly",
    ]
    available_cols = [c for c in cols if c in df_sorted.columns]

    def _serialize_row(row: pd.Series) -> dict:
        out: dict[str, object] = {}
        for col in available_cols:
            value = row.get(col)
            if col == "timestamp" and not pd.isna(value):
                out[col] = pd.to_datetime(value).isoformat()
            elif isinstance(value, (np.integer, np.floating)):
                out[col] = float(value)
            else:
                out[col] = value
        if "is_anomaly" in out:
            # type: ignore[arg-type]
            out["is_anomaly"] = bool(int(out["is_anomaly"]))
        return out

    events_payload = [_serialize_row(row) for _, row in df_sorted.iterrows()]
    return {"events": events_payload, "total": int(len(df))}


@app.get("/test-email")
def test_email():
    """Test endpoint to verify email configuration"""
    email_user = os.getenv("EMAIL_USER", "")
    email_password = os.getenv("EMAIL_PASSWORD", "")

    if not email_user or not email_password:
        return {
            "status": "error",
            "message": "Email credentials not configured",
            "email_user_set": bool(email_user),
            "email_password_set": bool(email_password)
        }

    # Test SMTP connection
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user.strip(), email_password.strip())
        server.quit()

        return {
            "status": "success",
            "message": "Email credentials are valid!",
            "email_user": email_user,
            "smtp_server": smtp_server,
            "smtp_port": smtp_port
        }
    except smtplib.SMTPAuthenticationError as e:
        return {
            "status": "error",
            "message": "Gmail authentication failed",
            "error": str(e),
            "help": "Make sure you're using a Gmail App Password, not your regular password. Generate one at: https://myaccount.google.com/apppasswords"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Email test failed",
            "error": str(e)
        }

# ----------------------------------------------------------
# ⚡ Live prediction endpoint (for UI or API calls)
# ----------------------------------------------------------


@app.post("/predict")
async def predict_event(request: Request):
    """Receive a single login event and return anomaly prediction"""
    event = await request.json()

    if "features" in event:
        feature_vector = np.asarray(
            event["features"], dtype=float).reshape(1, -1)
        X = scaler.transform(feature_vector)
    else:
        X = preprocess(event)

    pred = iso_model.predict(X)[0]
    label = ZERO_TRUST_POSITIVE_LABEL if pred == -1 else ZERO_TRUST_NORMAL_LABEL

    # Send email alert if anomaly detected
    if label == ZERO_TRUST_POSITIVE_LABEL:
        send_anomaly_alert(event, label)

    # Log event to real-time CSV for dashboards (mirrors login_ui.py behaviour)
    try:
        from datetime import timezone

        timestamp = datetime.now(timezone.utc).isoformat()
        event_record = {
            "timestamp": timestamp,
            "user_id": event.get("user_id"),
            "device_id": event.get("device_id"),
            "ip_address": event.get("ip_address"),
            "location": event.get("location"),
            "login_success": event.get("login_success"),
            "access_time": event.get("access_time"),
            "resource_accessed": event.get("resource_accessed"),
            "bytes_transferred": event.get("bytes_transferred"),
            "event_label": label,
            "is_anomaly": 1 if label == ZERO_TRUST_POSITIVE_LABEL else 0,
        }

        df_rt = pd.DataFrame([event_record])
        _realtime_events_path.parent.mkdir(parents=True, exist_ok=True)
        if _realtime_events_path.exists():
            df_rt.to_csv(
                _realtime_events_path, mode="a", header=False, index=False
            )
        else:
            df_rt.to_csv(
                _realtime_events_path, mode="w", header=True, index=False
            )
    except Exception as e:  # pragma: no cover - logging failures shouldn't break API
        print(f"⚠️ Could not append real-time event: {e}")

    response = {
        "user_id": event.get("user_id"),
        "device_id": event.get("device_id"),
        "location": event.get("location"),
        "prediction": label,
    }

    print(f"🔎 Login checked: {response}")
    return response
