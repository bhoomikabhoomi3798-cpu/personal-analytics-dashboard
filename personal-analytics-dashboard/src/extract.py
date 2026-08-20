"""
extract.py
Pulls a GitHub user's public activity data: repos, commit-ish events, and languages.
Uses the public GitHub REST API. A token is optional but recommended to avoid rate limits
(unauthenticated requests are limited to 60/hour; authenticated requests get 5,000/hour).

Usage:
    python src/extract.py --username <your-github-username>
"""

import argparse
import os
import json
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_API = "https://api.github.com"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def get_headers():
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def paginated_get(url, headers, params=None, max_pages=10):
    """Fetch all pages of a paginated GitHub API endpoint."""
    results = []
    params = dict(params or {})
    params["per_page"] = 100

    for page in range(1, max_pages + 1):
        params["page"] = page
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        results.extend(batch)
        if len(batch) < 100:
            break
        time.sleep(0.2)  # be polite to the API

    return results


def fetch_repos(username, headers):
    url = f"{GITHUB_API}/users/{username}/repos"
    return paginated_get(url, headers, params={"type": "owner", "sort": "updated"})


def fetch_events(username, headers):
    """Public events (commits, PRs, issues, stars) - last 90 days, capped by the API."""
    url = f"{GITHUB_API}/users/{username}/events/public"
    return paginated_get(url, headers, max_pages=3)


def fetch_languages(repos, headers):
    """For each repo, fetch the language breakdown (bytes of code per language)."""
    languages = {}
    for repo in repos:
        url = repo["languages_url"]
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            languages[repo["name"]] = resp.json()
        time.sleep(0.1)
    return languages


def save_json(data, filename):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data) if isinstance(data, list) else 'object'} -> {path}")


def main():
    parser = argparse.ArgumentParser(description="Extract GitHub activity data")
    parser.add_argument("--username", required=True, help="GitHub username to pull data for")
    args = parser.parse_args()

    headers = get_headers()

    print(f"Fetching repos for {args.username}...")
    repos = fetch_repos(args.username, headers)
    save_json(repos, "repos.json")

    print(f"Fetching public events for {args.username}...")
    events = fetch_events(args.username, headers)
    save_json(events, "events.json")

    print("Fetching language breakdown per repo...")
    languages = fetch_languages(repos, headers)
    save_json(languages, "languages.json")

    print("Done. Raw data saved to data/raw/")


if __name__ == "__main__":
    main()
