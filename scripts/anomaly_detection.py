import pandas as pd

# load data
df = pd.read_csv("data/bpo_call_center_data.csv")

# fix timestamp
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# filter tech support
tech = df[df["Issue_Category"] == "Tech Support"]

# create weekly groups
tech["week"] = tech["Timestamp"].dt.to_period("W")

# calculate drop rate per week
weekly = tech.groupby("week")["Resolution_Status"].value_counts(normalize=True).unstack().fillna(0)

weekly["drop_rate"] = weekly["Dropped"]

# z-score
mean = weekly["drop_rate"].mean()
std = weekly["drop_rate"].std()

weekly["z_score"] = (weekly["drop_rate"] - mean) / std

# anomaly flag
weekly["anomaly"] = weekly["z_score"].abs() > 2

print(weekly[["drop_rate", "z_score", "anomaly"]])

#detected anomaly
print("\n Detected Anomalies:\n") 
print(weekly[weekly["anomaly"] == True])