import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

d = jobs['job_67f7c6003e024de0']
print("Databricks FDE JD:")
print(d['jobDescription'][:2500])
