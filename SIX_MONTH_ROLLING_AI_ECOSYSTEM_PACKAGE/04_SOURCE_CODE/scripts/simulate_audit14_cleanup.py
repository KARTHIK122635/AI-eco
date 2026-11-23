import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

with open('reports/audit14_all_109_replacements.json', 'r', encoding='utf-8') as f:
    replacements = json.load(f)

# Simulate update
updated_jobs = []
for j in jobs:
    j_copy = dict(j)
    if j['jobId'] in replacements:
        j_copy['responsibilityEvidence'] = replacements[j['jobId']]
    updated_jobs.append(j_copy)

BANNED = [
    r'\b(?:product|strategic|company|long-term|our)\s+vision\b|paint the vision|set the vision|shaping the vision|strategic direction, ai vision|towards our vision|from the vision',
    r'\bmission\b',
    r'\bculture\b',
    r'\bour team\b|\bour teams\b',
    r'\bjoin\b',
    r'\babout (?:us|the|our|scale|anthropic|coreweave|openai|databricks|nebius)\b',
    r'\bwe believe\b|\bwe think\b|\bwe view\b|\bwe are building\b|\bis building\b',
    r'\bequal opportunity\b|\baffirmative action\b|\bwe encourage you to apply\b',
    r'\byears experience\b|\byears of experience\b',
    r'\bbachelor\'s degree\b|\bdegree in\b',
    r'\bideal candidate\b',
    r'\bwho you are\b|\bwhat you\'ll need\b',
    r'\bminimum qualifications\b|\bpreferred qualifications\b',
    r'\bwhat we\'re looking for\b|\bwe are looking for\b|\bwe’re looking for\b',
    r'\bexists to ensure\b',
    r'\bsit at the intersection\b',
    r'\bworld-class\b',
    r'\bcollaborative work:\b',
    r'\bplay a key role in\b|\bplays a key role in\b',
    r'^scale’s rapidly growing',
]

remaining_flagged = []
for j in updated_jobs:
    ev = j.get('responsibilityEvidence', '') or ''
    hits = []
    for pat in BANNED:
        if re.search(pat, ev, re.IGNORECASE):
            hits.append(pat)
    if hits:
        remaining_flagged.append((j['jobId'], j['companyName'], j['jobTitle'], hits, ev))

print(f"Total remaining flagged jobs after 109 updates: {len(remaining_flagged)}")
for r in remaining_flagged:
    print(f"  {r[0]} | {r[1]} | {r[2]} | {r[3]}")
    print(f"     Ev: {r[4][:100]}...")
