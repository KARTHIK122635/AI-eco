import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        j = json.loads(line)['content']['data']
        if j['jobId'] == 'job_fb3b97caf24d3590':
            print(j['jobDescription'][2400:4000])
            break
