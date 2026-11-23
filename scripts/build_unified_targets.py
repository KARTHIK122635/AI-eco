import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

with open('reports/all_87_targets_detailed.json', 'r', encoding='utf-8') as f:
    t87 = json.load(f)

t87_ids = [t['jobId'] for t in t87]

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

all_targets = list(t87_ids)
for jid, j in jobs.items():
    ev = j.get('responsibilityEvidence', '') or ''
    for pat, label in suspicious_patterns:
        if re.search(pat, ev, re.IGNORECASE):
            if jid not in all_targets:
                all_targets.append(jid)
            break

print(f"Total unified target records to clean: {len(all_targets)}")

unified_details = []
for idx, jid in enumerate(all_targets, 1):
    j = jobs[jid]
    unified_details.append({
        'index': idx,
        'jobId': jid,
        'company': j['companyName'],
        'title': j['jobTitle'],
        'category': j['category'],
        'reason': j['classificationReason'],
        'current_evidence': j.get('responsibilityEvidence', ''),
        'description': j['jobDescription']
    })

with open('reports/all_109_targets.json', 'w', encoding='utf-8') as f:
    json.dump(unified_details, f, indent=2)

print("Saved reports/all_109_targets.json")
