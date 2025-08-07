import os
import streamlit as st
import pandas as pd
from clean_data import clean_uploaded_file
from train_model import train_model_on_dataframe
from predict import run_po_delay_model
from vendor_analysis import generate_vendor_report
from alert_email import send_alert_email
import datetime

# ------------------------------
# Streamlit Config
# ------------------------------
st.set_page_config(
    page_title="PO Delay & Vendor Analysis",
    layout="wide",
    initial_sidebar_state="auto"
)

# ------------------------------
# Role-Based Login with Multi-Domain Support
# ------------------------------
CORRECT_PASSWORD = st.secrets["auth"]["password"]
ADMIN_EMAIL = st.secrets["auth"]["admin"]
ANALYST_EMAILS = st.secrets["auth"]["analysts"]
ALLOWED_DOMAINS = st.secrets["auth"]["allowed_domains"]

st.sidebar.title("🔐 Login Required")
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    domain = email.split("@")[-1] if "@" in email else ""
    if domain in ALLOWED_DOMAINS and password == CORRECT_PASSWORD:
        st.session_state["authenticated"] = True
        st.session_state["user_email"] = email
    else:
        st.sidebar.error("❌ Invalid credentials or unauthorized email domain.")

# Auth check
if "authenticated" not in st.session_state:
    st.stop()

user_email = st.session_state["user_email"]
if user_email == ADMIN_EMAIL:
    user_role = "admin"
elif user_email in ANALYST_EMAILS:
    user_role = "analyst"
else:
    user_role = "viewer"
    st.error("Access denied: Your email is not authorized.")
    st.stop()

st.title("📦 Purchase Order Delay Prediction & Vendor Performance Dashboard")

# ------------------------------
# File Upload Section
# ------------------------------
uploaded_file = st.file_uploader("Upload PO Excel File", type=["xlsx"])

if uploaded_file:
    st.info("✅ File uploaded. Starting processing...")

    try:
        df_clean = clean_uploaded_file(uploaded_file)
        st.success("✅ Data cleaned successfully.")
        st.dataframe(df_clean.head(), use_container_width=True)

        from log_to_gsheet import log_to_google_sheet
        log_to_google_sheet(user_email, uploaded_file.name, len(df_clean))

        train_model_on_dataframe(df_clean)
        st.success("✅ Model trained and saved.")

        st.sidebar.header("Prediction Settings")
        threshold = st.sidebar.slider("Set delay risk threshold", 0.0, 1.0, 0.7)

        prediction_df, alert_df = run_po_delay_model(df_clean, threshold=threshold)
        st.success("✅ Predictions completed.")

        ONEDRIVE_PATH = r"C:\Users\sarit\OneDrive - brandeis.edu\PO_Delay_Folder"
        os.makedirs(ONEDRIVE_PATH, exist_ok=True)
        one_drive_file_path = os.path.join(ONEDRIVE_PATH, "po_predictions.csv")
        prediction_df.to_csv(one_drive_file_path, index=False)
        st.success(f"✅ File also saved to OneDrive: {one_drive_file_path}")

        vendor_df = generate_vendor_report(df_clean)
        st.success("✅ Vendor report generated.")

        tab1, tab2 = st.tabs(["🔮 PO Delay Prediction", "📊 Vendor Performance Analysis"])

        with tab1:
            st.subheader("🔮 Delay Predictions")
            st.dataframe(prediction_df, use_container_width=True)

            st.download_button(
                "📥 Download Prediction Results",
                data=prediction_df.to_csv(index=False).encode(),
                file_name="predictions.csv",
                mime="text/csv"
            )

            if not alert_df.empty:
                st.warning(f"⚠️ {len(alert_df)} high-risk delayed POs detected.")
                st.dataframe(alert_df, use_container_width=True)

                if st.button("✉️ Send Alert Email"):
                    send_alert_email(alert_df)

        if user_role == "admin":
            with tab2:
                st.subheader("📊 Vendor Performance")
                st.dataframe(vendor_df, use_container_width=True)

                st.download_button(
                    "📥 Download Vendor Report",
                    data=vendor_df.to_csv(index=False).encode(),
                    file_name="vendor_report.csv",
                    mime="text/csv"
                )

        # ------------------------------
        # Power BI Dashboard Embed
        # ------------------------------
        st.markdown("---")
        st.subheader("📈 Live Power BI Dashboard")
        st.info("This dashboard is connected to your synced OneDrive predictions folder.")

        st.markdown("""
<h3>📊 Power BI Dashboard</h3>
<iframe width="100%" height="800"
        src="https://app.powerbi.com/view?r=eyJrIjoiN2QzYzY0ZjItZTAzZC00MTFiLWI1OWItNmYyM2ExMThkOTRkIiwidCI6IjAyZTQ5NmUwLWJiOGYtNGVjMy1iZjRkLTZlM2NkNGJkNGJhNCIsImMiOjN9" 
        frameborder="0" allowFullScreen="true">
</iframe>
""", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"🚨 An error occurred: {e}")

else:
    st.warning("📄 Please upload a raw PO Excel file to begin.")
