import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

j = jobs['job_49ea2bf597ea9b3b']
desc = j['jobDescription']
print("Length of desc:", len(desc))
print("Desc preview (0-1500):")
print(desc[:1500])
