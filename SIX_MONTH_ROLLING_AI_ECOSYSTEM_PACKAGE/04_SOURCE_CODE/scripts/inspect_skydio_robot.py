import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        j = json.loads(line)['content']['data']
        if j['jobId'] in ['job_16bc52df1159b77c', 'job_d98ec925aa02009f']:
            print(f"=== {j['jobId']} | {j['jobTitle']} ===")
            desc = j['jobDescription']
            print(desc[:1500])
            print('-'*50)
