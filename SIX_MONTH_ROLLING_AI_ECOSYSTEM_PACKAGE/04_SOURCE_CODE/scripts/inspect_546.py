import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

for target_src in ['Greenhouse: CoreWeave', 'Greenhouse: Databricks', 'Greenhouse: SambaNova Systems']:
    sub = [j for j in jobs if j['sourceName'] == target_src]
    print(f"\n{target_src} ({len(sub)} jobs):")
    for j in sub[:3]:
        print(f"  jobId: {j['jobId']}")
        print(f"  title: {j['jobTitle']}")
        print(f"  url: {j['applicationUrl']}")
        print(f"  prov: {j.get('provenance')}")
