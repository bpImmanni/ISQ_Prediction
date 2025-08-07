# train_model.py

import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
import joblib
import os

def train_model_on_dataframe(df):
    # Drop rows with missing target
    df = df.dropna(subset=['days_to_close'])

    # Binary classification: PO is delayed if days_to_close > 30
    df['is_late'] = df['days_to_close'] > 30

    # Drop raw target
    df = df.drop(columns=['days_to_close'])

    # Feature engineering - datetime columns
    date_cols = ['po_date', 'receiver_date', 'date_last_changed', 'date_passed_to_acctg', 'payment_date']
    for col in date_cols:
        if col in df.columns:
            df[f"{col}_month"] = df[col].dt.month
            df[f"{col}_weekday"] = df[col].dt.weekday
    df.drop(columns=date_cols, inplace=True, errors='ignore')

    # One-hot encoding for categorical variables
    X = pd.get_dummies(df.drop(columns=['is_late']))
    y = df['is_late']

    # Align missing/extra columns
    X = X.fillna(0)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=42)

    # Train XGBoost model
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)

    # Save model
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/model.pkl")
