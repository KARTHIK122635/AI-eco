import httpx
import json

app_id = '45BWZJ1SGC'
api_key = 'ZTQxNjIzMWY2Y2IxMTRhNjc4MTY4MTA1NjY0ZTg2OGU2ZDA3ZGI4ZTFiZTM4MTI2ZWQ0YmNhMzM4OGE4OGI5NWFuYWx5dGljc1RhZ3M9eWNkYyZyZXN0cmljdEluZGljZXM9WUNDb21wYW55X3Byb2R1Y3Rpb24lMkNZQ0NvbXBhbnlfQnlfTGF1bmNoX0RhdGVfcHJvZHVjdGlvbiZ0YWdGaWx0ZXJzPSU1QiUyMnljZGNfcHVibGljJTIyJTVEJnZhbGlkVW50aWw9MTc5NTMyNjExOQ=='

url = f'https://{app_id}-dsn.algolia.net/1/indexes/*/queries'
headers = {
    'x-algolia-application-id': app_id,
    'x-algolia-api-key': api_key,
    'content-type': 'application/json'
}
data = {
    'requests': [
        {
            'indexName': 'YCCompany_production',
            'params': 'hitsPerPage=5&query='
        }
    ]
}

r = httpx.post(url, headers=headers, json=data, timeout=10)
print('Algolia Status:', r.status_code)
if r.status_code == 200:
    res = r.json()
    hit_info = res['results'][0]
    print('Total hits:', hit_info.get('nbHits'))
    hits = hit_info.get('hits', [])
    if hits:
        print('Sample hit keys:', list(hits[0].keys()))
        print('Sample company name:', hits[0].get('name'))
        print('Sample one_liner:', hits[0].get('one_liner'))
        print('Sample long_description:', hits[0].get('long_description')[:100] if hits[0].get('long_description') else '')
        print('Sample team_size:', hits[0].get('team_size'))
        print('Sample website:', hits[0].get('website'))
        print('Sample tags / industry:', hits[0].get('tags'), hits[0].get('industry'))
