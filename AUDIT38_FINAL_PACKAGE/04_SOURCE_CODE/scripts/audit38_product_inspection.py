import sqlite3
import json
import re

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT count(*) FROM ai_products WHERE launch_date IS NOT NULL AND launch_date != ''")
print("Launch date non-empty count:", c.fetchone()[0])

c.execute("SELECT count(*) FROM ai_products WHERE release_date IS NOT NULL AND release_date != ''")
print("Release date non-empty count:", c.fetchone()[0])

c.execute("SELECT count(*) FROM ai_products WHERE published_at IS NOT NULL AND published_at != ''")
print("Published at non-empty count:", c.fetchone()[0])

c.execute("SELECT date_type, count(*) FROM ai_products GROUP BY date_type")
print("Date type breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT date_provenance, count(*) FROM ai_products GROUP BY date_provenance")
print("Date provenance breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT provenance_source, count(*) FROM ai_products GROUP BY provenance_source")
print("Provenance source breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT product_id, entity_name, product_type, developer_or_company, launch_date, release_date, published_at, original_source_url, provenance_source FROM ai_products LIMIT 10")
print("Sample rows:")
for r in c.fetchall():
    print(dict(r))

conn.close()
