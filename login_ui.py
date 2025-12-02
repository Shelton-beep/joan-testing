from sklearn.preprocessing import LabelEncoder
import streamlit as st
import shap
import requests
import pandas as pd
import numpy as np
from pathlib import Path
import datetime
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import joblib

# Load environment variables from .env file
load_dotenv()

# ------------------------------------------------------
# 🎯 Setup
# ------------------------------------------------------
st.set_page_config(page_title="Zero-Trust Login Simulator", layout="centered")
st.title("🔐 Zero-Trust Login Simulator with Explainability")

# ------------------------------------------------------
# 🧠 Load model + scaler locally for explainability
# ------------------------------------------------------
try:
    iso_model = joblib.load("isoforest_model.pkl")
    scaler = joblib.load("scaler.pkl")
except Exception as e:
    st.error(f"❌ Could not load model or scaler: {e}")
    st.stop()

features = [
    "user_id", "device_id", "ip_address", "location",
    "login_success", "hour", "resource_accessed", "bytes_transferred"
]

categorical_features = ["user_id", "device_id",
                        "ip_address", "location", "resource_accessed"]

ZERO_TRUST_NORMAL_LABEL = "normal"
ZERO_TRUST_POSITIVE_LABEL = "anomaly"
ADMIN_EMAIL = "zerotrustalliance@gmail.com"

reference_data_path = Path(__file__).resolve().parent / \
    "data" / "auth_logs_raw.csv"
realtime_events_path = Path(__file__).resolve().parent / \
    "data" / "realtime_events.csv"
label_encoders: dict[str, LabelEncoder] = {}
reference_df: pd.DataFrame | None = None

SECURITY_KB = {
    "bytes_transferred": (
        "The volume of data moved during a session is a classic data exfiltration indicator. "
        "Large transfers, especially from non-production resources, can expose sensitive assets."
    ),
    "hour": (
        "Access patterns that deviate from a user’s normal working hours often precede credential abuse "
        "or lateral movement."
    ),
    "login_success": (
        "Repeated login failures followed by success may highlight password spraying or brute-force activity."
    ),
    "resource_accessed": (
        "Sensitive resources such as finance or production systems should only be reached by authorised personas. "
        "Unexpected access can mark an intrusion path."
    ),
    "location": (
        "Unusual geographic origins or sudden travel between regions are strong impossible-travel signals."
    ),
    "device_id": (
        "New or rarely seen endpoints can point to compromised machines or rogue devices."
    ),
    "ip_address": (
        "Unknown IP addresses, especially from untrusted ranges, often flag VPN misuse or attacker footholds."
    ),
    "user_id": (
        "Account behaviour is profiled per identity. Sudden shifts in activity may signal account takeover."
    ),
}

if reference_data_path.exists():
    reference_df = pd.read_csv(reference_data_path)
    for col in categorical_features:
        encoder = LabelEncoder()
        label_encoders[col] = encoder.fit(reference_df[col].astype(str))
else:
    st.warning(
        "Reference dataset not found; categorical encodings will be inferred on the fly.")
    for col in categorical_features:
        label_encoders[col] = LabelEncoder()


def build_shap_background() -> np.ndarray:
    if reference_df is not None:
        baseline = reference_df.copy()
        if "hour" not in baseline.columns and "access_time" in baseline.columns:
            baseline["hour"] = pd.to_datetime(
                baseline["access_time"], errors="coerce").dt.hour.fillna(0)
        else:
            baseline["hour"] = pd.to_datetime(
                baseline.get("access_time"), errors="coerce").dt.hour.fillna(0)

        for col in categorical_features:
            baseline[col] = label_encoders[col].transform(
                baseline[col].astype(str))

        return scaler.transform(
            baseline[features].head(min(200, len(baseline))))

    return np.zeros((1, len(features)))


shap_background = build_shap_background()
shap_explainer = shap.KernelExplainer(
    iso_model.decision_function, shap_background)


def retrieve_security_context(feature: str, value: float | int | str) -> str:
    base_text = SECURITY_KB.get(
        feature,
        "This dimension influences the behavioural baseline for zero-trust monitoring.",
    )
    if feature == "hour":
        return (
            f"{base_text} The event took place at hour {int(value)}, which is compared against the user’s historical rhythm."
        )
    if feature == "bytes_transferred":
        return (
            f"{base_text} The session moved approximately {int(value):,} bytes."
        )
    if feature == "login_success":
        status = "successful" if int(value) == 1 else "unsuccessful"
        return f"{base_text} This attempt was {status}."
    return f"{base_text} Observed value: {value}."


