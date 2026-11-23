import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        j = json.loads(line)['content']['data']
        if j['jobId'] in ['job_9dcf0270490fc222', 'job_f54076e5c029a63e']:
            print(f"=== {j['jobId']} | {j['jobTitle']} ===")
            desc = j['jobDescription']
            p = desc.find('2. Your Impact')
            if p == -1: p = desc.find('Your Impact')
            if p == -1: p = desc.find('Responsibilities')
            print(desc[p:p+800])
            print('-'*50)
