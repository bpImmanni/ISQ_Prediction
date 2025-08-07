import pandas as pd
import re

def clean_uploaded_file(uploaded_file):
    """
    Cleans the uploaded PO Excel file based on approved columns.
    Returns a cleaned pandas DataFrame (no file saving).
    """

    # Define standard column names AFTER cleaning
    allowed_cleaned_columns = {
        'po_number', 'po_date', 'date_last_changed', 'date_passed_to_acctg', 'payment_date',
        'days_aging', 'days_to_close', 'po_type', 'po_status_desc', 'receiver_date',
        'cost_amount', 'order_qty', 'po_agent', 'vendor_name', 'facility_description', 'warehouse'
    }

    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"❌ Error reading Excel file: {e}")

    # Drop completely empty rows and columns
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    # Normalize column names: lowercase, replace non-word characters (space, dash, etc.) with _
    df.columns = [re.sub(r"[^\w]+", "_", col.strip().lower()) for col in df.columns]

    # Keep only allowed columns
    df = df[[col for col in df.columns if col in allowed_cleaned_columns]]

    # Validate required fields
    required = ['po_number', 'vendor_name']
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"❌ Required column(s) missing: {missing}")

    # Drop rows missing key fields
    df.dropna(subset=required, inplace=True)

    # Convert date columns
    date_columns = ['po_date', 'date_last_changed', 'date_passed_to_acctg', 'payment_date', 'receiver_date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Convert numeric columns
    num_columns = ['po_number', 'days_aging', 'days_to_close', 'cost_amount', 'order_qty']
    for col in num_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Clean text fields
    text_columns = ['po_type', 'po_status_desc', 'po_agent', 'vendor_name', 'facility_description', 'warehouse']
    for col in text_columns:
        if col in df.columns and isinstance(df[col], pd.Series):
            df[col] = df[col].astype(str).str.strip().str.upper()

    return df
