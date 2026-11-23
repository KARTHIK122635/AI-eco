import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

target_ids = [
    'job_0d920108a62c8874', # Finance Fellow
    'job_8ad086e5f89d9290', # Medical Fellow UK
    'job_9a8d370f471b9403', # Medical Fellow US
    'job_4c10396068078ad5', # Principal Software Engineer GPS
    'job_ca9fd326e9b5b4a3', # EM Billing Platform
    'job_6b50fb83f97464c3', # Staff+ SWE Billing Platform
    'job_4a03b7baf7f497e7', # Research Engineer Chip Design RL
    'job_82c44ea0d56968c5', # Research Engineer Code RL
    'job_67d5b04df41fa9f1', # Staff Software Engineer Code RL
    'job_63a3680d2fc7006a', # Senior Product Marketing Manager, Healthcare
    'job_a2b5203844474445', # Data Center Technician Cheyenne
    'job_de27bd5296f47999', # Data Center Technician Dalton
    'job_7427cacb294b9060', # Data Center Technician Express
]

for j in jobs:
    if j['jobId'] in target_ids:
        print(f"=== {j['jobId']} | {j['companyName']} | {j['jobTitle']} ===")
        print(f"Category: {j['category']}")
        print(f"Reason: {j['classificationReason']}")
        print(f"Current Ev: {j['responsibilityEvidence']}")
        print("FULL DESCRIPTION:")
        print(j['jobDescription'])
        print("=" * 80)
