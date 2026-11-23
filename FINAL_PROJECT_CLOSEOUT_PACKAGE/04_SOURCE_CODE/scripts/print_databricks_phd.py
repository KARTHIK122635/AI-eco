import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

d = jobs['job_22b89547b209fb71']
print("Databricks Systems PhD JD:")
print(d['jobDescription'][:2000])
