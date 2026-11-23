import json

with open('reports/all_87_targets_detailed.json', 'r', encoding='utf-8') as f:
    targets = {t['jobId']: t for t in json.load(f)}

cresta_ids = [
    'job_f37a0db650e24ab4', # Customer Strategy Director
    'job_8a2eaf03c2268b56', # Senior SWE Backend Berlin
    'job_290496d2e2a5b4f6', # Staff SWE Backend Bucharest
    'job_e0d7c5ee396ba813', # Solutions Architect
    'job_137701e6e768e918', # Senior Solutions Architect
    'job_eec1433ec677b473', # Solutions Architect
    'job_dcf271708a02a76f', # Solutions Architect (AI)
]

for jid in cresta_ids:
    t = targets[jid]
    print(f"=== {jid} | {t['title']} ===")
    print(f"Reason: {t['reason']}")
    print(f"Current Ev: {t['current_evidence']}")
    desc = t['description']
    idx = desc.find('Responsibilities')
    if idx == -1: idx = desc.find('About the role')
    print("DESC SNIPPET:")
    print(desc[idx:idx+800])
    print("-" * 60)
