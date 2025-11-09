import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
from xgboost import XGBClassifier
import datetime  # ✅ safer import (no shadowing)
import joblib
import json
from pathlib import Path
from utils.split_temporal import temporal_split


def do_temporal_split():
    """Loads gold table and performs temporal split."""
    gold_path = "/opt/airflow/datamart/gold/feature_store.csv"
    df = pd.read_csv(gold_path)
    print(f"✅ Gold table loaded: {df.shape[0]} rows × {df.shape[1]} cols")

    splits = temporal_split(df)
    print("✅ Temporal split completed successfully!")
    return splits


def check_and_retrain():
    flag = Path("/opt/airflow/model_store/RETRAIN_REQUESTED.flag")
    model_path = Path("/opt/airflow/model_store/best_model.pkl")

    # ✅ Skip retrain if model already exists and no flag
    if not flag.exists() and model_path.exists():
        print("✅ Model already trained and no retrain requested today.")
        return

    print("🚀 Training (or retraining) triggered...")
    flag.unlink(missing_ok=True)

    df = pd.read_csv("/opt/airflow/datamart/gold/feature_store.csv")
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    cutoff = datetime.datetime.now()

    # ✅ Filter training data up to cutoff
    train_df = df[df["snapshot_date"] <= cutoff]

    # Separate features and labels
    X = train_df.drop(columns=["default_flag", "customer_id"], errors="ignore")
    y = train_df["default_flag"]

    # ✅ Drop unsupported or non-numeric columns before training
    drop_cols = ["snapshot_date", "month"]
    X = X.drop(columns=drop_cols, errors="ignore")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # ✅ Train XGBoost model
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

    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba)
    }

    # ✅ Save model and metadata
    Path("/opt/airflow/model_store").mkdir(parents=True, exist_ok=True)
    version_tag = cutoff.strftime("v%Y%m%d_%H%M%S")
    versioned_model_path = f"/opt/airflow/model_store/{version_tag}_model.pkl"
    joblib.dump(model, versioned_model_path)

    # Also save latest model as best_model.pkl for production reference
    joblib.dump(model, "/opt/airflow/model_store/best_model.pkl")

    meta = {
        "model_name": "best_model.pkl",
        "versioned_model": f"{version_tag}_model.pkl",
        "trained_until": cutoff.strftime("%Y-%m-%d %H:%M:%S"),
        "rows_trained": len(X_train),
        "metrics": {
            "accuracy": round(metrics["accuracy"], 4),
            "roc_auc": round(metrics["roc_auc"], 4),
        },
        "version": version_tag
    }

    meta = {
        "model_name": "best_model.pkl",
        "trained_until": cutoff.strftime("%Y-%m-%d %H:%M:%S"),
        "rows_trained": len(X_train),
        "metrics": {
            "accuracy": round(metrics["accuracy"], 4),
            "roc_auc": round(metrics["roc_auc"], 4),
        },
        "version": cutoff.strftime("v%Y%m%d_%H%M%S")
    }

    with open("/opt/airflow/model_store/metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"✅ Training complete — Accuracy {metrics['accuracy']:.3f}, AUC {metrics['roc_auc']:.3f}")
    print(f"🧾 Model metadata saved → /opt/airflow/model_store/metadata.json")


if __name__ == "__main__":
    check_and_retrain()
