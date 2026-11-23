import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
from scripts.design_audit13_fixes import REASON_UPDATES

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    job_ids = {json.loads(line)['content']['data']['jobId'] for line in f}

for jid in REASON_UPDATES:
    if jid not in job_ids:
        print("Missing JID in canonical:", jid)
