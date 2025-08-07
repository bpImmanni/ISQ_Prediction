# log_to_gsheet.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

def log_to_google_sheet(user_email, file_name, row_count):
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Load credentials
    creds = ServiceAccountCredentials.from_json_keyfile_name("gcp_service_account.json", scope)

    # Authorize and open the sheet
    client = gspread.authorize(creds)
    sheet = client.open("PO_Upload_Logs").sheet1

    # Prepare log entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, user_email, file_name, row_count]

    # Append to the sheet
    sheet.append_row(row)
