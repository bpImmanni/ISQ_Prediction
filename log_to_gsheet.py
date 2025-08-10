import datetime
import gspread
import streamlit as st
from google.oauth2 import service_account

def log_to_google_sheet(user_email, file_name, row_count):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Load credentials from Streamlit secrets
    creds_info = st.secrets["gcp_service_account"]

    # Create credentials object
    creds = service_account.Credentials.from_service_account_info(creds_info, scopes=scope)

    # Authorize and open sheet
    client = gspread.authorize(creds)
    sheet = client.open("PO_Upload_Logs").sheet1

    # Log entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, user_email, file_name, row_count])
