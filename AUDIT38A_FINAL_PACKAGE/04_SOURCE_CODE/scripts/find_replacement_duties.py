import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

with open('reports/audit14_73_flagged_candidates.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

for c in candidates:
    j = jobs[c['jobId']]
    desc = j['jobDescription']
    # Let's search for responsibilities section
    lines = desc.split('\n')
    duty_lines = []
    in_resp = False
    for line in lines:
        l_str = line.strip()
        if any(h in l_str.lower() for h in ['key responsibilities', 'responsibilities:', 'what you’ll do', 'what you\'ll do', 'what you will do']):
            in_resp = True
            continue
        if in_resp and any(h in l_str.lower() for h in ['qualifications', 'who you are', 'requirements', 'what we look for', 'about us', 'benefits', 'compensation', 'logistics']):
            in_resp = False
            continue
        if in_resp and len(l_str) > 25:
            duty_lines.append(l_str)
            
    # print summary
    print(f"[{c['index']:2d}] {c['jobId']} | {c['company']} | {c['title']}")
    print(f"     Reason: {c['reason']}")
    print(f"     Current: {c['current_evidence'][:100]}...")
    if duty_lines:
        print(f"     Duty lines found ({len(duty_lines)}):")
        for dl in duty_lines[:3]:
            print(f"       -> {dl[:100]}...")
    else:
        print("     No explicit duty lines section found in line split")
    print("-" * 50)
