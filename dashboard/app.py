import streamlit as st
import pandas as pd
import numpy as np
import joblib
import shap
import requests
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
from sklearn.preprocessing import LabelEncoder
import io

# ------------------------------------------------------
# 🧠 Load trained models and scalers
# ------------------------------------------------------
st.set_page_config(page_title="Zero-Trust Anomaly Detection",
                   layout="wide", initial_sidebar_state="expanded")
st.title("🔒 Zero-Trust Anomaly Detection Dashboard")

# Get project root directory (parent of dashboard folder)
project_root = Path(__file__).resolve().parent.parent
model_path = project_root / "isoforest_model.pkl"
scaler_path = project_root / "scaler.pkl"
default_data_path = project_root / "data" / "auth_logs_raw.csv"
realtime_events_path = project_root / "data" / "realtime_events.csv"

# Try to load models (optional for visualization)
iso_model = None
scaler = None
try:
    iso_model = joblib.load(str(model_path))
    scaler = joblib.load(str(scaler_path))
    st.sidebar.success("✅ Model loaded")
except Exception as e:
    st.sidebar.warning(f"⚠️ Model not available: {e}")

ZERO_TRUST_NORMAL_LABEL = "normal"
ZERO_TRUST_POSITIVE_LABEL = "anomaly"

# ------------------------------------------------------
# 📂 Sidebar: Data Upload & Filters
# ------------------------------------------------------
st.sidebar.header("📂 Data Source")

# Real-time mode toggle
realtime_mode = st.sidebar.checkbox(
    "🔄 Real-Time Mode", value=True, help="Show new login events from Login UI")

# Auto-refresh button for real-time mode
if realtime_mode:
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    st.sidebar.caption("💡 Click 'Refresh Now' to update with latest events")

uploaded = st.sidebar.file_uploader(
    "Upload CSV", type=["csv"], help="Upload authentication logs CSV file")

# Load real-time events if available
realtime_df = None
if realtime_events_path.exists() and realtime_mode:
    try:
        realtime_df = pd.read_csv(realtime_events_path)
        if not realtime_df.empty:
            realtime_df["timestamp"] = pd.to_datetime(
                realtime_df["timestamp"], errors="coerce")
            st.sidebar.success(f"📡 {len(realtime_df)} real-time events")
    except Exception as e:
        st.sidebar.warning(f"Could not load real-time events: {e}")

# Try to load default dataset if no upload
df = None
if uploaded:
    df = pd.read_csv(uploaded)
elif default_data_path.exists():
    if st.sidebar.button("📊 Load Default Dataset") or realtime_mode:
        df = pd.read_csv(default_data_path)
        st.sidebar.success(f"Loaded {len(df)} records")

