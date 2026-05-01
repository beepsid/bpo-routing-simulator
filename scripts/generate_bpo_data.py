import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# faker configuration
fake = Faker()
np.random.seed(42)
random.seed(42)

NUM_RECORDS = 50000
NUM_AGENTS = 100
DAYS_BACK = 90

START_DATE = datetime.now() - timedelta(days=DAYS_BACK)

ISSUE_CATEGORIES = ["Billing", "Tech Support", "Retention", "General", "Sales"]
RESOLUTION_STATUS = ["Resolved", "Escalated", "Dropped"]

agents = [f"A{str(i).zfill(3)}" for i in range(1, NUM_AGENTS + 1)]

# agent metadata
DEPARTMENTS = ["Billing", "Tech Support", "Retention", "General", "Sales"]
SENIORITY_LEVELS = ["Junior", "Mid", "Senior"]

agent_records = []
for agent in agents:
    dept = random.choice(DEPARTMENTS)
    seniority = random.choices(SENIORITY_LEVELS, weights=[0.4, 0.4, 0.2])[0]
    hire_date = fake.date_between(start_date="-5y", end_date="-3m")
    agent_records.append({
        "agent_id": agent,
        "agent_name": fake.name(),
        "department": dept,
        "seniority": seniority,
        "hire_date": hire_date
    })

agents_df = pd.DataFrame(agent_records)

# category metadata with SLA targets
category_records = [
    {"category_id": "CAT001", "category_name": "Billing",      "sla_target_seconds": 240, "target_fcr_rate": 0.80},
    {"category_id": "CAT002", "category_name": "Tech Support",  "sla_target_seconds": 480, "target_fcr_rate": 0.70},
    {"category_id": "CAT003", "category_name": "Retention",     "sla_target_seconds": 720, "target_fcr_rate": 0.65},
    {"category_id": "CAT004", "category_name": "General",       "sla_target_seconds": 180, "target_fcr_rate": 0.85},
    {"category_id": "CAT005", "category_name": "Sales",         "sla_target_seconds": 300, "target_fcr_rate": 0.75},
]
categories_df = pd.DataFrame(category_records)

# base AHT per category
BASE_AHT = {
    "Billing":      180,
    "Tech Support": 420,
    "Retention":    600,
    "General":      140,
    "Sales":        300
}

CATEGORY_WEIGHTS = [0.25, 0.25, 0.15, 0.15, 0.20]

# anomaly setup — +40% drop rate spike in Tech Support
anomaly_start = START_DATE + timedelta(days=40)
anomaly_end   = anomaly_start + timedelta(days=7)
anomaly_agents = set(random.sample(agents, 8))

# data generation
rows = []

for i in range(NUM_RECORDS):

    timestamp = START_DATE + timedelta(
        minutes=random.randint(0, DAYS_BACK * 24 * 60)
    )

    category = random.choices(ISSUE_CATEGORIES, weights=CATEGORY_WEIGHTS)[0]
    agent    = random.choice(agents)
    base     = BASE_AHT[category]

    in_anomaly_window = anomaly_start <= timestamp <= anomaly_end

    call_duration = np.random.normal(base, 60)

    if agent in anomaly_agents and category == "Tech Support":
        call_duration *= 1.8

    call_duration = max(30, int(call_duration))
    queue_wait    = max(0, int(np.random.exponential(35)))

    # anomaly: Tech Support drop rate goes from ~5% baseline to ~45% (+40 percentage points)
    if in_anomaly_window and category == "Tech Support":
        resolution = np.random.choice(RESOLUTION_STATUS, p=[0.45, 0.10, 0.45])
    else:
        resolution = np.random.choice(RESOLUTION_STATUS, p=[0.75, 0.20, 0.05])

    # FCR: Resolved on first contact (not Escalated or Dropped, and duration reasonable)
    fcr = 1 if resolution == "Resolved" and call_duration <= base * 1.5 else 0

    rows.append([
        f"C{i+1:06d}",
        timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        agent,
        category,
        call_duration,
        queue_wait,
        resolution,
        fcr
    ])

# build main dataframe
df = pd.DataFrame(rows, columns=[
    "Call_ID",
    "Timestamp",
    "Agent_ID",
    "Issue_Category",
    "Call_Duration_Seconds",
    "Queue_Wait_Time",
    "Resolution_Status",
    "FCR"
])

df["Call_Duration_Seconds"] = df["Call_Duration_Seconds"].astype(int)
df["Queue_Wait_Time"]       = df["Queue_Wait_Time"].astype(int)
df["FCR"]                   = df["FCR"].astype(int)

# save all outputs
df.to_csv("data/bpo_call_center_data.csv", index=False)
agents_df.to_csv("data/agents.csv", index=False)
categories_df.to_csv("data/categories.csv", index=False)

# summary
print("\nData generated")
print("----------------------------")
print(f"Rows generated:      {len(df)}")
print(f"Date range:          {df['Timestamp'].min()} -> {df['Timestamp'].max()}")
print(f"Anomaly window:      {anomaly_start.strftime('%Y-%m-%d')} -> {anomaly_end.strftime('%Y-%m-%d')}")
print(f"Anomaly agents:      {len(anomaly_agents)}")
print(f"Categories:          {df['Issue_Category'].unique().tolist()}")
print(f"Agents CSV:          data/agents.csv ({len(agents_df)} rows)")
print(f"Categories CSV:      data/categories.csv ({len(categories_df)} rows)")

print("\nTech Support Resolution Distribution (anomaly window):")
mask = (
    (pd.to_datetime(df["Timestamp"]) >= anomaly_start) &
    (pd.to_datetime(df["Timestamp"]) <= anomaly_end) &
    (df["Issue_Category"] == "Tech Support")
)
print(df[mask]["Resolution_Status"].value_counts(normalize=True).round(3))

print("\nOverall FCR Rate:", round(df["FCR"].mean() * 100, 2), "%")
