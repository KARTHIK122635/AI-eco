import sqlite3
import json

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT batch_or_founded, count(*) FROM ai_startups GROUP BY batch_or_founded ORDER BY count(*) DESC LIMIT 25")
print("Top batch_or_founded:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT count(*) FROM ai_startups WHERE founding_date IS NOT NULL AND founding_date != ''")
print("Founding date non-empty count:", c.fetchone()[0])

c.execute("SELECT count(*) FROM ai_startups WHERE announcement_date IS NOT NULL AND announcement_date != ''")
print("Announcement date non-empty count:", c.fetchone()[0])

c.execute("SELECT count(*) FROM ai_startups WHERE published_at IS NOT NULL AND published_at != ''")
print("Published at non-empty count:", c.fetchone()[0])

c.execute("SELECT count(*) FROM ai_startups WHERE date_type IS NOT NULL AND date_type != ''")
print("Date type non-empty count:", c.fetchone()[0])

c.execute("SELECT date_type, count(*) FROM ai_startups GROUP BY date_type")
print("Date type breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT date_provenance, count(*) FROM ai_startups GROUP BY date_provenance")
print("Date provenance breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT startup_id, entity_name, batch_or_founded, founding_date, published_at, announcement_date, primary_source_url, provenance_sources FROM ai_startups LIMIT 10")
print("Sample rows:")
for r in c.fetchall():
    print(dict(r))

conn.close()
