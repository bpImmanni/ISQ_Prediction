import pandas as pd
import re
import logging
from collections import Counter

# Optional logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

def clean_uploaded_file(uploaded_file):
    """
    Cleans the uploaded PO Excel file based on approved columns.
    Returns a cleaned pandas DataFrame.
    """

    # Expected column names after normalization
    allowed_cleaned_columns = {
        'po_number', 'po_date', 'date_last_changed', 'date_passed_to_acctg', 'payment_date',
        'days_aging', 'days_to_close', 'po_type', 'po_status_desc', 'receiver_date',
        'cost_amount', 'order_qty', 'po_agent', 'vendor_name', 'facility_description', 'warehouse'
    }

    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        logging.info("✅ Excel file loaded successfully.")
    except Exception as e:
        logging.error(f"❌ Error reading Excel file: {e}")
        raise ValueError(f"❌ Error reading Excel file: {e}")

    # Drop empty rows/columns
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    # Normalize column names
    df.columns = [re.sub(r"\s+", "_", col.strip().lower()) for col in df.columns]

    # Handle duplicate columns (manual dedup for pandas >= 2.0)
    if df.columns.duplicated().any():
        original_cols = df.columns.tolist()

        def deduplicate_columns(cols):
            counts = Counter()
            new_cols = []
            for col in cols:
                if counts[col] == 0:
                    new_cols.append(col)
                else:
                    new_cols.append(f"{col}_{counts[col]}")
                counts[col] += 1
            return new_cols

        df.columns = deduplicate_columns(df.columns)
        logging.warning(f"⚠️ Duplicate column names renamed: {original_cols} → {df.columns.tolist()}")

    # Filter allowed columns
    df = df[[col for col in df.columns if col in allowed_cleaned_columns]]

    # Check for required columns
    required = ['po_number', 'vendor_name']
    missing = [col for col in required if col not in df.columns]
    if missing:
        logging.error(f"❌ Required columns missing: {missing}")
        raise ValueError(f"❌ Required columns missing: {missing}")

    df.dropna(subset=required, inplace=True)

    # Parse dates
    date_columns = ['po_date', 'date_last_changed', 'date_passed_to_acctg', 'payment_date', 'receiver_date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Create 'days_to_close' if missing
    if 'days_to_close' not in df.columns:
        if 'payment_date' in df.columns and 'po_date' in df.columns:
            df['days_to_close'] = (df['payment_date'] - df['po_date']).dt.days
            logging.info("ℹ️ 'days_to_close' calculated using payment_date - po_date.")
        elif 'date_last_changed' in df.columns and 'po_date' in df.columns:
            df['days_to_close'] = (df['date_last_changed'] - df['po_date']).dt.days
            logging.info("ℹ️ 'days_to_close' calculated using date_last_changed - po_date.")

    # Numeric conversions
    num_columns = ['po_number', 'days_aging', 'days_to_close', 'cost_amount', 'order_qty']
    for col in num_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Standardize text columns
    text_columns = ['po_type', 'po_status_desc', 'po_agent', 'vendor_name', 'facility_description', 'warehouse']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    logging.info("✅ Data cleaned and returned successfully.")
    return df
