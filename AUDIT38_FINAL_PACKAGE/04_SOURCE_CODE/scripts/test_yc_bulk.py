import httpx
import time

app_id = "45BWZJ1SGC"
api_key = "ZTQxNjIzMWY2Y2IxMTRhNjc4MTY4MTA1NjY0ZTg2OGU2ZDA3ZGI4ZTFiZTM4MTI2ZWQ0YmNhMzM4OGE4OGI5NWFuYWx5dGljc1RhZ3M9eWNkYyZyZXN0cmljdEluZGljZXM9WUNDb21wYW55X3Byb2R1Y3Rpb24lMkNZQ0NvbXBhbnlfQnlfTGF1bmNoX0RhdGVfcHJvZHVjdGlvbiZ0YWdGaWx0ZXJzPSU1QiUyMnljZGNfcHVibGljJTIyJTVEJnZhbGlkVW50aWw9MTc5NTMyNjExOQ=="

url = f"https://{app_id}-dsn.algolia.net/1/indexes/*/queries"
headers = {
    "x-algolia-application-id": app_id,
    "x-algolia-api-key": api_key,
    "content-type": "application/json"
}

t0 = time.time()
payload = {
    "requests": [{"indexName": "YCCompany_production", "params": "query=AI&hitsPerPage=100&page=0"}]
}
r = httpx.post(url, headers=headers, json=payload, timeout=10)
t1 = time.time()
hits = r.json()["results"][0]["hits"]
print(f"YC 100 hits fetched in {t1-t0:.2f}s, hits count: {len(hits)}")
print(f"Sample startup: {hits[0].get('name')}, team_size: {hits[0].get('team_size')}")
