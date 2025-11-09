import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime


def run_daily_inference():
    model_path = Path("/opt/airflow/model_store/best_model.pkl")
    gold_path = Path("/opt/airflow/datamart/gold/feature_store.csv")
    pred_path = Path("/opt/airflow/datamart/gold/predictions.csv")

    # --- 1. Validate model and feature store existence ---
    if not model_path.exists():
        raise FileNotFoundError(f"❌ Model file not found: {model_path}")
    if not gold_path.exists():
        raise FileNotFoundError(f"❌ Gold feature store not found: {gold_path}")

    model = joblib.load(model_path)
    df = pd.read_csv(gold_path)
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")

    # --- 2. Load last predictions if available ---
    if pred_path.exists():
        preds = pd.read_csv(pred_path)
        preds["snapshot_date"] = pd.to_datetime(preds["snapshot_date"], errors="coerce")
        last_date = preds["snapshot_date"].max()
        new_data = df[df["snapshot_date"] > last_date]
    else:
        preds = pd.DataFrame()
        new_data = df.copy()

    if new_data.empty:
        print("ℹ️ No new data for inference today.")
        return

    # --- 3. Prepare features ---
    X_new = new_data.drop(columns=["customer_id", "default_flag"], errors="ignore")

    # 🚨 Drop datetime and any other unsupported columns
    drop_cols = ["snapshot_date", "month"]
    X_new = X_new.drop(columns=drop_cols, errors="ignore")

    # --- 4. Run model inference ---
    y_pred = model.predict(X_new)
    y_proba = model.predict_proba(X_new)[:, 1]

    new_data["pred_default_flag"] = y_pred
    new_data["pred_prob"] = y_proba

    # --- 5. Append to predictions file ---
    preds = pd.concat([preds, new_data], ignore_index=True)
    preds.to_csv(pred_path, index=False)

    print(f"✅ Inference complete for {len(new_data)} new rows — stored in {pred_path}")


if __name__ == "__main__":
    run_daily_inference()
