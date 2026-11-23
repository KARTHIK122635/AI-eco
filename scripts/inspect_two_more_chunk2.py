import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        j = json.loads(line)['content']['data']
        if j['jobId'] in ['job_f37a0db650e24ab4', 'job_961d3a659e5894c4']:
            print(f"=== {j['jobId']} | {j['jobTitle']} ===")
            desc = j['jobDescription']
            print(desc[1300:2800])
            print('-'*50)
