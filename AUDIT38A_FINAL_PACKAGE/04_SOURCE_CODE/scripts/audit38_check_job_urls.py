import sqlite3

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT count(*) FROM ai_jobs WHERE application_url IS NULL OR application_url = ''")
empty_urls = c.fetchone()[0]
print(f"Empty application_url count: {empty_urls}")

c.execute("SELECT count(*) FROM ai_jobs WHERE application_url NOT LIKE 'http%'")
non_http_urls = c.fetchone()[0]
print(f"Non-http application_url count: {non_http_urls}")

# Check distribution of domains in application_url
c.execute("SELECT application_url FROM ai_jobs")
urls = [r[0] for r in c.fetchall()]

from urllib.parse import urlparse
from collections import Counter
domain_counts = Counter()
for u in urls:
    if u:
        dom = urlparse(u).netloc
        domain_counts[dom] += 1

print("\nApplication URL domains:")
for dom, cnt in domain_counts.most_common():
    print(f"  {dom}: {cnt}")

conn.close()
