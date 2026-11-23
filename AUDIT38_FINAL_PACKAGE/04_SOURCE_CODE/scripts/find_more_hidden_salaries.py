import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

null_jobs = [j for j in jobs if j.get('salaryMin') is None]

# Check Databricks null jobs
db_null = [j for j in null_jobs if 'databricks' in j['companyName'].lower()]
print(f"Databricks null jobs: {len(db_null)}")
for j in db_null:
    desc = j.get('jobDescription', '')
    m = re.findall(r'.{0,30}(?:hourly|per\s+hour|pay\s+range|rate|\$[0-9]+).{0,40}', desc, re.I)
    if m:
        print(f"\nDatabricks: {j['jobId']} | {j['jobTitle']}")
        for match in m[:4]:
            print(f"  {match.strip()}")

# Check Anthropic fellows stipends
fellows = [j for j in jobs if 'fellows' in j['jobTitle'].lower()]
print(f"\nFellows jobs: {len(fellows)}")
for j in fellows:
    print(f"  {j['jobId']} | {j['companyName']} | {j['jobTitle']} | Sal: {j.get('salaryMin')}")
    desc = j.get('jobDescription', '')
    m = re.findall(r'.{0,30}(?:stipend|\$[0-9]+|eur|gbp).{0,40}', desc, re.I)
    for match in m[:3]:
        print(f"    {match.strip()}")
