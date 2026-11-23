import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

null_salaries = [r for r in records if r['salaryMin'] is None]
print(f"Total null salary records: {len(null_salaries)}")

# Check for dollar, euro, pound, or explicit keywords
candidates = []
for r in null_salaries:
    desc = r['jobDescription']
    # Look for pay/salary patterns
    patterns = [
        r'\$\s*\d+[\d,.]*(?:\s*k|\s*K)?(?:\s*(?:-|—|to)\s*\$?\s*\d+[\d,.]*(?:\s*k|\s*K)?)?\s*(?:per|\/|\ba\b)?\s*(?:hour|hr|year|yr|month|mo|week|wk|annum|annually)',
        r'(?:hourly rate|hourly range|salary|pay|compensation|stipend|base compensation)[^.\n\r]{0,40}\$?\s*\d+[\d,.]*',
        r'(?:€|£)\s*\d+[\d,.]*',
        r'\d+[\d,.]*\s*(?:USD|CAD|EUR|GBP)\s*(?:\/|per)?\s*(?:hour|hr|year|yr|month|mo|week|wk)?',
        r'rate\s+for\s+this\s+role\s+is\s+\$\d+',
        r'stipend\s+of\s+[\d,.]+'
    ]
    matched_snippets = []
    for pat in patterns:
        for m in re.finditer(pat, desc, re.I):
            matched_snippets.append(m.group(0))
    if matched_snippets:
        candidates.append((r, matched_snippets))

print(f"Found {len(candidates)} candidate records among null salaries!")
for r, snippets in candidates:
    print(f"\nID: {r['jobId']} | {r['companyName']} | {r['jobTitle']}")
    for s in snippets[:5]:
        print(f"   -> {s.strip()}")
