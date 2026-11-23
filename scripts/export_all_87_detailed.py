import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

with open('reports/audit14_73_flagged_candidates.json', 'r', encoding='utf-8') as f:
    c73 = json.load(f)

priority_phrases = [
    'Finance Fellow',
    'Billing Platform',
    'Chip Design RL',
    'Code RL',
    'Principal Software Engineer, GPS',
    'Medical Fellow',
    'Product Marketing Manager, Healthcare',
    'Data Center Technician'
]

all_target_ids = [c['jobId'] for c in c73]
for jid, j in jobs.items():
    if any(p.lower() in j['jobTitle'].lower() for p in priority_phrases):
        if jid not in all_target_ids:
            all_target_ids.append(jid)

print(f"Total targets: {len(all_target_ids)}")

# Write details of each target to a JSON file for inspection
target_details = []
for idx, jid in enumerate(all_target_ids, 1):
    j = jobs[jid]
    target_details.append({
        'index': idx,
        'jobId': jid,
        'company': j['companyName'],
        'title': j['jobTitle'],
        'category': j['category'],
        'reason': j['classificationReason'],
        'current_evidence': j.get('responsibilityEvidence', ''),
        'description': j['jobDescription']
    })

with open('reports/all_87_targets_detailed.json', 'w', encoding='utf-8') as f:
    json.dump(target_details, f, indent=2)

print("Saved reports/all_87_targets_detailed.json")
