# alert_email.py

import yagmail
import pandas as pd
from io import BytesIO
import streamlit as st

def send_alert_email(alert_df):
    """
    Sends an email with delayed POs as Excel attachment.
    Supports multiple recipients using secrets.toml list.
    """
    if alert_df.empty:
        st.warning("No delayed POs to send.")
        return

    # Load credentials and recipients from secrets.toml
    sender = st.secrets["email"]["sender"]
    password = st.secrets["email"]["password"]
    recipients = st.secrets["email"]["recipient"]  # should be a list in secrets.toml

    # Create in-memory Excel file
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        alert_df.to_excel(writer, index=False, sheet_name='Delayed POs')
    excel_buffer.seek(0)

    # Email content
    subject = "⚠️ PO Delay Alert: High-Risk POs Identified"
    body = (
        "Hi Team,\n\n"
        "Attached is the list of purchase orders predicted to be delayed.\n"
        "Please review and take necessary action.\n\n"
        "Best regards,\n"
        "PO Delay Prediction System"
    )

    try:
        yag = yagmail.SMTP(user=sender, password=password)
        yag.send(
            to=recipients,
            subject=subject,
            contents=body,
            attachments=[("delayed_pos_alert.xlsx", excel_buffer.read())]
        )
        st.success(f"✅ Alert email sent to: {', '.join(recipients)}")
    except Exception as e:
        st.error(f"❌ Failed to send alert email: {e}")
