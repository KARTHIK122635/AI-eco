import json
import httpx
from urllib.parse import urlparse

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

agg_jobs = [j for j in jobs if j['sourceName'] in ('Arbeitnow API', 'Jobicy API', 'Remotive API')]
print(f"Total aggregator jobs: {len(agg_jobs)}")

results = {}
with httpx.Client(timeout=6.0, follow_redirects=True) as client:
    for j in agg_jobs:
        url = j['applicationUrl']
        try:
            r = client.get(url)
            status = r.status_code
            results[status] = results.get(status, 0) + 1
        except Exception as e:
            err = type(e).__name__
            results[err] = results.get(err, 0) + 1

print("\nAggregator URL live check results:")
for k, v in results.items():
    print(f"  {k}: {v}")
