-- Analysis queries against data/analytics.db
-- Run with: sqlite3 data/analytics.db < sql/queries.sql
-- or paste individually into any SQLite client / the dashboard.

-- 1. Activity by day of week (which days are most active)
SELECT
    day_of_week,
    COUNT(*) AS event_count,
    SUM(commit_count) AS total_commits
FROM events
GROUP BY day_of_week
ORDER BY event_count DESC;

-- 2. Activity by hour of day (when do you code most)
SELECT
    hour,
    COUNT(*) AS event_count
FROM events
GROUP BY hour
ORDER BY hour;

-- 3. Top repos by star count
SELECT
    name,
    stargazers_count,
    forks_count,
    language
FROM repos
WHERE fork = 0
ORDER BY stargazers_count DESC
LIMIT 10;

-- 4. Language usage across all repos, ranked by total bytes written
SELECT
    language,
    SUM(bytes) AS total_bytes,
    COUNT(DISTINCT repo_name) AS repo_count
FROM languages
GROUP BY language
ORDER BY total_bytes DESC;

-- 5. Rolling activity trend: events per day (window function)
SELECT
    date,
    COUNT(*) AS daily_events,
    AVG(COUNT(*)) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7day_avg
FROM events
GROUP BY date
ORDER BY date;

-- 6. Event type breakdown (pushes vs PRs vs issues vs stars, etc.)
SELECT
    type,
    COUNT(*) AS occurrences,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM events), 1) AS pct_of_total
FROM events
GROUP BY type
ORDER BY occurrences DESC;

-- 7. Most active repos (by event count, joined with repo metadata)
SELECT
    e.repo_name,
    COUNT(*) AS event_count,
    r.stargazers_count,
    r.language
FROM events e
LEFT JOIN repos r ON r.full_name = e.repo_name
GROUP BY e.repo_name
ORDER BY event_count DESC
LIMIT 10;
