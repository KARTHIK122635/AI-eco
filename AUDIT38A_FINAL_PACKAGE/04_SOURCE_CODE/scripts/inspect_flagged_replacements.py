import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re
from scripts.test_comprehensive_evidence_fix import extract_substantive_evidence

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

GENERIC_BOILERPLATE = [
    r'quickly growing group of committed',
    r'mission is to create',
    r'safe and beneficial',
    r'shape the trajectory of one of the most consequential',
    r'connective tissue between',
    r'equal opportunity',
    r'public benefit corporation',
    r'we offer competitive compensation',
    r'research shows that people who identify',
    r'we encourage you to apply even if',
    r'how we\'re different',
    r'your safety matters',
    r'years experience',
    r'years of experience',
    r'bachelor\'s degree',
    r'degree in'
]

flagged = []
for j in jobs:
    ev, ch = extract_substantive_evidence(j)
    if ch:
        for b in GENERIC_BOILERPLATE:
            if re.search(b, ev, re.I):
                flagged.append((j['jobId'], j['jobTitle'], b, ev))
                break

print(f"Flagged {len(flagged)} out of 110:")
for f in flagged:
    print(f"{f[0]} | {f[1]} | Pattern: {f[2]}")
    print(f"   Excerpt: {f[3]}")
