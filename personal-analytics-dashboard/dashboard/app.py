"""
app.py
Streamlit dashboard visualizing personal GitHub activity data.
Run with: streamlit run dashboard/app.py
"""

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "analytics.db"

st.set_page_config(page_title="Personal Analytics Dashboard", layout="wide")


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    repos = pd.read_sql("SELECT * FROM repos", conn)
    events = pd.read_sql("SELECT * FROM events", conn)
    languages = pd.read_sql("SELECT * FROM languages", conn)
    conn.close()
    return repos, events, languages


st.title("📊 Personal Analytics Dashboard")
st.caption("GitHub activity, repo stats, and language usage — pulled from the GitHub API")

if not DB_PATH.exists():
    st.error(
        "No database found. Run the pipeline first:\n\n"
        "```\npython src/extract.py --username <your-username>\n"
        "python src/transform.py\npython src/load.py\n```"
    )
    st.stop()

repos, events, languages = load_data()

# --- Top-level KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Public Repos", len(repos))
col2.metric("Total Stars", int(repos["stargazers_count"].sum()) if "stargazers_count" in repos else 0)
col3.metric("Recent Events", len(events))
col4.metric("Languages Used", languages["language"].nunique() if not languages.empty else 0)

st.divider()

# --- Activity by day of week ---
st.subheader("Activity by Day of Week")
if not events.empty and "day_of_week" in events.columns:
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_counts = events["day_of_week"].value_counts().reindex(day_order).fillna(0)
    fig = px.bar(x=day_counts.index, y=day_counts.values,
                 labels={"x": "Day", "y": "Events"}, color=day_counts.values,
                 color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No event data yet — run the extract pipeline to populate this.")

# --- Activity by hour ---
st.subheader("Activity by Hour of Day")
if not events.empty and "hour" in events.columns:
    hour_counts = events["hour"].value_counts().sort_index()
    fig = px.line(x=hour_counts.index, y=hour_counts.values,
                   labels={"x": "Hour (UTC)", "y": "Events"}, markers=True)
    st.plotly_chart(fig, use_container_width=True)

# --- Language breakdown ---
st.subheader("Language Usage (by bytes of code)")
if not languages.empty:
    lang_totals = languages.groupby("language")["bytes"].sum().sort_values(ascending=False).head(10)
    fig = px.pie(values=lang_totals.values, names=lang_totals.index, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# --- Top repos ---
st.subheader("Top Repos by Stars")
if not repos.empty:
    top_repos = repos.sort_values("stargazers_count", ascending=False).head(10)
    st.dataframe(
        top_repos[["name", "stargazers_count", "forks_count", "language"]],
        use_container_width=True,
        hide_index=True,
    )

# --- Event type breakdown ---
st.subheader("Event Type Breakdown")
if not events.empty:
    type_counts = events["type"].value_counts()
    fig = px.bar(x=type_counts.values, y=type_counts.index, orientation="h",
                 labels={"x": "Count", "y": "Event Type"})
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Data source: GitHub REST API · Built with Streamlit + Plotly + SQLite")