def send_anomaly_alert(event_data: dict, prediction: str, reason: str, shap_df: pd.DataFrame) -> bool:
    """Send email alert to admin when anomaly is detected"""
    try:
        # Get email credentials from environment variables or use defaults
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        email_user = os.getenv("EMAIL_USER", "")
        email_password = os.getenv("EMAIL_PASSWORD", "")

        if not email_user or not email_password:
            st.warning(
                "⚠️ Email credentials not configured. Set EMAIL_USER and EMAIL_PASSWORD environment variables.")
            return False

        # Strip any whitespace and quotes from password (in case .env has quotes)
        email_user = email_user.strip().strip('"').strip("'")
        email_password = email_password.strip().strip('"').strip("'")

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"🚨 ZERO-TRUST ALERT: Anomaly Detected - {event_data.get('user_id', 'Unknown User')}"

        # Build email body
        body = f"""
🔒 ZERO-TRUST ANOMALY DETECTION ALERT

Anomalous login activity has been detected and requires immediate attention.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 EVENT DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
👤 User ID: {event_data.get('user_id', 'N/A')}
💻 Device ID: {event_data.get('device_id', 'N/A')}
🌐 IP Address: {event_data.get('ip_address', 'N/A')}
📍 Location: {event_data.get('location', 'N/A')}
✅ Login Success: {'Yes' if event_data.get('login_success') == 1 else 'No'}
📂 Resource Accessed: {event_data.get('resource_accessed', 'N/A')}
📦 Bytes Transferred: {event_data.get('bytes_transferred', 0):,} bytes
🕐 Access Time: {event_data.get('access_time', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 ANOMALY CLASSIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: {prediction.upper()}
Reason: {reason}

"""

        # Add SHAP feature importance if available
        if not shap_df.empty:
            body += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 TOP CONTRIBUTING FACTORS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            for _, row in shap_df.iterrows():
                body += f"• {row['Feature']}: Impact Score {row['Impact']:.4f}\n"
            body += "\n"

        body += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ RECOMMENDED ACTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Review user account activity and verify legitimacy
2. Check for associated security events in the same time window
3. Consider temporary account suspension if risk is high
4. Investigate device and IP address for known threats
5. Review resource access patterns for this user

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated alert from the Zero-Trust Anomaly Detection System.
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

        return True

    except smtplib.SMTPAuthenticationError as e:
        error_msg = str(e)
        if "535" in error_msg or "BadCredentials" in error_msg:
            st.error("❌ Gmail authentication failed!")
            st.warning("**Common causes:**")
            st.write("1. Using regular Gmail password instead of App Password")
            st.write("2. 2-Step Verification not enabled")
            st.write("3. Incorrect App Password")
            st.info(
                "📧 **Solution:** Generate an App Password at: https://myaccount.google.com/apppasswords")
            st.caption("Make sure 2-Step Verification is enabled first!")
        else:
            st.error(f"❌ Failed to send email alert: {e}")
        return False
    except Exception as e:
        st.error(f"❌ Failed to send email alert: {e}")
        return False


def generate_security_explanation(
    prediction: str,
    reason: str,
    shap_rows: pd.DataFrame,
    original_event: dict,
) -> str:
    narrative = []
    tone = (
        "an anomaly under the zero-trust policy"
        if prediction == ZERO_TRUST_POSITIVE_LABEL
        else "consistent with the user’s expected behaviour"
    )
    narrative.append(
        f"The login was classified as {prediction} and is {tone}. {reason}"
    )

    if shap_rows.empty:
        return " ".join(narrative)

    narrative.append(
        "The model highlighted the following signals as most influential:"
    )
    for _, row in shap_rows.iterrows():
        feature = row["Feature"]
        shap_value = row["SHAP"]
        direction = (
            "elevated the anomaly risk"
            if shap_value > 0
            else "helped confirm the session as legitimate"
        )
        context = retrieve_security_context(feature, row["Value"])
        narrative.append(
            f"- {feature}: {context} This evidence {direction} (SHAP score {shap_value:.4f})."
        )

    narrative.append(
        "These insights blend behavioural baselines with zero-trust heuristics, enabling analysts to pivot quickly."
    )
    return " ".join(narrative)


# ------------------------------------------------------
# 🧩 UI Input
# ------------------------------------------------------
user_id = st.text_input("👤 User ID", "user_101")
device_id = st.text_input("💻 Device ID", "device_22")
ip_address = st.text_input("🌐 IP Address", "192.168.10.5")
location = st.selectbox(
    "📍 Location", ["New York, USA", "Cape Town, South Africa", "Tokyo, Japan"])
resource_accessed = st.selectbox(
    "📂 Resource", ["sales", "finance", "hr", "prod"])
