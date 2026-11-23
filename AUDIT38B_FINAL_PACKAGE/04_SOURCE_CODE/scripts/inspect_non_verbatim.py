import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

def norm_ws(s):
    if not s: return ""
    return re.sub(r'\s+', ' ', s.replace('\u00a0', ' ').replace('\u202f', ' ')).strip()

for r in records[:50]:
    jid = r['jobId']
    desc_norm = norm_ws(r['jobDescription'])
    qual = r['qualificationEvidence']
    if qual:
        q_norm = norm_ws(qual)
        if q_norm not in desc_norm:
            print("="*60)
            print(f"JID: {jid} | {r['companyName']} | {r['jobTitle']}")
            print("QUAL SNIPPET:", repr(q_norm[:120]))
            # Let's search for fragments of q_norm in desc_norm
            words = q_norm.split()[:8]
            prefix = " ".join(words)
            print("PREFIX:", repr(prefix))
            print("IN DESC?:", prefix in desc_norm)
            if prefix not in desc_norm:
                # search for first 3 words
                p3 = " ".join(words[:3])
                print("FIRST 3 WORDS IN DESC?:", p3 in desc_norm)
                # find where p3 occurs in desc_norm
                idx = desc_norm.find(p3)
                if idx != -1:
                    print("DESC NEARBY:", repr(desc_norm[idx:idx+200]))
