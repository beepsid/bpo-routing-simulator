# BPO Call Center Analytics

A data analytics project simulating a Business Process Outsourcing (BPO) call center environment. It covers synthetic data generation, MySQL storage, SQL-based KPI analysis, statistical anomaly detection, and a Power BI dashboard.

---

## Project Structure

```
bpo-routing-simulator/
├── data/
│   └── bpo_call_center_data.csv
├── scripts/
│   ├── generate_bpo_data.py
│   ├── load_to_mysql.py
│   ├── anomaly_detection.py
│   ├── anomaly_exploration.py
│   └── validate_anomaly.py
├── sql/
│   ├── create_tables.sql
│   ├── kpi_queries.sql
│   └── anomary_detection.sql
├── dashboard/
│   └── BPO Call Center Performance Dashboard.pbix
├── images/
│   └── call_center_log.png
├── .env
└── index.html
```

---

## Data

### `data/bpo_call_center_data.csv`

The main dataset used across all scripts and the dashboard. Contains 50,000 synthetic records with the following columns:

| Column | Description |
|---|---|
| `Call_ID` | Unique call identifier (e.g. C000001) |
| `Timestamp` | Date and time of the call |
| `Agent_ID` | Agent who handled the call (A001–A100) |
| `Issue_Category` | Category of the call: Billing, Tech Support, Retention, General |
| `Call_Duration_Seconds` | Total call handling time in seconds |
| `Queue_Wait_Time` | Time the caller waited in queue before being answered |
| `Resolution_Status` | Outcome of the call: Resolved, Escalated, or Dropped |

---

## Scripts

### `scripts/generate_bpo_data.py`

Generates the synthetic dataset and saves it to `data/bpo_call_center_data.csv`.

- Creates 50,000 records spanning 90 days from the current date
- Simulates 100 agents (A001–A100) across 4 issue categories
- Each category has a realistic base Average Handling Time (AHT): Billing 180s, Tech Support 420s, Retention 600s, General 140s
- Injects a deliberate anomaly: a 7-day window where Tech Support drop rates spike to 30% (vs the normal 5%) and 8 randomly selected agents have their call durations inflated by 1.8x
- Uses fixed random seeds (42) so results are reproducible

### `scripts/load_to_mysql.py`

Loads the CSV into a MySQL database.

- Reads credentials from the `.env` file using `python-dotenv`
- Connects to a local MySQL instance via SQLAlchemy and PyMySQL
- Renames CSV columns to match the database schema
- Loads data into the `call_center_logs` table using `if_exists='replace'`, which drops and recreates the table on each run

### `scripts/anomaly_detection.py`

Core anomaly detection script using z-score analysis.

- Filters records to Tech Support calls only
- Groups calls by week and calculates the weekly drop rate (proportion of Dropped calls)
- Computes the mean and standard deviation of the drop rate across all weeks
- Assigns a z-score to each week; weeks with an absolute z-score above 2 are flagged as anomalies
- Prints the full weekly table and a separate output showing only the flagged anomaly weeks

### `scripts/anomaly_exploration.py`

Exploratory script used during development to inspect the weekly drop rate trend before building the full detection logic.

- Filters to Tech Support calls
- Groups by week and prints the weekly drop rate in chronological order
- No anomaly flagging — used for visual inspection of the data

### `scripts/validate_anomaly.py`

Validation script to confirm the injected anomaly is present in the data.

- Prints the weekly drop rate for the last 10 weeks of Tech Support data
- Directly queries the known anomaly window (the 7-day injection period) and prints the resolution distribution for that period
- Used to verify that `generate_bpo_data.py` injected the anomaly correctly

---

## SQL

### `sql/create_tables.sql`

Creates the MySQL database and table schema.

- Creates the `bpo_project` database
- Creates the `call_center_logs` table with `call_id` as the primary key
- Column types match what `load_to_mysql.py` writes

### `sql/kpi_queries.sql`

A collection of operational KPI queries for the call center data.

- Total call volume
- Overall and per-category Average Handling Time (AHT)
- Overall and per-category drop rate percentage
- Percentage of calls with queue wait time over 60 seconds
- Average queue wait time
- Resolution status distribution as percentages
- Top 5 agents by call volume
- Drop rate ranked by agent (to identify underperforming agents)

### `sql/anomary_detection.sql`

SQL-based anomaly analysis queries that complement the Python detection script.

- Weekly drop rate across all categories
- Weekly drop rate filtered to Tech Support only
- Rolling 3-week average drop rate for Tech Support using a window function — useful for smoothing noise and spotting sustained trends

---

## Dashboard

### `dashboard/BPO Call Center Performance Dashboard.pbix`

A Power BI dashboard built on top of the MySQL database and CSV data. It visualizes the key metrics from the SQL KPI queries and surfaces the anomaly detected in the Python scripts.

The dashboard covers:

- **Call Volume** — total calls over time and by category
- **Average Handling Time** — AHT breakdown by issue category to identify which call types take the longest
- **Drop Rate** — overall drop rate and weekly trend, with the anomaly week visible as a spike
- **Queue Wait Time** — distribution of wait times and the percentage of calls exceeding 60 seconds
- **Resolution Distribution** — proportion of Resolved, Escalated, and Dropped calls
- **Agent Performance** — top agents by volume and drop rate by agent to identify outliers

---

## Setup

### Requirements

```
pandas
numpy
faker
sqlalchemy
pymysql
python-dotenv
```

Install with:

```bash
pip install pandas numpy faker sqlalchemy pymysql python-dotenv
```

### Environment Variables

Create a `.env` file in the project root:

```
DB_PASSWORD=your_mysql_password
```

### Running the Project

```bash
# 1. Generate the dataset
python scripts/generate_bpo_data.py

# 2. Create the MySQL table
# Run sql/create_tables.sql in your MySQL client

# 3. Load data into MySQL
python scripts/load_to_mysql.py

# 4. Run anomaly detection
python scripts/anomaly_detection.py
```

---

## Notes

- Do not open `bpo_call_center_data.csv` in Excel while running any script. Excel locks the file and truncates datetime values, which corrupts the timestamps and breaks the anomaly detection.
- The `.env` file is excluded from version control. Never commit credentials.
- The anomaly window shifts each time `generate_bpo_data.py` is run because it is calculated relative to the current date.
