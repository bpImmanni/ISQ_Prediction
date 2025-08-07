# app.py

import os
import streamlit as st
import pandas as pd
from clean_data import clean_uploaded_file
from train_model import train_model_on_dataframe
from predict import run_po_delay_model
from vendor_analysis import generate_vendor_report
from alert_email import send_alert_email

# Simple domain-based login
ALLOWED_DOMAIN = "brandeis.edu"
CORRECT_PASSWORD = st.secrets["auth"]["password"]  # stored securely in .streamlit/secrets.toml

def login():
    st.sidebar.title("🔐 Login Required")
    email = st.sidebar.text_input("Email", "")
    password = st.sidebar.text_input("Password", "", type="password")

    if st.sidebar.button("Login"):
        if email.endswith(f"@{ALLOWED_DOMAIN}") and password == CORRECT_PASSWORD:
            st.session_state["authenticated"] = True
        else:
            st.sidebar.error("❌ Invalid credentials. Only @brandeis.edu emails allowed.")

# Check session
if "authenticated" not in st.session_state:
    login()
    st.stop()


# ------------------------------
# Streamlit Config
# ------------------------------
st.set_page_config(
    page_title="PO Delay & Vendor Analysis",
    layout="wide",
    initial_sidebar_state="auto"
)

st.title("📦 Purchase Order Delay Prediction & Vendor Performance Dashboard")

# ------------------------------
# File Upload Section
# ------------------------------
uploaded_file = st.file_uploader("Upload PO Excel File", type=["xlsx"])

if uploaded_file:
    st.info("✅ File uploaded. Starting processing...")

    try:
        # Step 1: Clean the uploaded file
        df_clean = clean_uploaded_file(uploaded_file)
        st.success("✅ Data cleaned successfully.")
        st.dataframe(df_clean.head(), use_container_width=True)

        # Step 2: Train model on cleaned data
        train_model_on_dataframe(df_clean)
        st.success("✅ Model trained and saved.")

        # Sidebar settings
        st.sidebar.header("Prediction Settings")
        threshold = st.sidebar.slider("Set delay risk threshold", 0.0, 1.0, 0.7)

        # Step 3: Run predictions
        prediction_df, alert_df = run_po_delay_model(df_clean, threshold=threshold)
        st.success("✅ Predictions completed.")

        # Save to OneDrive folder
        ONEDRIVE_PATH = r"C:\Users\sarit\OneDrive - brandeis.edu\PO_Delay_Folder"
        os.makedirs(ONEDRIVE_PATH, exist_ok=True)
        one_drive_file_path = os.path.join(ONEDRIVE_PATH, "po_predictions.csv")
        prediction_df.to_csv(one_drive_file_path, index=False)
        st.success(f"✅ File also saved to OneDrive: {one_drive_file_path}")

        # Step 4: Vendor metrics
        vendor_df = generate_vendor_report(df_clean)
        st.success("✅ Vendor report generated.")

        # Debug checks
        st.write("🔎 prediction_df:", prediction_df.shape)
        st.write("🔎 vendor_df:", vendor_df.shape)

        # ------------------------------
        # Tabs for Results
        # ------------------------------
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

        powerbi_embed_url = "https://app.powerbi.com/links/2-N4iVJRGt?ctid=02e496e0-bb8f-4ec3-bf4d-6e3cd4bd4ba4&pbi_source=linkShare"

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
