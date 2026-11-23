import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

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

flagged = {}
for j in jobs:
    ev = j.get('responsibilityEvidence', '') or ''
    for p in CHECK_WORDS:
        if re.search(p, ev, re.I):
            flagged[j['jobId']] = (j, p, ev)
            break

print(f"Count from CHECK_WORDS: {len(flagged)}")

missing_priorities = [
    'job_0d920108a62c8874', # Finance Fellow
    'job_8ad086e5f89d9290', # Medical Fellow UK
    'job_9a8d370f471b9403', # Medical Fellow US
    'job_4c10396068078ad5', # Principal SWE GPS
]

for mid in missing_priorities:
    if mid not in flagged:
        mj = next(j for j in jobs if j['jobId'] == mid)
        flagged[mid] = (mj, 'priority_manual', mj.get('responsibilityEvidence', ''))

print(f"Total after adding missing priorities: {len(flagged)}")
