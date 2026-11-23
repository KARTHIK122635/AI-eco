import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

with open('reports/all_87_targets_detailed.json', 'r', encoding='utf-8') as f:
    t87_ids = {t['jobId'] for t in json.load(f)}

suspicious_patterns = [
    (r'\bvision\b', 'vision'),
    (r'\bmission\b', 'mission'),
    (r'\bculture\b', 'culture'),
    (r'\bour team\b|\bour teams\b', 'our team(s)'),
    (r'\bjoin\b', 'join'),
    (r'\babout (?:us|the|our|scale|anthropic|coreweave|openai|databricks|nebius)\b', 'about company'),
    (r'\bwe believe\b|\bwe think\b|\bwe view\b|\bwe are building\b|\bis building\b', 'we believe/building'),
    (r'\bequal opportunity\b|\baffirmative action\b|\bwe encourage you to apply\b', 'EEO / apply'),
    (r'\byears experience\b|\byears of experience\b', 'years of experience'),
    (r'\bbachelor\'s degree\b|\bdegree in\b', 'degree'),
    (r'\bideal candidate\b', 'ideal candidate'),
    (r'\bwho you are\b|\bwhat you\'ll need\b', 'who you are / what you need'),
    (r'\bminimum qualifications\b|\bpreferred qualifications\b', 'qualifications header'),
    (r'\bwhat we\'re looking for\b|\bwe are looking for\b|\bwe’re looking for\b', 'looking for'),
    (r'\bexists to ensure\b', 'exists to ensure'),
    (r'\bsit at the intersection\b', 'sit at the intersection'),
    (r'\bworld-class\b', 'world-class'),
    (r'\bcollaborative work:\b', 'collaborative work:'),
    (r'\bplay a key role in\b|\bplays a key role in\b', 'play a key role'),
    (r'^scale’s rapidly growing', 'scale rapidly growing'),
]

matched_not_in_87 = []
for j in jobs:
    ev = j.get('responsibilityEvidence', '') or ''
    hits = []
    for pat, label in suspicious_patterns:
        if re.search(pat, ev, re.IGNORECASE):
            hits.append(label)
    if hits and j['jobId'] not in t87_ids:
        matched_not_in_87.append((j, hits))

print(f"Matched jobs not in 87: {len(matched_not_in_87)}")
for j, hits in matched_not_in_87:
    print(f"{j['jobId']} | {j['companyName']} | {j['jobTitle']} | Hits: {hits}")
    print(f"   Ev: {j.get('responsibilityEvidence')[:100]}...")
