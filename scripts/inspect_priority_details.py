import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

targets = [
    'job_0d920108a62c8874', # Finance Fellow
    'job_8ad086e5f89d9290', # Medical Fellow UK
    'job_9a8d370f471b9403', # Medical Fellow US
    'job_4c10396068078ad5', # Principal SWE GPS
    'job_ca9fd326e9b5b4a3', # EM Billing Platform
    'job_6b50fb83f97464c3', # Staff+ SWE Billing Platform
    'job_4a03b7baf7f497e7', # Research Engineer Chip Design RL
    'job_82c44ea0d56968c5', # Research Engineer Code RL
    'job_67d5b04df41fa9f1', # Staff SWE Code RL
    'job_63a3680d2fc7006a', # Senior Product Marketing Manager Healthcare
    'job_4f4361d44526f5d7', # Data Center Tech Afton
    'job_a2b5203844474445', # Data Center Tech Cheyenne
    'job_de27bd5296f47999', # Data Center Tech Dalton
    'job_e6c5f4d8890b7630', # Data Center Tech Elk Grove
    'job_509b55147b60eecb', # Data Center Tech Ellendale
    'job_7427cacb294b9060', # Data Center Tech Express
    'job_f9a9b26d75b45013', # Data Center Tech Miami
    'job_7d02a7727c51c1d9', # Data Center Tech Sandusky
]

for tid in targets:
    j = jobs[tid]
    print(f"=== {j['jobId']} | {j['companyName']} | {j['jobTitle']} | Cat: {j['category']} ===")
    print(f"Reason: {j['classificationReason']}")
    print(f"Current Ev: {j['responsibilityEvidence']}")
    desc = j['jobDescription']
    # Look for candidate sentences in desc
    sentences = [s.strip() for s in desc.replace('\n', '. ').split('.') if len(s.strip()) > 25]
    print("Sample sentences:")
    for s in sentences[:8]:
        print(f"  * {s}")
    print("-" * 60)
