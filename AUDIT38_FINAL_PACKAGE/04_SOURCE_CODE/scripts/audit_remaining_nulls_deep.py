import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

# Let's inspect all null records after the 4 specific ones
targets = {'job_4dbed03c7b9d1981', 'job_635816dfd21a2298', 'job_58809b0308baf230', 'job_675a85266ca800bd'}

remaining_null = [r for r in records if r['salaryMin'] is None and r['jobId'] not in targets]
print(f"Remaining null records to audit: {len(remaining_null)}")

# Search for any currency symbols or numbers with pay words
found_items = []
for r in remaining_null:
    desc = r['jobDescription']
    # search for numbers near dollar/euro/pound or salary terms
    m1 = re.findall(r'(?:salary|compensation|pay|rate|bonus|stipend)[^.\n\r]{0,40}(?:\$|€|£|¥|₹|\bUSD\b|\bEUR\b|\bGBP\b|\bCAD\b)\s*[\d,.]+', desc, re.I)
    m2 = re.findall(r'(?:\$|€|£|¥|₹)\s*[\d,.]+(?:\s*k|\s*K)?(?:\s*(?:-|—|to)\s*(?:\$|€|£|¥|₹)?\s*[\d,.]+(?:\s*k|\s*K)?)?\s*(?:per|\/)?\s*(?:year|yr|hour|hr|month|mo|week|wk|annum)?', desc, re.I)
    
    matches = set(m1 + m2)
    # filter out obvious false positives
    filtered = []
    for m in matches:
        # ignore 401k, 401(k), $23B, $35B company valuations, etc.
        if any(ign in m.lower() for ign in ['401k', '401(k)', '$23b', '$35b', '$1b', '$10b', '$400', '10 pays', 'de 1 000']):
            continue
        filtered.append(m)
    if filtered:
        found_items.append((r, filtered))

print(f"Found {len(found_items)} potential disclosures in remaining nulls:")
for r, m in found_items:
    print(f"\nID: {r['jobId']} | {r['companyName']} | {r['jobTitle']}")
    for s in m:
        print("   ->", s)
