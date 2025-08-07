# predict.py

import pandas as pd
import joblib
import os

def run_po_delay_model(df, threshold=0.7):
    model_path = "models/model.pkl"
    if not os.path.exists(model_path):
        raise FileNotFoundError("Trained model not found in 'models/model.pkl'")

    model = joblib.load(model_path)

    # Feature Engineering - match training
    date_cols = ['po_date', 'receiver_date', 'date_last_changed', 'date_passed_to_acctg', 'payment_date']
    for col in date_cols:
        if col in df.columns:
            df[f"{col}_month"] = df[col].dt.month
            df[f"{col}_weekday"] = df[col].dt.weekday

    df.drop(columns=date_cols, inplace=True, errors='ignore')

    # Drop target if present
    if 'days_to_close' in df.columns:
        df = df.drop(columns=['days_to_close'])

    # Apply same encoding
    X = pd.get_dummies(df)

    # Align with model training features
    model_features = model.get_booster().feature_names
    for col in model_features:
        if col not in X.columns:
            X[col] = 0  # Add missing
    X = X[model_features]  # Match order

    # Predict
    probs = model.predict_proba(X)[:, 1]
    df['delay_risk_score'] = probs
    df['is_late_predicted'] = (probs >= threshold)

    alert_df = df[df['is_late_predicted'] == True]
    return df, alert_df
