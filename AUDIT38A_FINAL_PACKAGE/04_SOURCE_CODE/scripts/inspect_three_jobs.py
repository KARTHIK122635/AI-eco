import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

for jid in ['job_c4a4457141216031', 'job_205d2992ea142ea2', 'job_7cd7101cda12baa2']:
    j = jobs[jid]
    print(f"=== {jid}: {j['jobTitle']} ===")
    desc = j['jobDescription']
    for kw in ['responsibilities', 'responsibility', 'you will', 'what you\'ll do']:
        m = re.search(r'\b' + kw + r'\b', desc, re.I)
        if m:
            print(desc[m.start():m.start()+400])
            print('---')
            break
