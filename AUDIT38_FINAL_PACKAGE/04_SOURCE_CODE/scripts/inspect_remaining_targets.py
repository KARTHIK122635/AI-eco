import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

target_ids = [
    'job_9e3c061de5f3230d',
    'job_5239de691155afc1',
    'job_3eb7f06aac9c95df',
    'job_f3386228b7398977',
    'job_7bfbdf8b1ac820ea'
]

for jid in target_ids:
    j = jobs[jid]
    print(f"=== {jid}: {j['jobTitle']} ===")
    desc = j['jobDescription']
    idx = -1
    for kw in ['responsibilities', 'responsibility', 'you will', 'what you\'ll do']:
        m = re.search(r'\b' + kw + r'\b', desc, re.I)
        if m:
            idx = m.start()
            break
    if idx != -1:
        print(desc[idx:idx+600])
    else:
        print(desc[:500])
    print("-" * 60)
