# predict.py

import pandas as pd
import numpy as np
import joblib
import os

MODEL_PATH = os.path.join("models", "model.pkl")

def run_po_delay_model(df_clean, threshold=0.7):
    """
    Loads the ML model, predicts delay probabilities, and returns:
    - Full dataframe with predictions
    - Alert dataframe with high-probability delays
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Trained model not found in 'models/model.pkl'")

    model = joblib.load(MODEL_PATH)

    features = [
        'days_aging', 'po_type', 'po_status_desc', 'cost_amount',
        'order_qty', 'po_agent', 'facility_description', 'warehouse'
    ]

    missing = [col for col in features if col not in df_clean.columns]
    if missing:
        raise ValueError(f"Missing columns for prediction: {missing}")

    X = pd.get_dummies(df_clean[features])
    model_features = model.feature_names_in_

    for col in model_features:
        if col not in X.columns:
            X[col] = 0

    X = X[model_features]

    probs = model.predict_proba(X)[:, 1]
    df_clean['delay_probability'] = probs
    df_clean['predicted_status'] = np.where(probs >= threshold, 'DELAYED', 'ON TIME')

    alert_df = df_clean[df_clean['predicted_status'] == 'DELAYED']
    alert_df = alert_df[alert_df['delay_probability'] >= threshold]

    return df_clean, alert_df
