import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

with open('reports/audit14_73_flagged_candidates.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

print(f"Total candidates to evaluate: {len(candidates)}")

# For each candidate, find candidate responsibility sentences from its own jobDescription
for c in candidates:
    j = jobs[c['jobId']]
    desc = j['jobDescription']
    # split into sentences
    # look for sentences in sections like Responsibilities, What you'll do, etc.
    # or sentences starting with action verbs (Lead, Build, Design, Partner, Develop, Manage, Implement, Support, Drive, Guide)
    print(f"[{c['index']:2d}] {c['jobId']} | {c['company']} | {c['title']} | Tag: {c['flag_pattern']}")
    print(f"     Reason: {c['reason']}")
    print(f"     Current: {c['current_evidence'][:100]}...")
