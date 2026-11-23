import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

for jid in ['job_aa001c816ac245da', 'job_3f7c9cb190129a33']:
    j = jobs[jid]
    print(f"=== {jid} | {j['jobTitle']} ===")
    desc = j['jobDescription']
    idx = -1
    for kw in ["You will:", "Responsibilities:", "What you'll do:", "You will"]:
        m = re.search(r'\b' + kw, desc, re.I)
        if m:
            idx = m.start()
            break
    if idx != -1:
        print(desc[idx:idx+600])
    else:
        print(desc[:500])
    print("-" * 60)
