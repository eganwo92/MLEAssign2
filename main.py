# main.py
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier
import joblib
from utils.monitoring import log_metrics

def main():
    print("🚀 Starting ML pipeline (Assignment 2)")

    # === 1. Load Gold table ===
    gold_path = "datamart/gold/feature_store.csv"
    df = pd.read_csv(gold_path)
    print(f"✅ Gold table loaded: {df.shape[0]} rows, {df.shape[1]} cols")

    # === 2. Prepare features and label ===
    X = df.drop(columns=["default_flag", "customer_id"])
    y = df["default_flag"]

    # === 3. Train/test split ===
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # === 4. Train XGBoost baseline ===
    model = XGBClassifier(
        n_estimators=300, learning_rate=0.05, max_depth=5,
        subsample=0.8, colsample_bytree=0.8, random_state=42,
        eval_metric="auc"
    )
    model.fit(X_train, y_train)
    print("✅ Model training complete")

    # === 5. Evaluate model ===
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }
    print(f"📊 Model performance: {metrics}")

    # === 6. Save model and metrics ===
    os.makedirs("model_store", exist_ok=True)
    joblib.dump(model, "model_store/xgb_baseline.pkl")
    log_metrics(metrics)
    print("✅ Model and metrics saved")

    print("🏁 Pipeline finished successfully")

if __name__ == "__main__":
    main()
