import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

j = jobs['job_ae1e07a4aa366094']
desc = j['jobDescription']
idx = desc.find("Research Engineer, you'll touch")
print('idx:', idx)
if idx != -1:
    print(repr(desc[idx-20:idx+200]))
else:
    print("Not found, printing 500-1500:")
    print(desc[500:1500])
