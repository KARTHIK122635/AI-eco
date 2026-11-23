import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re
from scripts.build_audit12_evidence_map import extract_clean_evidence

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

CHECK_PATTERNS = [
    r'\bwe are\b',
    r'\bwe\'re\b',
    r'\bwe’re\b',
    r'\bour team\b',
    r'\babout us\b',
    r'\blooking for\b',
    r'\bhiring\b',
    r'\bjoin us\b',
    r'\bjoin our\b',
    r'\bmission\b',
    r'\bequal opportunity\b',
    r'\baffirmative action\b',
    r'\baccommodations\b',
    r'\bvisa sponsorship\b',
    r'\bcandidate\b',
    r'\bideal candidate\b',
    r'\bwho you are\b',
    r'\bwhat you\'ll need\b',
    r'\bqualifications\b',
    r'\brequirements\b'
]

flagged = []
for j in jobs:
    ev, ch = extract_clean_evidence(j)
    for pat in CHECK_PATTERNS:
        m = re.search(pat, ev, re.I)
        if m:
            flagged.append((j['jobId'], j['companyName'], j['jobTitle'], pat, ev))
            break

print(f"Total jobs with potential suspect words: {len(flagged)}")
for f in flagged[:30]:
    print(f"{f[0]} | {f[1]} | {f[2]} | Matched: {f[3]}")
    print(f"   Excerpt: {f[4][:120]}...")
