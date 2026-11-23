import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

null_salaries = [r for r in records if r['salaryMin'] is None]

print("Auditing all candidates in null_salaries...")
results = []
for r in null_salaries:
    desc = r['jobDescription']
    # search for explicit salary / hourly / monthly / annual / stipend mentions
    matches = re.findall(r'(?:salary|compensation|pay|rate|stipend|base)[\s\S]{0,100}?(?:\$|€|£|¥|₹|USD|EUR|GBP|CAD)\s*[\d,.]+', desc, re.I)
    matches += re.findall(r'(?:\$|€|£|¥|₹)\s*[\d,.]+[\s\S]{0,40}?(?:per hour|\/hour|\/hr|per month|\/month|\/mo|per year|\/year|\/yr|annually|stipend)', desc, re.I)
    matches += re.findall(r'(?:hourly rate|hourly range|base pay range|base compensation)[\s\S]{0,80}', desc, re.I)
    if matches:
        results.append((r, list(set(matches))))

print(f"Total potential candidates: {len(results)}")
for r, m in results:
    print(f"\nID: {r['jobId']} | {r['companyName']} | {r['jobTitle']}")
    for match in m[:4]:
        # clean whitespace
        clean = " ".join(match.split())
        print(f"   -> {clean[:120]}")