# Merge real-time events with main dataset
if df is not None and not df.empty:
    # Convert timestamp to datetime in main dataset first
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Merge with real-time events
    if realtime_df is not None and not realtime_df.empty:
        # Ensure columns match
        common_cols = [col for col in df.columns if col in realtime_df.columns]
        if common_cols:
            # Ensure both dataframes have datetime timestamps before merging
            if "timestamp" in common_cols:
                df["timestamp"] = pd.to_datetime(
                    df["timestamp"], errors="coerce")
                realtime_df["timestamp"] = pd.to_datetime(
                    realtime_df["timestamp"], errors="coerce")

            # Combine datasets
            df = pd.concat([df, realtime_df[common_cols]], ignore_index=True)

            # Convert timestamp again after merge to ensure all are datetime
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(
                    df["timestamp"], errors="coerce")

            # Drop duplicates and sort
            df = df.drop_duplicates(
                subset=["timestamp", "user_id", "device_id"], keep="last")
            df = df.sort_values("timestamp", ascending=False)
            st.sidebar.info(
                f"📊 Combined: {len(df)} total events (including {len(realtime_df)} real-time)")

    # Apply Zero-Trust labeling
    if "event_label" in df.columns:
        df["binary_label"] = (df["event_label"] !=
                              ZERO_TRUST_NORMAL_LABEL).astype(int)
        df["is_anomaly"] = df["binary_label"] == 1
    elif "is_anomaly" in df.columns:
        # Use existing is_anomaly if event_label not present
        df["binary_label"] = df["is_anomaly"]

        # Extract anomaly types from event_label
        anomaly_types = [
            "impossible_travel", "off_hours_login", "multiple_failed_logins",
            "large_data_transfer", "unusual_resource_access"
        ]

        for atype in anomaly_types:
            df[f"has_{atype}"] = df["event_label"].str.contains(
                atype, case=False, na=False)
    else:
        df["is_anomaly"] = False
        st.warning("⚠️ No event_label column found. Anomaly detection disabled.")

    # Parse timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])

    # Extract hour if access_time exists
    if 'hour' not in df.columns and 'access_time' in df.columns:
        df['hour'] = pd.to_datetime(
            df['access_time'], format='%H:%M:%S', errors='coerce').dt.hour.fillna(0)

    # ------------------------------------------------------
    # 🔍 Sidebar Filters
    # ------------------------------------------------------
    st.sidebar.header("🔍 Filters")

    # Time range filter
    if "timestamp" in df.columns:
        min_date = df["timestamp"].min().date()
        max_date = df["timestamp"].max().date()
        date_range = st.sidebar.date_input(
            "📅 Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            df = df[(df["timestamp"].dt.date >= date_range[0]) &
                    (df["timestamp"].dt.date <= date_range[1])]

    # User filter
    if "user_id" in df.columns:
        users = ["All"] + sorted(df["user_id"].unique().tolist())
        selected_user = st.sidebar.selectbox("👤 User ID", users)
        if selected_user != "All":
            df = df[df["user_id"] == selected_user]

    # Anomaly type filter
    if "event_label" in df.columns:
        anomaly_labels = [
            "All"] + sorted([l for l in df["event_label"].unique() if l != ZERO_TRUST_NORMAL_LABEL])
        selected_anomaly = st.sidebar.selectbox(
            "🚨 Anomaly Type", anomaly_labels)
        if selected_anomaly != "All":
            df = df[df["event_label"] == selected_anomaly]

    # Login success filter
    if "login_success" in df.columns:
        login_filter = st.sidebar.selectbox(
            "✅ Login Success", ["All", "Success (1)", "Failed (0)"])
        if login_filter == "Success (1)":
            df = df[df["login_success"] == 1]
        elif login_filter == "Failed (0)":
            df = df[df["login_success"] == 0]

    # Location filter
    if "location" in df.columns:
        locations = ["All"] + sorted(df["location"].unique().tolist())
        selected_location = st.sidebar.selectbox("📍 Location", locations)
        if selected_location != "All":
            df = df[df["location"] == selected_location]

    # Anomaly status filter
    if "is_anomaly" in df.columns:
        anomaly_status = st.sidebar.selectbox(
            "🔍 Anomaly Status", ["All", "Normal Only", "Anomalies Only"])
        if anomaly_status == "Normal Only":
            df = df[df["is_anomaly"] == False]
        elif anomaly_status == "Anomalies Only":
            df = df[df["is_anomaly"] == True]

    # Real-time indicator
    if realtime_mode and realtime_df is not None and not realtime_df.empty:
        latest_event_time = realtime_df["timestamp"].max(
        ) if "timestamp" in realtime_df.columns else None
        if latest_event_time:
            time_diff = (datetime.now() -
                         pd.to_datetime(latest_event_time)).total_seconds()
            if time_diff < 10:
                st.success(f"🟢 Real-Time: Latest event {int(time_diff)}s ago")
            elif time_diff < 60:
                st.info(f"🟡 Recent: Latest event {int(time_diff)}s ago")
            else:
                st.warning(f"🔴 Stale: Latest event {int(time_diff/60)}m ago")

    # ------------------------------------------------------
    # 📊 Top Section: Key Metrics
    # ------------------------------------------------------
    st.header("📈 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    total_events = len(df)
    anomalies = df["is_anomaly"].sum() if "is_anomaly" in df.columns else 0
    anomaly_rate = (anomalies / total_events * 100) if total_events > 0 else 0

    # Calculate MTTD (Mean Time To Detect)
    mttd = None
    if "timestamp" in df.columns and "is_anomaly" in df.columns:
        anomaly_times = df[df["is_anomaly"] == True]["timestamp"]
        if len(anomaly_times) > 1:
            time_diffs = anomaly_times.sort_values().diff().dropna()
            mttd = time_diffs.mean() if len(time_diffs) > 0 else None

    with col1:
        st.metric("Total Events", f"{total_events:,}")

    with col2:
        st.metric("Anomalies Detected",
                  f"{anomalies:,}", delta=f"{anomaly_rate:.2f}%")

    with col3:
        st.metric("Anomaly Rate", f"{anomaly_rate:.2f}%")

    with col4:
        if mttd:
            mttd_str = str(mttd).split('.')[0]  # Remove microseconds
            st.metric("Avg. MTTD", mttd_str)
        else:
            st.metric("Avg. MTTD", "N/A")

    # ------------------------------------------------------
    # 📊 Middle Section: Visualizations
    # ------------------------------------------------------
    st.header("📊 Visualizations")

    # Line chart: Login events over time
    if "timestamp" in df.columns and "is_anomaly" in df.columns:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Login Events Over Time")
            df_time = df.groupby(
                [df["timestamp"].dt.date, "is_anomaly"]).size().reset_index(name="count")
            df_time["timestamp"] = pd.to_datetime(df_time["timestamp"])
            df_time["status"] = df_time["is_anomaly"].map(
                {True: "Anomaly", False: "Normal"})

            fig_time = px.line(
                df_time, x="timestamp", y="count", color="status",
                color_discrete_map={"Normal": "#00cc00", "Anomaly": "#ff0000"},
                labels={"count": "Number of Events", "timestamp": "Date"},
                title="Login Events Timeline"
            )
            fig_time.update_layout(showlegend=True, height=400)
            st.plotly_chart(fig_time, use_container_width=True)

        with col2:
            st.subheader("🚨 Anomalies by Type")
            if "event_label" in df.columns:
                anomaly_df = df[df["is_anomaly"] == True]
                if len(anomaly_df) > 0:
                    anomaly_counts = anomaly_df["event_label"].value_counts().head(
                        10)
                    fig_bar = px.bar(
                        x=anomaly_counts.index,
                        y=anomaly_counts.values,
                        labels={"x": "Anomaly Type", "y": "Count"},
                        title="Top Anomaly Types",
                        color=anomaly_counts.values,
                        color_continuous_scale="Reds"
                    )
                    fig_bar.update_layout(
                        showlegend=False, height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("No anomalies detected in filtered data")
            else:
                st.info("Anomaly type breakdown not available")

    # Geo plot: IP login locations
    if "location" in df.columns:
        st.subheader("🌍 Login Locations")
        col1, col2 = st.columns([2, 1])

        with col1:
            location_counts = df.groupby(
                ["location", "is_anomaly"]).size().reset_index(name="count")
            location_totals = df.groupby(
                "location").size().reset_index(name="total")
            location_anomalies = df[df["is_anomaly"] == True].groupby(
                "location").size().reset_index(name="anomalies")
            location_stats = location_totals.merge(
                location_anomalies, on="location", how="left").fillna(0)
            location_stats["anomaly_rate"] = (
                location_stats["anomalies"] / location_stats["total"] * 100).round(2)

            # Simple bar chart for locations (geo mapping would require geocoding)
            fig_geo = px.bar(
                location_stats.sort_values("anomalies", ascending=False),
                x="location",
                y=["total", "anomalies"],
                barmode="group",
                labels={"value": "Count", "location": "Location"},
                title="Login Activity by Location",
                color_discrete_map={"total": "#3498db", "anomalies": "#e74c3c"}
            )
            fig_geo.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_geo, use_container_width=True)

        with col2:
            st.write("**Location Statistics**")
            st.dataframe(
                location_stats.sort_values("anomaly_rate", ascending=False)[
                    ["location", "total", "anomalies", "anomaly_rate"]],
                use_container_width=True,
                hide_index=True
            )

    # ------------------------------------------------------
    # 📋 Bottom Section: Interactive Table
    # ------------------------------------------------------
    st.header("📋 Event Details")

    # Display columns
    display_cols = [
        "timestamp", "user_id", "device_id", "ip_address", "location",
        "login_success", "access_time", "resource_accessed",
        "bytes_transferred", "event_label"
    ]

    available_cols = [col for col in display_cols if col in df.columns]
    if "is_anomaly" in df.columns:
        available_cols.insert(0, "is_anomaly")

    # Add prediction column if model is available
    if iso_model is not None and scaler is not None:
        try:
            # Prepare features for prediction
            features = ['user_id', 'device_id', 'ip_address', 'location',
                        'login_success', 'hour', 'resource_accessed', 'bytes_transferred']

            # Create a copy for encoding
            df_pred = df.copy()

            # Encode categorical features
            for col in ['user_id', 'device_id', 'ip_address', 'location', 'resource_accessed']:
                if col in df_pred.columns and df_pred[col].dtype == 'object':
                    le = LabelEncoder()
                    df_pred[col] = le.fit_transform(df_pred[col].astype(str))

            # Check if all features exist
            missing = [f for f in features if f not in df_pred.columns]
            if not missing:
                X = scaler.transform(df_pred[features])
                preds = np.where(iso_model.predict(
                    X) == -1, ZERO_TRUST_POSITIVE_LABEL, ZERO_TRUST_NORMAL_LABEL)
                df["model_prediction"] = preds
                available_cols.append("model_prediction")
        except Exception as e:
            st.warning(f"Could not generate model predictions: {e}")

    # Display table with conditional styling for anomalies
    display_df = df[available_cols].copy()

    # Apply styling if is_anomaly column exists
    if "is_anomaly" in display_df.columns:
        # Create styled dataframe with red background for anomalies
        def highlight_anomalies(row):
            """Apply red background to anomaly rows"""
            is_anomaly = row.get("is_anomaly", False)
            # Convert to boolean if needed (handles 1/0, True/False, etc.)
            is_anomaly = bool(is_anomaly) if pd.notna(is_anomaly) else False

            if is_anomaly:
                # Light red background for entire row
                return ['background-color: #ffcccc; color: #000000'] * len(row)
            return [''] * len(row)

        try:
            styled_df = display_df.style.apply(highlight_anomalies, axis=1)
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=400
            )
            st.caption("🔴 Rows highlighted in red indicate anomalies detected")
        except Exception as e:
            # Fallback if styling doesn't work
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
            st.caption("💡 Anomalies are marked in the 'is_anomaly' column")
    else:
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )

    # Export functionality
    st.subheader("💾 Export Data")
    col1, col2 = st.columns(2)

    with col1:
        csv = df[available_cols].to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name=f"anomaly_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    with col2:
        st.info(f"📊 Showing {len(df)} of {total_events} total records")

    # ------------------------------------------------------
    # 🧠 SHAP Explainability (optional)
    # ------------------------------------------------------
    if iso_model is not None and scaler is not None:
        st.header("🧠 Model Explainability")
        if st.checkbox("🔍 Show SHAP Feature Importance"):
            sample_size = min(200, len(df))
            if sample_size > 0:
                try:
                    st.info("Generating SHAP values... please wait.")
                    # Prepare features
                    df_shap = df.copy()
                    for col in ['user_id', 'device_id', 'ip_address', 'location', 'resource_accessed']:
                        if col in df_shap.columns and df_shap[col].dtype == 'object':
                            le = LabelEncoder()
                            df_shap[col] = le.fit_transform(
                                df_shap[col].astype(str))

                    if all(f in df_shap.columns for f in features):
                        X_shap = scaler.transform(
                            df_shap[features][:sample_size])
                        background = X_shap[:min(100, len(X_shap))]

                        explainer = shap.KernelExplainer(
                            iso_model.decision_function, background)
                        shap_values = explainer.shap_values(background)
                        if isinstance(shap_values, list):
                            shap_values = shap_values[0]

                        st.write("### 💡 Feature Importance (SHAP Summary)")
                        shap.summary_plot(
                            shap_values, background, feature_names=features, show=False)
                        st.pyplot(bbox_inches='tight')
                except Exception as e:
                    st.error(f"SHAP analysis failed: {e}")

