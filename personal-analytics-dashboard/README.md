# 📊 Personal Analytics Dashboard

An end-to-end data pipeline and interactive dashboard that analyzes personal GitHub
activity — commit patterns, language usage, and repo growth — to answer a simple
question: **when and how do I actually work?**

🔗 **Live demo:** _add your Streamlit Community Cloud link here after deploying_

![dashboard-screenshot](docs/screenshot.png)
_(add a screenshot or GIF of the running dashboard here)_

---

## Problem

Most developers have a vague sense of their own habits ("I code a lot on weekends,"
"I'm more productive at night") but no actual data to back it up. This project pulls
real activity data from the GitHub API and turns it into a queryable dataset and
dashboard to test those assumptions.

## Approach

1. **Extract** — Pull repos, public events, and language stats for a given GitHub
   username via the GitHub REST API (`src/extract.py`).
2. **Transform** — Clean and reshape raw JSON into tidy, typed tables: parsed
   timestamps, day-of-week/hour features, normalized language byte counts
   (`src/transform.py`).
3. **Load** — Write the cleaned data into a local SQLite database for SQL-based
   analysis (`src/load.py`).
4. **Analyze** — Run SQL queries covering activity trends, rolling averages, and
   language distribution (`sql/queries.sql`).
5. **Visualize** — Serve the results through an interactive Streamlit dashboard
   (`dashboard/app.py`).

## Findings (example — replace with your own after running the pipeline)

- Activity peaks on **Tuesdays and Wednesdays**, with a sharp drop-off on weekends —
  contrary to the "weekend warrior" assumption.
- **Python and TypeScript** account for over 60% of total bytes written across repos.
- A 7-day rolling average of events shows activity is bursty, not steady — long
  gaps followed by high-output days, consistent with project-based (not daily-habit)
  coding patterns.

## Tech Stack

| Layer         | Tool                          |
|---------------|--------------------------------|
| Extraction    | Python, `requests`, GitHub REST API |
| Transformation| `pandas`                       |
| Storage       | SQLite                          |
| Analysis      | SQL (window functions, joins, aggregations) |
| Dashboard     | Streamlit + Plotly              |

## Project Structure

```
personal-analytics-dashboard/
├── data/
│   ├── raw/                # raw JSON pulled from the API
│   └── processed/          # cleaned CSVs
├── src/
│   ├── extract.py          # pulls data from GitHub API
│   ├── transform.py        # cleans + reshapes into tidy CSVs
│   └── load.py              # loads CSVs into SQLite
├── sql/
│   └── queries.sql           # analysis queries (trends, joins, window functions)
├── dashboard/
│   └── app.py                 # Streamlit dashboard
├── requirements.txt
└── .env.example
```

## Running It Locally

```bash
# 1. Clone and install dependencies
git clone https://github.com/<your-username>/personal-analytics-dashboard.git
cd personal-analytics-dashboard
pip install -r requirements.txt

# 2. (Optional) Add a GitHub token to raise API rate limits
cp .env.example .env
# edit .env and add GITHUB_TOKEN=your_token_here

# 3. Run the pipeline
python src/extract.py --username <your-github-username>
python src/transform.py
python src/load.py

# 4. Launch the dashboard
streamlit run dashboard/app.py
```

## Possible Extensions

- Swap the data source for Spotify, Strava, or bank export data — the
  extract/transform/load pattern stays the same.
- Add anomaly detection (e.g., flag weeks with unusually high/low activity).
- Schedule the pipeline to run daily (cron / GitHub Actions) and append to a
  growing historical table instead of overwriting.
- Deploy the SQLite file to a hosted Postgres instance for a "real" production setup.

## Why This Project

This was built to demonstrate a full analyst workflow — not just a chart, but the
whole path from raw API data to a cleaned dataset, SQL analysis, and a
decision-ready dashboard.
