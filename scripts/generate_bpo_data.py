import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

#faker configuration 

fake = Faker()
np.random.seed(42)
random.seed(42)

NUM_RECORDS = 50000
NUM_AGENTS = 100
DAYS_BACK = 90

START_DATE = datetime.now() - timedelta(days=DAYS_BACK)

ISSUE_CATEGORIES = ["Billing", "Tech Support", "Retention", "General"]
RESOLUTION_STATUS = ["Resolved", "Escalated", "Dropped"]

agents = [f"A{str(i).zfill(3)}" for i in range(1, NUM_AGENTS + 1)]

#base distributions

BASE_AHT = {
    "Billing": 180,
    "Tech Support": 420,
    "Retention": 600,
    "General": 140
}

CATEGORY_WEIGHTS = [0.30, 0.30, 0.20, 0.20]

#anomaly setup

anomaly_start = START_DATE + timedelta(days=40)
anomaly_end = anomaly_start + timedelta(days=7)

anomaly_agents = set(random.sample(agents, 8))

#data

rows = []

for i in range(NUM_RECORDS):

    timestamp = START_DATE + timedelta(
        minutes=random.randint(0, DAYS_BACK * 24 * 60)
    )

    category = random.choices(ISSUE_CATEGORIES, weights=CATEGORY_WEIGHTS)[0]
    agent = random.choice(agents)

    base = BASE_AHT[category]

    #anomaly logic

    in_anomaly_window = anomaly_start <= timestamp <= anomaly_end

    call_duration = np.random.normal(base, 60)

    if agent in anomaly_agents and category == "Tech Support":
        call_duration *= 1.8

    call_duration = max(30, int(call_duration))

    queue_wait = max(0, int(np.random.exponential(35)))

    if in_anomaly_window and category == "Tech Support":

        resolution = np.random.choice(
            RESOLUTION_STATUS,
            p=[0.55, 0.15, 0.30] 
        )
    else:
        resolution = np.random.choice(
            RESOLUTION_STATUS,
            p=[0.75, 0.20, 0.05]
        )

    rows.append([
        f"C{i+1:06d}",
        timestamp,
        agent,
        category,
        call_duration,
        queue_wait,
        resolution
    ])

# dataframe

df = pd.DataFrame(rows, columns=[
    "Call_ID",
    "Timestamp",
    "Agent_ID",
    "Issue_Category",
    "Call_Duration_Seconds",
    "Queue_Wait_Time",
    "Resolution_Status"
])

#cleaning

df["Call_Duration_Seconds"] = df["Call_Duration_Seconds"].astype(int)
df["Queue_Wait_Time"] = df["Queue_Wait_Time"].astype(int)

output_path = "data/bpo_call_center_data.csv"
df.to_csv(output_path, index=False)

print("\n Data generated")
print("----------------------------")
print(f"Rows generated: {len(df)}")
print(f"Date range: {df['Timestamp'].min()} → {df['Timestamp'].max()}")
print(f"Anomaly window: {anomaly_start} → {anomaly_end}")
print(f"Bad agents injected: {len(anomaly_agents)}")
print(f"Output file: {output_path}")

# anomaly validation
tech_drop_rate = df[
    df["Issue_Category"] == "Tech Support"
]["Resolution_Status"].value_counts(normalize=True)

print("\n Tech Support Resolution Distribution:")
print(tech_drop_rate)