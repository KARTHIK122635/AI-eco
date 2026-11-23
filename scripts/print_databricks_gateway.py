import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

d = jobs['job_53a205e783412830']
print("Databricks AI Gateway JD:")
print(d['jobDescription'][:2000])
