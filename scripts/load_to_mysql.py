import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

df = pd.read_csv("data/bpo_call_center_data.csv")

url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="tomioka@141025", 
    host="localhost",
    database="bpo_project"
)

engine = create_engine(url)

df = df.rename(columns={
    'Call_ID': 'call_id',
    'Timestamp': 'call_timestamp',
    'Agent_ID': 'agent_id',
    'Issue_Category': 'issue_category',
    'Call_Duration_Seconds': 'call_duration_seconds',
    'Queue_Wait_Time': 'queue_wait_time',
    'Resolution_Status': 'resolution_status'
})


df.to_sql(
    name='call_center_logs',
    con=engine,
    if_exists='append',
    index=False
)

print('Loaded!')

