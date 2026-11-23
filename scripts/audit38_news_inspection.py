import sqlite3
from collections import Counter

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT count(*) FROM ai_news")
total_news = c.fetchone()[0]
print(f"Total news: {total_news}")

c.execute("SELECT freshness_status, count(*) FROM ai_news GROUP BY freshness_status")
print("Freshness status breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT source_name, count(*) FROM ai_news GROUP BY source_name ORDER BY count(*) DESC")
sources = c.fetchall()
print("Source name breakdown:")
for r in sources:
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT source_name, freshness_status, count(*) FROM ai_news GROUP BY source_name, freshness_status ORDER BY source_name, freshness_status")
print("\nPer-source freshness breakdown:")
for r in c.fetchall():
    print(f"  {r[0]} | {r[1]}: {r[2]}")

# Check publication dates range per source
print("\nPer-source date ranges:")
for src in [r[0] for r in sources]:
    c.execute("SELECT min(published_at), max(published_at), count(*) FROM ai_news WHERE source_name = ?", (src,))
    min_d, max_d, cnt = c.fetchone()
    print(f"  {src} ({cnt} arts): min={min_d}, max={max_d}")

# Check content length and quality
c.execute("SELECT length(content), length(summary), title, source_name, published_at FROM ai_news LIMIT 10")
print("\nSample content inspection:")
for r in c.fetchall():
    print(f"  [{r[3]}] len(content)={r[0]}, len(summary)={r[1]}, pub={r[4]} | title={r[2][:60]}")

# Check for empty content
c.execute("SELECT count(*) FROM ai_news WHERE content IS NULL OR content = ''")
empty_content = c.fetchone()[0]
print(f"\nEmpty content count: {empty_content}")

# Check for empty summary
c.execute("SELECT count(*) FROM ai_news WHERE summary IS NULL OR summary = ''")
empty_summary = c.fetchone()[0]
print(f"Empty summary count: {empty_summary}")

# Check for duplicate URLs or titles
c.execute("SELECT article_url, count(*) FROM ai_news GROUP BY article_url HAVING count(*) > 1")
dup_urls = c.fetchall()
print(f"Duplicate URLs count: {len(dup_urls)}")

c.execute("SELECT title, count(*) FROM ai_news GROUP BY lower(trim(title)) HAVING count(*) > 1")
dup_titles = c.fetchall()
print(f"Duplicate titles count: {len(dup_titles)}")

conn.close()
