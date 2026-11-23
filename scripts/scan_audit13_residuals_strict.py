import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re
from scripts.test_audit13_evidence_cleanup import clean_evidence_v13

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

CHECK_WORDS = [
    r'\bmission\b',
    r'\bculture\b',
    r'\bvision\b',
    r'\bour team\b',
    r'\bjoin\b',
    r'\babout (?:us|the|our|scale|anthropic|coreweave|openai|databricks|nebius)\b',
    r'\bwe believe\b',
    r'\bwe think\b',
    r'\bwe view\b',
    r'\bwe are building\b',
    r'\bis building\b',
    r'\bequal opportunity\b',
    r'\baffirmative action\b',
    r'\bwe encourage you to apply\b',
    r'\bhow we\'re different\b',
    r'\byour safety matters\b',
    r'\byears experience\b',
    r'\byears of experience\b',
    r'\bbachelor\'s degree\b',
    r'\bdegree in\b',
    r'\bideal candidate\b',
    r'\bwho you are\b',
    r'\bwhat you\'ll need\b',
    r'\bminimum qualifications\b',
    r'\bpreferred qualifications\b',
    r'\bwhat we\'re looking for\b'
]

flagged = []
for j in jobs:
    ev, ch = clean_evidence_v13(j)
    for p in CHECK_WORDS:
        if re.search(p, ev, re.I):
            flagged.append((j['jobId'], j['companyName'], j['jobTitle'], p, ev))
            break

print(f"Total jobs with flagged words: {len(flagged)}")
for f in flagged[:25]:
    print(f"{f[0]} | {f[1]} | {f[2]} | Word: {f[3]}")
    print(f"   Ev: {f[4]}")
    print()
