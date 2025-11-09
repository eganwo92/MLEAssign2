import pandas as pd
import joblib
import json
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score, accuracy_score
from pathlib import Path
import datetime

# === Paths ===
gold_path = Path("/opt/airflow/datamart/gold/feature_store.csv")
model_path = Path("/opt/airflow/model_store/best_model.pkl")
meta_path = Path("/opt/airflow/model_store/metadata.json")
log_file = Path("/opt/airflow/monitoring_logs/monthly_scores.json")

# === Load model + metadata ===
if not model_path.exists():
    raise FileNotFoundError("❌ Model not found. Please retrain first.")
model = joblib.load(model_path)

model_version = "unknown"
trained_until = "N/A"
if meta_path.exists():
    with open(meta_path, "r") as f:
        meta = json.load(f)
        model_version = meta.get("version", "unknown")
        trained_until = meta.get("trained_until", "N/A")

# === Load data ===
df = pd.read_csv(gold_path)
df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")
df["snapshot_month"] = df["snapshot_date"].dt.to_period("M")

# Only include rows with labels
df = df.dropna(subset=["default_flag"])

# === Drop non-numeric or unsupported columns ===
drop_cols = ["customer_id", "snapshot_date", "month"]
X_all = df.drop(columns=["default_flag"] + drop_cols, errors="ignore")
y_all = df["default_flag"]

# === Monthly evaluation ===
monthly_results = []
for month, group in df.groupby("snapshot_month"):
    X = group.drop(columns=["default_flag", "customer_id", "snapshot_date", "month"], errors="ignore")
    y = group["default_flag"]

    # Drop object columns (e.g. encoded categories)
    X = X.select_dtypes(include=["number", "bool", "float", "int"])

    if len(y.unique()) < 2:  # Skip if no variation in labels
        continue

    y_pred = model.predict(X)
    f1 = f1_score(y, y_pred)
    acc = accuracy_score(y, y_pred)

    monthly_results.append({
        "snapshot_month": str(month),
        "f1": round(f1, 4),
        "accuracy": round(acc, 4)
    })

# === Save monthly scores ===
Path("/opt/airflow/monitoring_logs").mkdir(parents=True, exist_ok=True)

# Convert Timestamp-like objects to strings before saving
for record in monthly_results:
    record["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record["model_version"] = model_version

with open(log_file, "w") as f:
    json.dump(monthly_results, f, indent=2)

print(f"✅ Monthly F1/Accuracy tracked and logged to {log_file}")
print(f"🧾 Model: {model_version} (trained until {trained_until})")

# === Plot graphs ===
if monthly_results:
    df_plot = pd.DataFrame(monthly_results)

    # F1 over time
    plt.figure(figsize=(8, 4))
    plt.plot(df_plot["snapshot_month"], df_plot["f1"], marker="o", label="F1 Score")
    plt.title(f"Monthly F1 Score — Model {model_version}")
    plt.xlabel("Snapshot Month")
    plt.ylabel("F1 Score")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.ylim(0, 1)  # 👈 force y-axis to start at 0 and end at 1
    plt.savefig("/opt/airflow/monitoring_logs/monthly_f1_trend.png")
    plt.close()

    # Accuracy over time
    plt.figure(figsize=(8, 4))
    plt.plot(df_plot["snapshot_month"], df_plot["accuracy"], marker="s", label="Accuracy", color="orange")
    plt.title(f"Monthly Accuracy — Model {model_version}")
    plt.xlabel("Snapshot Month")
    plt.ylabel("Accuracy")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.ylim(0, 1)  # 👈 force y-axis to start at 0 and end at 1
    plt.savefig("/opt/airflow/monitoring_logs/monthly_accuracy_trend.png")
    plt.close()

    print("📈 Saved plots:")
    print("   • monthly_f1_trend.png")
    print("   • monthly_accuracy_trend.png")

else:
    print("⚠️ No valid labeled months found for evaluation.")
