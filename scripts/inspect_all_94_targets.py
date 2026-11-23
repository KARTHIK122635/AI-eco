import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

PATTERNS = {
    'priority_titles': lambda j: any(t in j['jobTitle'].lower() for t in [
        'finance fellow', 'billing platform', 'chip design rl', 'code rl',
        'principal software engineer, gps', 'medical fellow',
        'product marketing manager, healthcare', 'data center technician'
    ]),
    'paint_the_vision': lambda j: 'paint the vision' in j.get('responsibilityEvidence', '').lower(),
    'as_an_intro': lambda j: re.search(r'^as an? (?:applied ai|member|deployment manager|account executive|partners solutions architect)', j.get('responsibilityEvidence', ''), re.I) is not None,
    'our_team_or_teams': lambda j: re.search(r'\bour (?:team|teams|data center operations team)\b', j.get('responsibilityEvidence', ''), re.I) is not None,
    'exists_to_ensure': lambda j: 'exists to ensure' in j.get('responsibilityEvidence', '').lower(),
    'sit_at_intersection': lambda j: 'sit at the intersection' in j.get('responsibilityEvidence', '').lower(),
    'world_class': lambda j: 'world-class' in j.get('responsibilityEvidence', '').lower(),
    'collaborative_work': lambda j: 'collaborative work:' in j.get('responsibilityEvidence', '').lower(),
    'ideal_candidate': lambda j: 'ideal candidate' in j.get('responsibilityEvidence', '').lower(),
    'years_of_experience': lambda j: 'years of experience' in j.get('responsibilityEvidence', '').lower() or 'years experience' in j.get('responsibilityEvidence', '').lower(),
    'who_you_are': lambda j: re.search(r'\bwho you are\b|\bwhat you\'ll need\b', j.get('responsibilityEvidence', ''), re.I) is not None,
    'we_are_looking_for': lambda j: re.search(r'\bwe are looking for\b|\bwe’re looking for\b|\bwe are seeking\b', j.get('responsibilityEvidence', ''), re.I) is not None,
}

hit_jobs = []
for j in jobs:
    matched = [name for name, func in PATTERNS.items() if func(j)]
    if matched:
        hit_jobs.append((j, matched))

print(f"Total matching jobs: {len(hit_jobs)}")
for idx, (j, matched) in enumerate(hit_jobs, 1):
    print(f"[{idx}] {j['jobId']} | {j['companyName']} | {j['jobTitle']} | Cat: {j['category']} | Tags: {matched}")
    print(f"    Reason: {j['classificationReason']}")
    print(f"    Current Ev: {j['responsibilityEvidence'][:120]}...")
