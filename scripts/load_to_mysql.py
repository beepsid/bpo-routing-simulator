import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os

load_dotenv()

url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=os.getenv("DB_PASSWORD"),
    host="localhost",
    database="bpo_project"
)

engine = create_engine(url)

# 1. categories 
categories_df = pd.read_csv("data/categories.csv")
categories_df.to_sql("categories", con=engine, if_exists="replace", index=False)
print(f"Loaded categories: {len(categories_df)} rows")

#  2. agents
agents_df = pd.read_csv("data/agents.csv")
agents_df.to_sql("agents", con=engine, if_exists="replace", index=False)
print(f"Loaded agents:     {len(agents_df)} rows")

# 3. call_center_logs 
df = pd.read_csv("data/bpo_call_center_data.csv")

df = df.rename(columns={
    "Call_ID":                "call_id",
    "Timestamp":              "call_timestamp",
    "Agent_ID":               "agent_id",
    "Issue_Category":         "issue_category",
    "Call_Duration_Seconds":  "call_duration_seconds",
    "Queue_Wait_Time":        "queue_wait_time",
    "Resolution_Status":      "resolution_status",
    "FCR":                    "fcr"
})

# disable FK checks so replace works cleanly, then re-enable
with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    conn.commit()

df.to_sql("call_center_logs", con=engine, if_exists="replace", index=False)

with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    conn.commit()

print(f"Loaded call_logs:  {len(df)} rows")
print("\nAll tables loaded successfully.")
