import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

target_ids = [
    'job_d207b42e585bf8e6', # Digital Campaigns, Policy Advocacy
    'job_03adf198b79570b7', # Research Associate, Biology
    'job_80a480dfe5f61806', # Public Policy, Strategic Advisory
    'job_3ab4fad59bd0a42d', # Research Scientist, Life Sciences (Chemistry)
    'job_b30c4117b32b2e1b', # Research Scientist, Life Sciences (Large Molecules, Antibody Design)
    'job_d2ffb1910190a82b'  # Data Acquisition Lead, Frontier Environments
]

for jid in target_ids:
    j = jobs[jid]
    print(f"=== {jid}: {j['jobTitle']} ({j['companyName']}) ===")
    print("Category:", j['category'])
    print("Reason:", j['classificationReason'])
    print("Evidence:", j['responsibilityEvidence'])
    print("-" * 60)
