import sqlite3

w_db = 'data/working/rolling_ai_ecosystem.db'
conn = sqlite3.connect(w_db)
c = conn.cursor()

cols = [r[1] for r in c.execute("PRAGMA table_info(ai_news)").fetchall()]
print("ai_news columns:", cols)

print("\nai_news source breakdown:")
c.execute("""
SELECT 
    source_name,
    COUNT(*) as total_articles,
    SUM(CASE WHEN content IS NOT NULL AND trim(content) != '' THEN 1 ELSE 0 END) as has_content,
    SUM(CASE WHEN summary IS NOT NULL AND trim(summary) != '' THEN 1 ELSE 0 END) as has_summary,
    SUM(CASE WHEN (content IS NULL OR trim(content) = '') AND (summary IS NULL OR trim(summary) = '') THEN 1 ELSE 0 END) as empty_both
FROM ai_news
GROUP BY source_name
""")
for r in c.fetchall():
    print(" ", r)

conn.close()
