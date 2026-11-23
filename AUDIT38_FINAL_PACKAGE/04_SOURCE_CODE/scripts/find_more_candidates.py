import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

# Let's inspect other candidates that might contain introductory/team/promotional words:
ADDITIONAL_PATTERNS = [
    r'\bour mission\b',
    r'\bwe believe\b',
    r'\bthe team is\b',
    r'\bour team\b',
    r'\bjoin\b',
    r'\bseeking a\b',
    r'\bwelcome\b',
    r'\babout (?:the role|our|us)\b',
    r'\bwho you are\b',
    r'\bwhat you will do\b',
    r'\bwhat we do\b',
]

with open('scripts/scan_audit15_candidates.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's see what else matches
for j in jobs:
    ev = j.get('responsibilityEvidence', '') or ''
    for p in ADDITIONAL_PATTERNS:
        if re.search(p, ev, re.IGNORECASE):
            print(f"{j['jobId']} | {j['companyName']} | {j['jobTitle']} | Pat: {p}")
            print(f"   Ev: {ev[:100]}...")
            break
