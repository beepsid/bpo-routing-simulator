import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os

load_dotenv()

password = os.getenv("db_password")

df = pd.read_csv("data/bpo_call_center_data.csv")

url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=os.getenv('db_password'), 
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
    if_exists='replace',
    index=False
)

print('Loaded!')