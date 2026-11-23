import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

d = jobs['job_4d99a9d1ea3bffb4']
print("Anthropic Life Sciences Computational JD:")
print(d['jobDescription'][:2000])
