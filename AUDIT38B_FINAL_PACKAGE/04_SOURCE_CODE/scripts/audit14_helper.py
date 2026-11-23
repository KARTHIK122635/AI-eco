import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

def print_job_info(jid):
    j = jobs[jid]
    print(f"=== {j['jobId']} | {j['companyName']} | {j['jobTitle']} ===")
    print(f"Category: {j['category']}")
    print(f"Reason: {j['classificationReason']}")
    print(f"Current Ev: {j['responsibilityEvidence']}")
    desc = j['jobDescription']
    # print snippet
    for marker in ["What You'll Do", "What you'll do", "Responsibilities", "Key responsibilities", "Key Responsibilities", "About the role"]:
        pos = desc.find(marker)
        if pos != -1:
            print(f"\n--- Found section: {marker} ---")
            print(desc[pos:pos+600])
            break

for jid in ['job_8ad086e5f89d9290', 'job_9a8d370f471b9403']:
    print_job_info(jid)