login_success = st.selectbox("✅ Login Success", [1, 0])
bytes_transferred = st.number_input(
    "📦 Bytes Transferred (in bytes)", value=500000, step=1000)
access_time = datetime.datetime.now().strftime("%H:%M:%S")

# ------------------------------------------------------
# 🚀 Button Action
# ------------------------------------------------------
if st.button("🚀 Attempt Login"):
    # 1️⃣ Prepare event
    data = {
        "user_id": user_id,
        "device_id": device_id,
        "ip_address": ip_address,
        "location": location,
        "login_success": login_success,
        "access_time": access_time,
        "resource_accessed": resource_accessed,
        "bytes_transferred": bytes_transferred,
    }

    try:
        # 2️⃣ Business rule override — only anomaly if > 5 GB
        if bytes_transferred > 5 * 1024 * 1024 * 1024:  # 5 GB in bytes
            prediction = ZERO_TRUST_POSITIVE_LABEL
            reason = "High data transfer (> 5 GB) detected — potential exfiltration risk."
        else:
            # Send to FastAPI model for prediction
            res = requests.post("http://localhost:8000/predict", json=data)
            res.raise_for_status()
            result = res.json()
            prediction = result["prediction"]
            reason = "Model-based behavior anomaly detection."

        # 3️⃣ Local explainability using SHAP (only if model used)
        df = pd.DataFrame([data])
        df["hour"] = pd.to_datetime(
            df["access_time"], errors="coerce").dt.hour.fillna(0)

        # Encode categorical variables
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

        # Compute SHAP values only if using the model
        if prediction == ZERO_TRUST_POSITIVE_LABEL and reason != "Model-based behavior anomaly detection.":
            shap_df = pd.DataFrame(
                columns=["Feature", "SHAP", "Impact", "Value"])
        else:
            shap_values = shap_explainer.shap_values(X)
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            shap_df = pd.DataFrame({
                "Feature": features,
                "SHAP": shap_values[0],
                "Impact": np.abs(shap_values[0]),
                "Value": df[features].iloc[0].values
            }).sort_values("Impact", ascending=False).head(3)

        # 4️⃣ Display results
        if prediction == ZERO_TRUST_POSITIVE_LABEL:
            st.error(
                f"🚨 {user_id} flagged as {ZERO_TRUST_POSITIVE_LABEL} from {location}")

            # 4️⃣.5 Send email alert to admin
            email_sent = send_anomaly_alert(data, prediction, reason, shap_df)
            if email_sent:
                st.success(f"📧 Alert email sent to {ADMIN_EMAIL}")
            else:
                st.warning(
                    "⚠️ Could not send email alert. Check email configuration.")
        else:
            st.success(f"✅ {user_id} login looks {ZERO_TRUST_NORMAL_LABEL}.")

        st.markdown(f"**🧩 Reason:** {reason}")

        # 5️⃣ Show explanation (if available)
        if not shap_df.empty:
            st.markdown("### 🧠 Explanation: Top contributing factors")
            for i, row in shap_df.iterrows():
                st.write(
                    f"- **{row['Feature']}** → impact score: `{row['Impact']:.4f}`")

            st.caption(
                "Feature importance computed using SHAP values from the Isolation Forest model.")
        else:
            st.info("No SHAP explanation shown (rule-based anomaly).")

        st.markdown("### 🛡️ Security Narrative")
        narrative = generate_security_explanation(
            prediction,
            reason,
            shap_df,
            data,
        )
        st.write(narrative)

        # 6️⃣ Save event to real-time events file for dashboard
        try:
            event_record = {
                "timestamp": datetime.datetime.now().isoformat(),
                "user_id": user_id,
                "device_id": device_id,
                "ip_address": ip_address,
                "location": location,
                "login_success": login_success,
                "access_time": access_time,
                "resource_accessed": resource_accessed,
                "bytes_transferred": bytes_transferred,
                "event_label": prediction,
                "is_anomaly": 1 if prediction == ZERO_TRUST_POSITIVE_LABEL else 0,
            }

            event_df = pd.DataFrame([event_record])

            # Ensure data directory exists
            realtime_events_path.parent.mkdir(parents=True, exist_ok=True)

            # Append to real-time events file
            if realtime_events_path.exists():
                event_df.to_csv(realtime_events_path, mode='a',
                                header=False, index=False)
            else:
                event_df.to_csv(realtime_events_path, mode='w',
                                header=True, index=False)

            st.success(
                "📊 Event logged to dashboard! View it in the Dashboard app.")

        except Exception as save_error:
            st.warning(f"⚠️ Could not save event to dashboard: {save_error}")

    except Exception as e:
        st.error(f"❌ Error processing login: {e}")
