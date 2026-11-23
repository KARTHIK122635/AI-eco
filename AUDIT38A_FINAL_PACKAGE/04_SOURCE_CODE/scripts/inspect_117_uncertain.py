import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

uncertain_jobs = [j for j in jobs if j['category'] == 'UNCERTAIN']
print(f'Total uncertain jobs: {len(uncertain_jobs)}')

for i, j in enumerate(uncertain_jobs):
    print(f"{i+1:3d}. [{j['jobId']}] {j['companyName']} - {j['jobTitle']}")
