import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

d = jobs['job_76d112469d687bb9']
print("CoreWeave Product Strategy Lead JD:")
print(d['jobDescription'][:2000])
