import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

suspect_patterns = [
    r'^\s*we are hiring\b',
    r'^\s*we\'re hiring\b',
    r'^\s*we’re hiring\b',
    r'^\s*we are looking\b',
    r'^\s*we\'re looking\b',
    r'^\s*we’re looking\b',
    r'^\s*we are seeking\b',
    r'^\s*we\'re seeking\b',
    r'^\s*we’re seeking\b',
    r'^\s*join\b',
    r'^\s*about (?:the|us|anthropic|scale|openai|coreweave|our|this|zilliz|google|databricks)\b',
    r'^\s*who we are\b',
    r'is seeking\b',
    r'is looking\b',
    r'is hiring\b',
    r'team is building\b',
    r'is building the\b',
    r'is building a\b',
    r'builds RL environments\b',
    r'^\s*at [a-zA-Z0-9\s]+, we\b',
    r'^\s*our mission is\b',
    r'^\s*come join\b',
    r'^\s*overview\b',
    r'^\s*the role\b',
    r'^\s*the position\b',
    r'^\s*about the role\b',
    r'^\s*about the team\b',
    r'^\s*we are an equal\b',
    r'^\s*anthropic is\b',
    r'^\s*scale is\b',
    r'^\s*coreweave is\b',
    r'^\s*openai is\b',
    r'^\s*databricks is\b',
    r'^\s*cresta is\b',
    r'^\s*together ai is\b',
    r'^\s*figure ai is\b',
    r'^\s*snorkel is\b',
    r'^\s*cohere is\b',
    r'^\s*mistral is\b',
    r'^\s*we believe\b',
    r'^\s*we value\b',
    r'^\s*we think\b',
    r'^\s*you will join\b',
    r'^\s*in this role, you will join\b'
]

print(f"Total jobs: {len(jobs)}")
matches = []
for j in jobs:
    ev = (j.get('responsibilityEvidence') or '').strip()
    matched_pat = None
    for p in suspect_patterns:
        if re.search(p, ev, re.I):
            matched_pat = p
            break
    if matched_pat:
        matches.append((j['jobId'], j['companyName'], j['jobTitle'], matched_pat, ev))

print(f"Found {len(matches)} suspect evidence records in canonical_jobs.jsonl:")
for m in matches:
    print(f"{m[0]} | {m[1]} | {m[2]} | Pat: {m[3]}")
    print(f"   Excerpt: {m[4][:120]}...")
