import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

# Let's inspect the exact candidates
# What are the phrases that indicate introductory / promotional / team-overview / generic positioning?
intro_patterns = [
    # Mission / about / company statements
    r'^about anthropic',
    r'^anthropic exists to ensure',
    r'^scale’s rapidly growing',
    r'^at scale, our mission',
    r'^built for pioneers',
    r'^the world’s leading companies',
    r'^coreweave is',
    r'^our mission is',
    r'^our vision is',
    r'^our data center operations team is',
    r'^our reinforcement learning teams sit',
    r'^collaborative work: get invited',
    # "As an [role], you will..."
    r'^as an? .*? you will',
    r'^as an? .*? at',
    # "We are looking for..."
    r'we are looking for',
    r'we’re looking for',
    r'we are seeking',
    r'looking for a',
    # "The ideal candidate..."
    r'the ideal candidate',
    r'ideal candidate will',
    # "Who you are..."
    r'who you are',
    r'what you\'ll need',
    r'minimum qualifications',
    r'preferred qualifications',
    # "Play a key role..."
    r'play a key role in',
    r'plays a key role in',
    # "You will be responsible for..."
    r'you will be a pre-sales architect',
    r'paint the vision',
    r'sit at the intersection',
    r'world-class'
]

flagged_records = []
for j in jobs:
    ev = j.get('responsibilityEvidence', '') or ''
    is_flagged = False
    reasons = []
    for pat in intro_patterns:
        if re.search(pat, ev, re.IGNORECASE):
            is_flagged = True
            reasons.append(pat)
    if is_flagged:
        flagged_records.append((j, reasons))

print(f"Total flagged by refined patterns: {len(flagged_records)}")
for j, r in flagged_records:
    print(f"{j['jobId']} | {j['companyName']} | {j['jobTitle']} | Pat: {r[0]}")
    print(f"   Ev: {j['responsibilityEvidence'][:140]}...")
