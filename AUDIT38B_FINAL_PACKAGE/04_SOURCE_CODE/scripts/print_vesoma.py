import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

v = jobs['job_68fc708b1be009aa']
print("Vesoma JD:")
print(v['jobDescription'])
