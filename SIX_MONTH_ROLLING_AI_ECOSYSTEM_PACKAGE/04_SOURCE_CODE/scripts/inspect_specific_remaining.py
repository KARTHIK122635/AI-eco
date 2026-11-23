import json

with open('reports/all_87_targets_detailed.json', 'r', encoding='utf-8') as f:
    targets = {t['jobId']: t for t in json.load(f)}

check_ids = [
    'job_dec08a00c3ca6fe1',
    'job_eb55db7bacee02ee',
    'job_16bc52df1159b77c',
    'job_d98ec925aa02009f',
    'job_566f348bd3bf0e18',
    'job_cf172bf7557a0ff6',
    'job_720ab8670e44abea',
    'job_3eed57cf8a82a763',
    'job_3a10b52751a1502a',
    'job_265369bd508c5241',
    'job_250264be75f8dafc',
    'job_01654beed0a04548',
    'job_752ebcc3e0493ad4',
    'job_e58baeb7a86d3815',
    'job_c4489b6d5491b5ca',
    'job_ad0a653b919ed9e7',
    'job_4370eb0694ede9e6',
    'job_b097510b7a51bd85',
]

for jid in check_ids:
    t = targets[jid]
    print(f"=== {jid} | {t['company']} | {t['title']} ===")
    print(f"Current Ev: {t['current_evidence']}")
    desc = t['description']
    print("DESC SNIPPET (first 1000 chars):")
    print(desc[:1000])
    print("-" * 60)
