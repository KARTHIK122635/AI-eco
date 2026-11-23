import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

def norm_ws(s):
    if not s: return ""
    return re.sub(r'\s+', ' ', s.replace('\u00a0', ' ').replace('\u202f', ' ')).strip()

missing_resp = []
for r in records:
    resp = r['responsibilityEvidence']
    if resp:
        r_norm = norm_ws(resp)
        desc_norm = norm_ws(r['jobDescription'])
        if r_norm not in desc_norm:
            missing_resp.append((r['jobId'], r['companyName'], r['jobTitle'], resp))

missing_qual = []
for r in records:
    qual = r['qualificationEvidence']
    if qual:
        q_norm = norm_ws(qual)
        desc_norm = norm_ws(r['jobDescription'])
        if q_norm not in desc_norm:
            missing_qual.append((r['jobId'], r['companyName'], r['jobTitle'], qual))

print(f"Missing Resp: {len(missing_resp)}")
print(f"Missing Qual: {len(missing_qual)}")

# Breakdown by company
from collections import Counter
print("Resp missing by company:", Counter(c for _, c, _, _ in missing_resp))
print("Qual missing by company:", Counter(c for _, c, _, _ in missing_qual))
