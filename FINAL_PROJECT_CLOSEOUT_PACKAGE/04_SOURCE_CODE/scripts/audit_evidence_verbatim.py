import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

def norm_ws(s):
    if not s:
        return ""
    # normalize spaces, non-breaking spaces, newlines
    return re.sub(r'\s+', ' ', s.replace('\u00a0', ' ').replace('\u202f', ' ')).strip()

missing_resp = []
missing_qual = []
visa_in_qual = []

for r in records:
    jid = r['jobId']
    title = r['jobTitle']
    company = r['companyName']
    desc_norm = norm_ws(r['jobDescription'])
    
    resp = r['responsibilityEvidence']
    if resp:
        resp_norm = norm_ws(resp)
        if resp_norm not in desc_norm:
            missing_resp.append((jid, company, title, resp))
            
    qual = r['qualificationEvidence']
    if qual:
        qual_norm = norm_ws(qual)
        if 'visa' in qual_norm.lower() or 'sponsorship' in qual_norm.lower() or 'work authorization' in qual_norm.lower():
            visa_in_qual.append((jid, company, title, qual))
        if qual_norm not in desc_norm:
            missing_qual.append((jid, company, title, qual))

print(f"Total records checked: {len(records)}")
print(f"Visa boilerplate in qualificationEvidence: {len(visa_in_qual)}")
print(f"Qualification snippets NOT verbatim in description: {len(missing_qual)}")
print(f"Responsibility snippets NOT verbatim in description: {len(missing_resp)}")

print("\n--- Sample Visa snippets in qual ---")
for jid, comp, tit, q in visa_in_qual[:10]:
    print(f"[{comp}] {tit}: {q[:100]}...")

print("\n--- Sample non-verbatim qual snippets ---")
for jid, comp, tit, q in missing_qual[:10]:
    print(f"[{comp}] {tit}: {q[:100]}...")

print("\n--- Sample non-verbatim resp snippets ---")
for jid, comp, tit, resp in missing_resp[:10]:
    print(f"[{comp}] {tit}: {resp[:100]}...")
