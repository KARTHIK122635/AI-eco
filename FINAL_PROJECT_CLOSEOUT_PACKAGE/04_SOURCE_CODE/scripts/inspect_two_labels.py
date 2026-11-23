import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        j = json.loads(line)['content']['data']
        if j['jobId'] in ['job_fb3b97caf24d3590', 'job_beb466c57c7e3e6e']:
            print(f"=== {j['jobId']} | {j['jobTitle']} ===")
            print(j['jobDescription'][800:2500])
            print('-'*50)
