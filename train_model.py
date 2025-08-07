# train_model.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

def train_model_on_dataframe(df):
    """
    Trains a delay prediction model using in-memory cleaned DataFrame.
    Saves the trained model to models/model.pkl.
    """
    # Ensure output folder exists
    os.makedirs("models", exist_ok=True)

    # Create target column: delay if days_to_close > 30
    if 'days_to_close' not in df.columns:
        raise ValueError("Missing 'days_to_close' column in DataFrame.")
    
    df = df.copy()
    df['is_delayed'] = (df['days_to_close'] > 30).astype(int)

    # Features to use
    features = [
        'days_aging', 'po_type', 'po_status_desc', 'cost_amount',
        'order_qty', 'po_agent', 'facility_description', 'warehouse'
    ]

    # Check for missing features
    missing = [col for col in features if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in training data: {missing}")

    # One-hot encode
    X = pd.get_dummies(df[features])
    y = df['is_delayed']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X_train, y_train)

    # Optional: Print evaluation to console
    y_pred = model.predict(X_test)
    print("\n✅ Model Evaluation:")
    print(classification_report(y_test, y_pred))

    # Save model
    model.feature_names_in_ = X.columns  # save input features for use in predict.py
    joblib.dump(model, "models/model.pkl")
    print("✅ Trained model saved to models/model.pkl")
