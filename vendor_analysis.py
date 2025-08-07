# vendor_analysis.py

import pandas as pd

def generate_vendor_report(df):
    """
    Generates vendor performance metrics from cleaned PO data.
    Returns a summary DataFrame grouped by vendor.
    """
    if 'vendor_name' not in df.columns:
        raise ValueError("Missing 'vendor_name' column in input data.")

    df = df.copy()

    # Create binary delay flag
    df['is_delayed'] = (df['days_to_close'] > 30).astype(int)

    # Group by vendor and calculate metrics
    vendor_summary = df.groupby('vendor_name').agg(
        total_pos=('po_number', 'count'),
        avg_days_to_close=('days_to_close', 'mean'),
        delayed_pos=('is_delayed', 'sum')
    ).reset_index()

    # Add delay rate %
    vendor_summary['delay_rate_%'] = (
        vendor_summary['delayed_pos'] / vendor_summary['total_pos'] * 100
    ).round(2)

    # Reorder and format
    vendor_summary = vendor_summary[[
        'vendor_name', 'total_pos', 'avg_days_to_close', 'delayed_pos', 'delay_rate_%'
    ]]
    vendor_summary.sort_values(by='delay_rate_%', ascending=False, inplace=True)

    return vendor_summary
