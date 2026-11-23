import sqlite3
import json
from collections import Counter

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT count(*) FROM ai_research_papers")
total_papers = c.fetchone()[0]
print(f"Total papers: {total_papers}")

c.execute("SELECT freshness_status, count(*) FROM ai_research_papers GROUP BY freshness_status")
print("Freshness status breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT publication_date, count(*) FROM ai_research_papers GROUP BY publication_date ORDER BY publication_date DESC")
pub_dates = c.fetchall()
print(f"Unique publication dates: {len(pub_dates)}")
print("Sample publication dates (first 25):")
for r in pub_dates[:25]:
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT provenance, count(*) FROM ai_research_papers GROUP BY provenance")
print("Provenance breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

# Inspect paper IDs format
c.execute("SELECT paper_id, publication_date, title, paper_url, collected_at, first_seen_at FROM ai_research_papers LIMIT 15")
print("Sample paper rows:")
for r in c.fetchall():
    print(dict(r))

# Check arXiv ID prefixes
c.execute("SELECT paper_id FROM ai_research_papers")
paper_ids = [r[0] for r in c.fetchall()]
prefix_counter = Counter()
for pid in paper_ids:
    # normalize arxiv:2611.12345 or 2611.12345
    clean = pid.replace("arxiv:", "").replace("arXiv:", "")
    parts = clean.split(".")
    if len(parts) >= 2:
        prefix = parts[0]
        prefix_counter[prefix] += 1
    else:
        prefix_counter["other"] += 1

print("arXiv ID YYMM prefix breakdown:")
for pref, cnt in prefix_counter.most_common():
    print(f"  Prefix {pref}: {cnt}")

# Check for title duplicates
c.execute("SELECT title, count(*) FROM ai_research_papers GROUP BY lower(trim(title)) HAVING count(*) > 1")
dup_titles = c.fetchall()
print(f"Duplicate titles count: {len(dup_titles)}")
for r in dup_titles[:10]:
    print(f"  '{r[0]}': {r[1]}")

# Check for paper_id duplicates
c.execute("SELECT paper_id, count(*) FROM ai_research_papers GROUP BY paper_id HAVING count(*) > 1")
dup_ids = c.fetchall()
print(f"Duplicate paper_ids count: {len(dup_ids)}")

conn.close()
