import pandas as pd
from pathlib import Path

def temporal_split(df: pd.DataFrame):
    """Split dataset into train, validation, OOT, and inference."""
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    df["month"] = df["snapshot_date"].dt.to_period("M")

    train_period = (df["month"] >= "2023-01") & (df["month"] <= "2023-12")
    val_period = (df["month"] >= "2024-01") & (df["month"] <= "2024-03")
    oot_period = (df["month"] >= "2024-04") & (df["month"] <= "2024-06")
    inference_period = (df["month"] > "2024-06")

    splits = {
        "train": df.loc[train_period].copy(),
        "val": df.loc[val_period].copy(),
        "oot": df.loc[oot_period].copy(),
        "inference": df.loc[inference_period].copy(),
    }

    Path("datamart/splits").mkdir(parents=True, exist_ok=True)
    for name, subset in splits.items():
        subset.to_csv(f"datamart/splits/{name}.csv", index=False)
        print(f"✅ {name.capitalize()} split: {subset.shape}")
    return splits
