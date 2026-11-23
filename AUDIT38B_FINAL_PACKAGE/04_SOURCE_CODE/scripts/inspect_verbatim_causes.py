import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

def norm_ws(s):
    if not s: return ""
    return re.sub(r'\s+', ' ', s.replace('\u00a0', ' ').replace('\u202f', ' ')).strip()

missing_resp = [r for r in records if r['responsibilityEvidence'] and norm_ws(r['responsibilityEvidence']) not in norm_ws(r['jobDescription'])]
missing_qual = [r for r in records if r['qualificationEvidence'] and norm_ws(r['qualificationEvidence']) not in norm_ws(r['jobDescription'])]

print(f"Total records: {len(records)}")
print(f"Non-verbatim resp: {len(missing_resp)}")
print(f"Non-verbatim qual: {len(missing_qual)}")

# Let's see what is causing the non-verbatim in each
print("\n--- Inspecting why Resp failed ---")
for r in missing_resp[:15]:
    resp = r['responsibilityEvidence']
    desc = r['jobDescription']
    # find where in desc the words appear
    words = [w for w in re.findall(r'\b\w+\b', resp) if len(w) > 3]
    if len(words) >= 3:
        w_sub = " ".join(words[:4])
        # search for individual words
        found = [w for w in words if w.lower() in desc.lower()]
        print(f"[{r['companyName']}] {r['jobTitle'][:40]} | Len resp: {len(resp)} | Words matched: {len(found)}/{len(words)}")
        print(f"   Resp start: {repr(resp[:80])}")
