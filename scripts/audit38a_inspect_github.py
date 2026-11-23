import sqlite3

w_db = 'data/working/rolling_ai_ecosystem.db'
conn = sqlite3.connect(w_db)
c = conn.cursor()

# Repos with snapshots
c.execute("""
SELECT 
    gr.repo_id,
    gr.html_url,
    gr.last_checked_at,
    gr.latest_stars,
    gr.latest_forks,
    COUNT(gmh.snapshot_id) as snapshot_count,
    MAX(gmh.snapshot_timestamp) as latest_snapshot_at
FROM github_repositories gr
LEFT JOIN github_metrics_history gmh ON gr.repo_id = gmh.repo_id
GROUP BY gr.repo_id
""")
rows = c.fetchall()
with_snap = [r for r in rows if r[5] > 0]
without_snap = [r for r in rows if r[5] == 0]
print(f"Total repos: {len(rows)}")
print(f"Repos with at least one snapshot: {len(with_snap)}")
print(f"Repos with zero snapshots: {len(without_snap)}")

print("\nSnapshot timestamps distribution in github_metrics_history:")
c.execute("SELECT substr(snapshot_timestamp, 1, 10) as dt, count(*) FROM github_metrics_history GROUP BY dt ORDER BY dt")
for r in c.fetchall():
    print(" ", r)

print("\nlast_checked_at distribution in github_repositories:")
c.execute("SELECT substr(last_checked_at, 1, 10) as dt, count(*) FROM github_repositories GROUP BY dt ORDER BY dt")
for r in c.fetchall():
    print(" ", r)

# Distribution of snapshot counts per repo
c.execute("""
SELECT snap_cnt, count(*) FROM (
    SELECT repo_id, count(*) as snap_cnt FROM github_metrics_history GROUP BY repo_id
) GROUP BY snap_cnt
""")
print("\nSnapshots per repo distribution:")
for r in c.fetchall():
    print(" ", r)

conn.close()
