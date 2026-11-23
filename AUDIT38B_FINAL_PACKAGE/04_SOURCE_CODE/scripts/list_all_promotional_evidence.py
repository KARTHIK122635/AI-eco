import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

EXACT_PROMOTIONAL_PATTERNS = [
    r'\bmission\b',
    r'\bculture\b',
    r'\bwe believe\b',
    r'\bwe think\b',
    r'\bwe view\b',
    r'\bwe are building\b',
    r'\bis building\b',
    r'\bteam is building\b',
    r'\byou will join\b',
    r'\byou\'ll join\b',
    r'\byou’ll join\b',
    r'\bjoin our\b',
    r'\bjoin the\b',
    r'\bjoin us\b',
    r'\bfoundational to our\b',
    r'\bcore part of\b',
    r'\bsoftware is eating the world\b',
    r'\bthe team is based\b',
    r'\borganization is foundational\b',
    r'\borganization makes sure\b',
    r'\bdeep part of our\b',
    r'\bat [A-Z][a-zA-Z0-9\s]+, we\b',
    r'\bwe are a\b',
    r'\bwe\'re a\b',
    r'\bwe’re a\b',
    r'\bour goal is\b',
    r'\bour vision is\b',
    r'\bour team\b',
    r'\babout (?:us|the|our|scale|anthropic|coreweave|openai|databricks|nebius)\b',
    r'^\s*as an? [^.]*?(?:you will join|welcome to)\b'
]

flagged = []
for j in jobs:
    ev = j.get('responsibilityEvidence') or ''
    hit_pat = None
    for p in EXACT_PROMOTIONAL_PATTERNS:
        if re.search(p, ev, re.I):
            hit_pat = p
            break
    if hit_pat:
        flagged.append((j['jobId'], j['companyName'], j['jobTitle'], hit_pat, ev))

print(f"Total flagged records: {len(flagged)}")
for i, f in enumerate(flagged, 1):
    print(f"[{i:03d}] {f[0]} | {f[1]} | {f[2]} (matched: {f[3]})")
    print(f"      Ev: {f[4][:120]}...")
