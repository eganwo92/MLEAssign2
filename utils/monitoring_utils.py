import pandas as pd
import json
from sklearn.metrics import accuracy_score, roc_auc_score
from datetime import datetime
from pathlib import Path

# === Absolute paths (inside Airflow container) ===
PRED_PATH = Path("/opt/airflow/datamart/gold/predictions.csv")
LOG_FILE = Path("/opt/airflow/monitoring_logs/metrics_log.json")
FLAG_FILE = Path("/opt/airflow/model_store/RETRAIN_REQUESTED.flag")
TRAIN_LOG = Path("/opt/airflow/model_store/training_metrics.json")

THRESHOLD_ACCURACY = 0.72


# ---------------------------------------------------------------------
# 🧾 Training-time metric logger (used by main.py)
# ---------------------------------------------------------------------
def log_metrics(metrics: dict):
    """Append training metrics to a JSON log file with timestamp."""
    TRAIN_LOG.parent.mkdir(parents=True, exist_ok=True)

    record = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **metrics}

    if TRAIN_LOG.exists():
        try:
            logs = json.load(open(TRAIN_LOG))
        except json.JSONDecodeError:
            logs = []
    else:
        logs = []

    logs.append(record)
    with open(TRAIN_LOG, "w") as f:
        json.dump(logs, f, indent=2)

    print(f"🧾 Logged training metrics → {TRAIN_LOG}: {record}")


# ---------------------------------------------------------------------
# 📊 Daily monitoring (used by DAG 08)
# ---------------------------------------------------------------------
def monitor_daily():
    """Monitor model performance daily and trigger retraining flag if accuracy drops."""
    if not PRED_PATH.exists():
        print(f"❌ Predictions file not found: {PRED_PATH}")
        return

    preds = pd.read_csv(PRED_PATH)
    preds["snapshot_date"] = pd.to_datetime(preds["snapshot_date"], errors="coerce")

    # Compare predictions vs actuals (if available)
    labeled = preds.dropna(subset=["default_flag"])
    if labeled.empty:
        print("⚠️ No labeled data yet — skipping performance calculation.")
        return

    y_true = labeled["default_flag"]
    y_pred = labeled["pred_default_flag"]
    y_proba = labeled["pred_prob"]

    acc = accuracy_score(y_true, y_pred)
    auc = roc_auc_score(y_true, y_proba)

    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "accuracy": round(acc, 4),
        "roc_auc": round(auc, 4),
    }

    # Log to monitoring file
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LOG_FILE.exists():
        try:
            logs = json.load(open(LOG_FILE))
        except json.JSONDecodeError:
            logs = []
    else:
        logs = []

    logs.append(record)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

    print(f"📊 Daily Monitoring: accuracy={acc:.3f}, AUC={auc:.3f}")

    # Check retrain threshold
    if acc < THRESHOLD_ACCURACY:
        FLAG_FILE.touch()
        print(f"🚨 Accuracy dropped below {THRESHOLD_ACCURACY}! Created retrain flag → {FLAG_FILE}")


if __name__ == "__main__":
    monitor_daily()
