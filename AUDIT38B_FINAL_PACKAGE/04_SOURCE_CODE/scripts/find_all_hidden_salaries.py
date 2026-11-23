import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

null_jobs = [j for j in jobs if j.get('salaryMin') is None]
print(f"Scanning {len(null_jobs)} null jobs for hidden salary disclosures...")

# Comprehensive regex patterns
patterns = [
    # 1. $250-295K or $250k-300k
    (r'([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{2,3})\s*(?:k)?\s*(?:—|–|-|to)\s*([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{2,3})\s*k\s*(USD|CAD|EUR|GBP)?', 'K_RANGE'),
    # 2. $120,000.00 - $160,000.00 (with .00 or cents)
    (r'([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{2,3}(?:[,\.][0-9]{3})+(?:\.[0-9]{2})?)\s*(?:—|–|-|to)\s*([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{2,3}(?:[,\.][0-9]{3})+(?:\.[0-9]{2})?)\s*(USD|CAD|EUR|GBP)?', 'FULL_NUM_RANGE'),
    # 3. Hourly e.g. $54 — $60 USD, CAD $30-50/hour, $30 - $50 / hr
    (r'(?:hourly\s+rate|compensation)?[:\s]*([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(?:—|–|-|to)\s*([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(USD|CAD|EUR|GBP)?\s*(?:/\s*hr|/\s*hour|hourly|per\s+hour)', 'HOURLY'),
    # 4. Monthly e.g. €4.000 - €7.000 per maand / per month / monthly
    (r'([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{1,2}(?:[,\.][0-9]{3})*)\s*(?:—|–|-|to)\s*([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{1,2}(?:[,\.][0-9]{3})*)\s*(USD|CAD|EUR|GBP)?\s*(?:/\s*month|monthly|per\s+maand|per\s+month|p/m|bruto\s+per\s+maand)', 'MONTHLY'),
    # 5. Weekly / Stipend
    (r'(?:stipend|stipend\s+of)[:\s]*([$£€]|CAD|USD|EUR|GBP)?\s*([0-9]{1,2}(?:[,\.][0-9]{3})*)\s*(USD|CAD|EUR|GBP)?\s*(?:per\s+week|weekly)', 'WEEKLY_STIPEND')
]

candidates = []
for j in null_jobs:
    desc = j.get('jobDescription', '')
    title = j['jobTitle']
    comp = j['companyName']
    
    found = False
    for pat, pat_type in patterns:
        m = re.search(pat, desc, re.I)
        if m:
            # Check context to ensure it's not seed funding, series A, or placeholder
            span = desc[max(0, m.start()-40):min(len(desc), m.end()+40)]
            if any(w in span.lower() for w in ['funding', 'raised', 'seed', 'series a', 'series b', 'series c', 'valuation', 'revenue', 'budget for training', 'l&d budget']):
                continue
            candidates.append((j['jobId'], comp, title, pat_type, m.group(0), span.strip()))
            found = True
            break

print(f"\nTotal potential salary candidates found: {len(candidates)}")
for jid, comp, title, ptype, match_str, span in candidates:
    print(f"\n{jid} | {comp} | {title} | [{ptype}]")
    print(f"  Match: {match_str}")
    print(f"  Context: {span}")
