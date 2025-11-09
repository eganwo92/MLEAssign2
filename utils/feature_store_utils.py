import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

def update_feature_store():
    gold_path = "/opt/airflow/datamart/gold/feature_store.csv"
    df = pd.read_csv(gold_path)
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])

    # Simulate daily incoming data
    last_date = df["snapshot_date"].max()
    new_date = last_date + timedelta(days=1)

    new_rows = df.sample(5).copy()
    new_rows["snapshot_date"] = new_date

    df = pd.concat([df, new_rows], ignore_index=True)
    df.to_csv(gold_path, index=False)

    print(f"✅ Feature store updated with 5 new rows for {new_date.date()}")

if __name__ == "__main__":
    update_feature_store()