else:
    # Show real-time events only if no main dataset
    if realtime_mode and realtime_df is not None and not realtime_df.empty:
        st.info(
            "📡 Showing real-time events only. Load default dataset for full analysis.")
        df = realtime_df

        # Parse timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df.dropna(subset=["timestamp"])

        # Extract hour if access_time exists
        if 'hour' not in df.columns and 'access_time' in df.columns:
            df['hour'] = pd.to_datetime(
                df['access_time'], format='%H:%M:%S', errors='coerce').dt.hour.fillna(0)

        # Apply Zero-Trust labeling
        if "event_label" in df.columns:
            df["binary_label"] = (df["event_label"] !=
                                  ZERO_TRUST_NORMAL_LABEL).astype(int)
            df["is_anomaly"] = df["binary_label"] == 1
            # Extract anomaly types
            anomaly_types = [
                "impossible_travel", "off_hours_login", "multiple_failed_logins",
                "large_data_transfer", "unusual_resource_access"
            ]
            for atype in anomaly_types:
                df[f"has_{atype}"] = df["event_label"].str.contains(
                    atype, case=False, na=False)
        elif "is_anomaly" in df.columns:
            df["binary_label"] = df["is_anomaly"]

        # Now process through the same pipeline as main dataset
        # (This will be handled by the if df is not None block above, but we need to set it up)
        # For now, show a simplified view
        st.header("📈 Real-Time Events Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Events", len(df))
        with col2:
            anomalies = df["is_anomaly"].sum(
            ) if "is_anomaly" in df.columns else 0
            st.metric("Anomalies", anomalies)
        with col3:
            anomaly_rate = (anomalies / len(df) * 100) if len(df) > 0 else 0
            st.metric("Anomaly Rate", f"{anomaly_rate:.2f}%")

        st.subheader("📋 Recent Events")
        display_cols = ["timestamp", "user_id", "device_id", "ip_address", "location",
                        "login_success", "resource_accessed", "bytes_transferred", "event_label"]
        available_cols = [col for col in display_cols if col in df.columns]
        if "is_anomaly" in df.columns:
            available_cols.insert(0, "is_anomaly")

        display_df = df[available_cols].head(50).copy()

        # Apply styling if is_anomaly column exists
        if "is_anomaly" in display_df.columns:
            def highlight_anomalies(row):
                """Apply red background to anomaly rows"""
                is_anomaly = row.get("is_anomaly", False)
                # Convert to boolean if needed (handles 1/0, True/False, etc.)
                is_anomaly = bool(is_anomaly) if pd.notna(
                    is_anomaly) else False

                if is_anomaly:
                    # Light red background for entire row
                    return ['background-color: #ffcccc; color: #000000'] * len(row)
                return [''] * len(row)

            try:
                styled_df = display_df.style.apply(highlight_anomalies, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                st.caption(
                    "🔴 Rows highlighted in red indicate anomalies detected")
            except Exception as e:
                # Fallback if styling doesn't work
                st.dataframe(display_df, use_container_width=True)
                st.caption("💡 Anomalies are marked in the 'is_anomaly' column")
        else:
            st.dataframe(display_df, use_container_width=True)

    else:
        st.info(
            "⬆️ Please upload a CSV file or load the default dataset from the sidebar to begin.")

    # Show sample data structure
    st.subheader("📋 Expected Data Format")
    st.code("""
    Required columns:
    - timestamp: DateTime of the event
    - user_id: User identifier
    - device_id: Device identifier
    - ip_address: IP address
    - location: Geographic location
    - login_success: 1 for success, 0 for failure
    - access_time: Time of access (HH:MM:SS)
    - resource_accessed: Resource name
    - bytes_transferred: Data transfer amount
    - event_label: Event classification (normal, off_hours_login, etc.)
    """)
