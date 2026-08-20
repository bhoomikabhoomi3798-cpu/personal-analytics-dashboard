"""
transform.py
Cleans and reshapes raw GitHub JSON (data/raw/) into tidy CSVs (data/processed/)
ready for SQL loading and dashboarding.
"""

import json
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def load_raw(filename):
    path = RAW_DIR / filename
    with open(path) as f:
        return json.load(f)


def transform_repos(repos):
    df = pd.DataFrame(repos)
    keep = [
        "name", "full_name", "stargazers_count", "forks_count",
        "open_issues_count", "language", "created_at", "updated_at",
        "pushed_at", "size", "archived", "fork",
    ]
    df = df[[c for c in keep if c in df.columns]].copy()
    for col in ["created_at", "updated_at", "pushed_at"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def transform_events(events):
    if not events:
        return pd.DataFrame(columns=["type", "repo_name", "created_at", "commit_count"])

    rows = []
    for e in events:
        commit_count = 0
        if e.get("type") == "PushEvent":
            commit_count = len(e.get("payload", {}).get("commits", []))
        rows.append({
            "type": e.get("type"),
            "repo_name": e.get("repo", {}).get("name"),
            "created_at": e.get("created_at"),
            "commit_count": commit_count,
        })

    df = pd.DataFrame(rows)
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["day_of_week"] = df["created_at"].dt.day_name()
    df["hour"] = df["created_at"].dt.hour
    df["date"] = df["created_at"].dt.date
    return df


def transform_languages(languages_dict):
    rows = []
    for repo_name, langs in languages_dict.items():
        for lang, byte_count in langs.items():
            rows.append({"repo_name": repo_name, "language": lang, "bytes": byte_count})
    return pd.DataFrame(rows)


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    repos_df = transform_repos(load_raw("repos.json"))
    repos_df.to_csv(PROCESSED_DIR / "repos.csv", index=False)
    print(f"repos.csv -> {len(repos_df)} rows")

    events_df = transform_events(load_raw("events.json"))
    events_df.to_csv(PROCESSED_DIR / "events.csv", index=False)
    print(f"events.csv -> {len(events_df)} rows")

    languages_df = transform_languages(load_raw("languages.json"))
    languages_df.to_csv(PROCESSED_DIR / "languages.csv", index=False)
    print(f"languages.csv -> {len(languages_df)} rows")

    print("Transform complete. Processed CSVs in data/processed/")


if __name__ == "__main__":
    main()
