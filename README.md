# BPO Call Center Analytics

A data analytics project simulating a Business Process Outsourcing (BPO) call center environment. It covers synthetic data generation, a normalized MySQL schema, SQL-based KPI analysis, statistical anomaly detection, and a Power BI dashboard.

---

## Project Structure

```
bpo-routing-simulator/
├── data/
│   ├── bpo_call_center_data.csv
│   ├── agents.csv
│   └── categories.csv
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

The main call log dataset consist of 50,000 synthetic records spanning 90 days.

| Column | Description |
|---|---|
| `Call_ID` | Unique call identifier (C000001–C050000) |
| `Timestamp` | Date and time of the call |
| `Agent_ID` | Agent who handled the call (A001–A100) |
| `Issue_Category` | Billing, Tech Support, Retention, General, or Sales |
| `Call_Duration_Seconds` | Total call handling time in seconds |
| `Queue_Wait_Time` | Time the caller waited before being answered |
| `Resolution_Status` | Resolved, Escalated, or Dropped |
| `FCR` | First Call Resolution flag, 1 if resolved without escalation, 0 otherwise |

### `data/agents.csv`

Reference table for the 100 simulated agents.

| Column | Description |
|---|---|
| `agent_id` | Agent identifier (A001–A100) |
| `agent_name` | Randomly generated full name |
| `department` | Assigned department |
| `seniority` | Junior, Mid, or Senior |
| `hire_date` | Simulated hire date |

### `data/categories.csv`

Reference table for the 5 issue categories with SLA and FCR targets.

| Column | Description |
|---|---|
| `category_id` | Category identifier (CAT001–CAT005) |
| `category_name` | Category label |
| `sla_target_seconds` | Maximum acceptable call duration for SLA compliance |
| `target_fcr_rate` | Target first call resolution rate for the category |

---

## Scripts

### `scripts/generate_bpo_data.py`

Generates all three datasets and saves them to the `data/` folder.

- Creates 50,000 call records across 5 categories with realistic base AHT per category: Billing 180s, Tech Support 420s, Retention 600s, General 140s, Sales 300s
- Generates 100 agents with randomized names, departments, seniority levels, and hire dates
- Injects a deliberate anomaly: a 7-day window where Tech Support drop rate spikes from ~5% to ~45% (+40 percentage points), and 8 randomly selected agents have their call durations inflated by 1.8x
- Adds an `FCR` column, 1 if the call was resolved within 1.5x the category baseline, 0 otherwise
- Uses fixed random seeds (42) for reproducibility
- Outputs: `bpo_call_center_data.csv`, `agents.csv`, `categories.csv`

### `scripts/load_to_mysql.py`

Loads all three CSVs into MySQL in dependency order.

- Reads credentials from `.env` using `python-dotenv`
- Loads `categories` first, then `agents`, then `call_center_logs` to respect foreign key constraints
- Uses `if_exists='replace'` so re-runs are clean
- Temporarily disables foreign key checks during the main table load to avoid constraint errors on replace

### `scripts/anomaly_detection.py`

Core anomaly detection using z-score analysis on weekly drop rates.

- Filters to Tech Support calls and groups by week
- Calculates weekly drop rate, mean, and standard deviation across all weeks
- Flags any week with an absolute z-score above 2 as an anomaly
- Prints the full weekly table and a separate block showing only flagged weeks

### `scripts/anomaly_exploration.py`

Exploratory script for inspecting the weekly drop rate trend before building detection logic.

- Filters to Tech Support, groups by week, and prints drop rates in chronological order
- No anomaly flagging, used for visual inspection

### `scripts/validate_anomaly.py`

Confirms the injected anomaly is present in the generated data.

- Prints the last 10 weeks of Tech Support drop rates
- Directly queries the known anomaly window and prints the resolution distribution for that period

---

## SQL

### `sql/create_tables.sql`

Creates the normalized MySQL schema with 3 tables.

- `categories`: reference table with SLA targets and FCR targets per category
- `agents`: reference table with agent metadata
- `call_center_logs`: main fact table with foreign keys to both reference tables

### `sql/kpi_queries.sql`

17 KPI queries covering the full range of call center metrics. Uses JOINs, window functions, and subqueries throughout.

| # | Query | Technique |
|---|---|---|
| 1 | Total call volume | Aggregate |
| 2 | Overall AHT | Aggregate |
| 3 | AHT by category with SLA status | JOIN + CASE |
| 4 | SLA adherence rate by department | JOIN + conditional aggregate |
| 5 | Overall FCR rate | Aggregate |
| 6 | FCR rate by category vs target | JOIN + comparison |
| 7 | Overall drop rate | Conditional aggregate |
| 8 | Drop rate by category | GROUP BY |
| 9 | Resolution status distribution % | Window function (SUM OVER) |
| 10 | Agent utilization: calls and talk hours | JOIN |
| 11 | Top 10 agents by call volume | JOIN + ORDER BY |
| 12 | Agent FCR ranking | Subquery + RANK window function |
| 13 | Agent drop rate ranking with seniority | Subquery + JOIN + RANK |
| 14 | Queue wait time analysis | Aggregate + conditional |
| 15 | Queue wait time by category | JOIN + conditional aggregate |
| 16 | Monthly call volume with running total | Subquery + SUM OVER |
| 17 | Agent AHT vs department average | Subquery + JOIN |

### `sql/anomary_detection.sql`

SQL-based anomaly analysis to complement the Python detection script.

- Weekly drop rate across all categories
- Weekly drop rate filtered to Tech Support only
- Rolling 3-week average drop rate for Tech Support using a window function, smooths noise and surfaces sustained trends

---

## Dashboard

### `dashboard/BPO Call Center Performance Dashboard.pbix`

A Power BI dashboard built on the MySQL database and CSV data. Visualizes the KPIs from the SQL queries and surfaces the injected anomaly.

Panels covered:

- **Call Volume**: total calls over time and by category
- **Average Handling Time**: AHT by category with SLA target comparison
- **Drop Rate Trend**: weekly drop rate with the anomaly week visible as a spike
- **FCR Rate**: actual vs target FCR by department
- **Queue Wait Time**: distribution and percentage of calls exceeding 60 seconds
- **Agent Performance**: utilization, FCR ranking, and drop rate by agent

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
# 1. Generate all datasets
python scripts/generate_bpo_data.py

# 2. Create the MySQL schema
# Run sql/create_tables.sql in your MySQL client

# 3. Load all tables into MySQL
python scripts/load_to_mysql.py

# 4. Run anomaly detection
python scripts/anomaly_detection.py
```

---

## Notes

- Do not open any CSV in Excel while running scripts. Excel locks files and truncates datetime values, which corrupts timestamps and breaks anomaly detection.
- The `.env` file is excluded from version control. Never commit credentials.
- The anomaly window shifts on each run of `generate_bpo_data.py` because it is calculated relative to the current date.
