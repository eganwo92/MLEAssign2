import pandas as pd, matplotlib.pyplot as plt

def plot():
    df = pd.read_csv("datamart/gold/monitoring_metrics.csv")
    plt.figure(figsize=(8,5))
    plt.plot(df["timestamp"], df["accuracy"], marker='o')
    plt.title("Model Accuracy Over Time")
    plt.ylabel("Accuracy")
    plt.xlabel("Timestamp")
    plt.savefig("datamart/gold/accuracy_trend.png")
    print("✅ Visualization saved at datamart/gold/accuracy_trend.png")
