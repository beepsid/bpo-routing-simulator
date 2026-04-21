import pandas as pd

df = pd.read_csv('data/bpo_call_center_data.csv')

df['Timestamp']=pd.to_datetime(df['Timestamp'])

tech_df = df[df['Issue_Category'] == 'Tech Support'].copy()

tech_df['week']= tech_df['Timestamp'].dt.to_period("W")

weekly_distribution = (
    tech_df
    .groupby("week")["Resolution_Status"]
    .value_counts(normalize=True)
    .unstack()
    .fillna(0)
)

drop_rate=weekly_distribution['Dropped']

drop_rate = drop_rate.sort_index()

print("\n Weekly Drop Rate (Tech Support):\n")
print(drop_rate)