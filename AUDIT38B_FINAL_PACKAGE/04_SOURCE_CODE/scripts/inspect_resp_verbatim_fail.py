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
            missing_resp.append((r['jobId'], r['companyName'], r['jobTitle'], resp, r['jobDescription']))

print(f"Total non-verbatim resp: {len(missing_resp)}")
for jid, comp, tit, resp, desc in missing_resp[:10]:
    print("="*60)
    print(f"[{comp}] {tit}")
    print("RESP:", repr(resp[:100]))
    # Where does it fail?
    for i in range(10, len(resp)):
        if norm_ws(resp[:i]) not in norm_ws(desc):
            print(f"Failed at char {i}: {repr(resp[i-15:i+15])}")
            break
