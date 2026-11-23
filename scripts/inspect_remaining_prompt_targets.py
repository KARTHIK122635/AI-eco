import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

remaining = [
    'job_61144ba521cc8449', # Databricks
    'job_1b9058f92fab34da', # Aleph Alpha
    'job_366b4bea010eed1f', # Aleph Alpha
    'job_889d2fb771307d3f', # Nebius
    'job_5fcaf184c259b65a', # CoreWeave
    'job_61fd4233c744a6f8', # CoreWeave
    'job_a8b0b2fba1f2d038', # CoreWeave
]

for jid in remaining:
    j = jobs[jid]
    print(f"=== {jid} | {j['companyName']} | {j['jobTitle']} ===")
    desc = j['jobDescription']
    # Print lines that look like responsibilities
    lines = desc.split('\n')
    for l in lines:
        l_s = l.strip()
        if any(w in l_s.lower() for w in ['responsibilities', 'you will', 'tasks', 'role', 'what you will do']):
            print("Line:", l_s[:150])
    print("=" * 60)
