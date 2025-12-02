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

# Load environment variables from .env file
load_dotenv()

try:
    from kafka import KafkaConsumer  # type: ignore
except ImportError:
    KafkaConsumer = None

app = FastAPI(title="🧠 Real-Time Zero-Trust Anomaly Detection API")

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

    response = {
        "user_id": event.get("user_id"),
        "device_id": event.get("device_id"),
        "location": event.get("location"),
        "prediction": label,
    }

    print(f"🔎 Login checked: {response}")
    return response
