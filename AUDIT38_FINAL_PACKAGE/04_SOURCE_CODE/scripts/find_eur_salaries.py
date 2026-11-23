import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

null_jobs = [j for j in jobs if j.get('salaryMin') is None]

print(f"Total null jobs: {len(null_jobs)}")
eur_candidates = []

for j in null_jobs:
    desc = j.get('jobDescription', '')
    # Check for € or EUR with digits
    m1 = re.findall(r'.{0,30}(?:€|EUR)\s*[0-9]+.{0,40}', desc, re.I)
    m2 = re.findall(r'.{0,30}[0-9]+\s*(?:€|EUR).{0,40}', desc, re.I)
    m = m1 + m2
    if m:
        eur_candidates.append((j, list(set(m))))

print(f"Null jobs with EUR digits: {len(eur_candidates)}")
for j, matches in eur_candidates:
    print(f"\n{j['jobId']} | {j['companyName']} | {j['jobTitle']}")
    for match in matches:
        print(f"   {match.strip()}")
