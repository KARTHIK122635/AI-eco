import json
import asyncio
import httpx
from collections import Counter

async def main():
    with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
        jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

    agg_jobs = [j for j in jobs if j['sourceName'] in ('Arbeitnow API', 'Jobicy API', 'Remotive API')]
    print(f"Total aggregator jobs to check: {len(agg_jobs)}")

    sem = asyncio.Semaphore(25)
    results = Counter()
    records = []

    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
        async def check(j):
            url = j['applicationUrl']
            async with sem:
                try:
                    r = await client.get(url)
                    status = r.status_code
                    results[str(status)] += 1
                    records.append((j['jobId'], j['sourceName'], status, str(r.url)))
                except Exception as e:
                    err = type(e).__name__
                    results[err] += 1
                    records.append((j['jobId'], j['sourceName'], 0, err))

        await asyncio.gather(*(check(j) for j in agg_jobs))

    print("\nAggregator URL live check results:")
    for k, v in results.most_common():
        print(f"  {k}: {v}")

    with open('data/agg_url_check_results.json', 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)

if __name__ == '__main__':
    asyncio.run(main())
