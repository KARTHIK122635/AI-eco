import httpx

app_id = "45BWZJ1SGC"
api_key = "ZTQxNjIzMWY2Y2IxMTRhNjc4MTY4MTA1NjY0ZTg2OGU2ZDA3ZGI4ZTFiZTM4MTI2ZWQ0YmNhMzM4OGE4OGI5NWFuYWx5dGljc1RhZ3M9eWNkYyZyZXN0cmljdEluZGljZXM9WUNDb21wYW55X3Byb2R1Y3Rpb24lMkNZQ0NvbXBhbnlfQnlfTGF1bmNoX0RhdGVfcHJvZHVjdGlvbiZ0YWdGaWx0ZXJzPSU1QiUyMnljZGNfcHVibGljJTIyJTVEJnZhbGlkVW50aWw9MTc5NTMyNjExOQ=="

url = f"https://{app_id}-dsn.algolia.net/1/indexes/*/queries"
headers = {
    "x-algolia-application-id": app_id,
    "x-algolia-api-key": api_key,
    "content-type": "application/json"
}

# Test different AI queries/filters on YC
queries = [
    "query=AI&hitsPerPage=5",
    "query=Artificial Intelligence&hitsPerPage=5",
    "query=Machine Learning&hitsPerPage=5",
    "facetFilters=%5B%22tags%3AArtificial%20Intelligence%22%5D&hitsPerPage=5",
    "facetFilters=%5B%22tags%3AGenerative%20AI%22%5D&hitsPerPage=5"
]

for q in queries:
    payload = {
        "requests": [{"indexName": "YCCompany_production", "params": q}]
    }
    r = httpx.post(url, headers=headers, json=payload, timeout=10)
    if r.status_code == 200:
        res = r.json()["results"][0]
        print(f"Params: {q[:45]}... -> Total hits: {res.get('nbHits')}")
    else:
        print(f"Error for {q}: {r.status_code}")
