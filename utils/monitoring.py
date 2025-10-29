import pandas as pd
import os
from datetime import datetime

def log_metrics(metrics: dict):
    os.makedirs("datamart/metrics", exist_ok=True)
    path = "datamart/metrics/model_metrics.csv"
    metrics["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([metrics])
    if os.path.exists(path):
        old = pd.read_csv(path)
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(path, index=False)
