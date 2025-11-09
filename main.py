# main.py
import os
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score
)
import joblib
from utils.split_temporal import temporal_split
from utils.monitoring_utils import log_metrics


def main():
    print("🚀 Starting ML pipeline (Assignment 2)")

    # === 1. Load Gold Table ===
    gold_path = "datamart/gold/feature_store.csv"
    df = pd.read_csv(gold_path)
    print(f"✅ Gold table loaded: {df.shape[0]} rows × {df.shape[1]} cols")

    # === 2. Temporal Split ===
    splits = temporal_split(df)
    train_df, val_df = splits["train"], splits["val"]

    X_train = train_df.drop(columns=["default_flag", "customer_id", "snapshot_date"], errors="ignore")
    y_train = train_df["default_flag"]
    X_val = val_df.drop(columns=["default_flag", "customer_id", "snapshot_date"], errors="ignore")
    y_val = val_df["default_flag"]

    # Drop unsupported period column
    X_train = X_train.drop(columns=["month"], errors="ignore")
    X_val = X_val.drop(columns=["month"], errors="ignore")

    # === 3. Train XGBoost baseline ===
    model = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="auc"
    )

    model.fit(X_train, y_train)
    print("✅ Model training complete")

    # === 4. Evaluate on validation ===
    y_pred = model.predict(X_val)
    y_proba = model.predict_proba(X_val)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_val, y_pred),
        "precision": precision_score(y_val, y_pred),
        "recall": recall_score(y_val, y_pred),
        "f1": f1_score(y_val, y_pred),
        "roc_auc": roc_auc_score(y_val, y_proba),
    }

    print("📊 Model performance:")
    for k, v in metrics.items():
        print(f"   {k}: {v:.3f}")

    # === 5. Save model + metrics ===
    os.makedirs("model_store", exist_ok=True)
    joblib.dump(model, "model_store/xgb_baseline.pkl")
    joblib.dump(model, "model_store/best_model.pkl")
    log_metrics(metrics)

    print("✅ Model and metrics saved")
    print("🏁 Pipeline finished successfully")


if __name__ == "__main__":
    main()
