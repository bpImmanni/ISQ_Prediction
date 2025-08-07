# app.py

import streamlit as st
import pandas as pd
from clean_data import clean_uploaded_file
from train_model import train_model_on_dataframe
from predict import run_po_delay_model
from vendor_analysis import generate_vendor_report
from alert_email import send_alert_email

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

    except Exception as e:
        st.error(f"🚨 An error occurred: {e}")

else:
    st.warning("📄 Please upload a raw PO Excel file to begin.")
