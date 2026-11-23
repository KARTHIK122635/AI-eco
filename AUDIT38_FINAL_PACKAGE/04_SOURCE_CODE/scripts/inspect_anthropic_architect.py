import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

j = jobs['job_aaed61f362acc050']
print("Title:", j['jobTitle'])
print("Desc length:", len(j['jobDescription']))
print("\n" + j['jobDescription'])
