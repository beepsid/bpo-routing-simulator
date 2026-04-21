import pandas as pd

df = pd.read_csv("data/bpo_call_center_data.csv")

df["Timestamp"] = pd.to_datetime(df["Timestamp"])

tech = df[df["Issue_Category"] == "Tech Support"].copy()

tech["week"] = tech["Timestamp"].dt.to_period("W").astype(str)

weekly = tech.groupby("week")["Resolution_Status"].value_counts(normalize=True).unstack().fillna(0)

print("\n Weekly Drop Rate (TECH SUPPORT)")
print(weekly[["Dropped"]].tail(10))

print("\n ANOMALY WINDOW CHECK")

anomaly_mask = (df["Timestamp"] >= "2026-02-26") & (df["Timestamp"] <= "2026-03-05")
anomaly_data = df[anomaly_mask & (df["Issue_Category"] == "Tech Support")]

print(anomaly_data["Resolution_Status"].value_counts(normalize=True))