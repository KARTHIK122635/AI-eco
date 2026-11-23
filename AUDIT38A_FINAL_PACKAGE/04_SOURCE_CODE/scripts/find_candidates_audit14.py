import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

# Patterns for introductory, promotional, team-overview, generic positioning
PATTERNS = [
    (r'\bvision\b', 'vision'),
    (r'\bmission\b', 'mission'),
    (r'\bculture\b', 'culture'),
    (r'\bour team\b', 'our team'),
    (r'\bour mission\b', 'our mission'),
    (r'\bjoin\b', 'join'),
    (r'\babout (?:us|the|our|scale|anthropic|coreweave|openai|databricks|nebius)\b', 'about company'),
    (r'\bwe believe\b', 'we believe'),
    (r'\bwe think\b', 'we think'),
    (r'\bwe view\b', 'we view'),
    (r'\bwe are building\b', 'we are building'),
    (r'\bis building\b', 'is building'),
    (r'\bwe are looking for\b', 'we are looking for'),
    (r'\blooking for a\b', 'looking for a'),
    (r'\bseeking a\b', 'seeking a'),
    (r'\byou will be a\b', 'you will be a'),
    (r'\byou will be part of\b', 'you will be part of'),
    (r'\bas an? [A-Z]', 'as an X'),
    (r'\bideal candidate\b', 'ideal candidate'),
    (r'\bwho you are\b', 'who you are'),
    (r'\bwhat you\'ll need\b', 'what you will need'),
    (r'\bwhat we\'re looking for\b', 'what we are looking for'),
    (r'\bwhat you will do\b', 'what you will do header'),
    (r'\bminimum qualifications\b', 'min qualifications'),
    (r'\bpreferred qualifications\b', 'pref qualifications'),
    (r'\byears of experience\b', 'years of experience'),
    (r'\byears experience\b', 'years experience'),
    (r'\bplay a key role in\b', 'play a key role'),
    (r'\bsit at the intersection\b', 'sit at intersection'),
    (r'\bexists to ensure\b', 'exists to ensure'),
    (r'\bcutting-edge\b', 'cutting-edge'),
    (r'\bworld-class\b', 'world-class'),
    (r'\bcompetitive compensation\b', 'competitive compensation'),
    (r'\bequal opportunity\b', 'equal opportunity'),
    (r'\bfast-paced\b', 'fast-paced'),
    (r'\bexcited to\b', 'excited to'),
    (r'\bpassion for\b', 'passion for')
]

candidates = []
for j in jobs:
    ev = j.get('responsibilityEvidence', '') or ''
    matched_pats = []
    for pat, name in PATTERNS:
        if re.search(pat, ev, re.IGNORECASE):
            matched_pats.append(name)
    if matched_pats:
        candidates.append((j, matched_pats))

print(f"Total matching candidates: {len(candidates)}")

# Check our priority roles specifically
priorities = [
    'Finance Fellow',
    'Billing Platform',
    'Chip Design RL',
    'Code RL',
    'Principal Software Engineer, GPS',
    'Medical Fellow',
    'Product Marketing Manager, Healthcare',
    'Data Center Technician'
]

print("\nPriority roles in candidates:")
for j, pats in candidates:
    for p in priorities:
        if p.lower() in j['jobTitle'].lower():
            print(f"- {j['jobId']} | {j['companyName']} | {j['jobTitle']} | Patterns: {pats}")
            print(f"  Ev: {j['responsibilityEvidence'][:120]}...")
            break
