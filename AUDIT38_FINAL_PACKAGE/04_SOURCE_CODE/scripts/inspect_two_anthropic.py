import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f if line.strip()}

for jid in ['job_8b0aeb86027bf38c', 'job_bc4daa75bc0b654e']:
    j = jobs[jid]
    print("=" * 80)
    print(f"{j['jobTitle']} ({j['companyName']})")
    desc = j.get('jobDescription', '')
    print(desc[:500])
    # check compensation section
    m = re.search(r'.{0,50}(?:annual salary|compensation|sales bonus|ote).{0,100}', desc, re.I)
    if m:
        print(f"Salary section: {m.group(0)}")
