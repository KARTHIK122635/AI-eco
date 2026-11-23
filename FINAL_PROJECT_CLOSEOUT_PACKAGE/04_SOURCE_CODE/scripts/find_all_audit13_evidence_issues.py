import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

SUSPECT_PATTERNS = [
    (r'\bmission\b', 'mission'),
    (r'\bculture\b', 'culture'),
    (r'\bwe believe\b', 'we believe'),
    (r'\bwe think\b', 'we think'),
    (r'\bwe view\b', 'we view'),
    (r'\bwe are building\b', 'we are building'),
    (r'\bis building\b', 'is building'),
    (r'\bteam is building\b', 'team is building'),
    (r'\byou will join\b', 'you will join'),
    (r'\byou\'ll join\b', 'you\'ll join'),
    (r'\byou’ll join\b', 'you’ll join'),
    (r'\bjoin our\b', 'join our'),
    (r'\bjoin the\b', 'join the'),
    (r'\bjoin us\b', 'join us'),
    (r'\bfoundational to our\b', 'foundational to our'),
    (r'\bcore part of\b', 'core part of'),
    (r'\bsoftware is eating the world\b', 'software is eating the world'),
    (r'\bthe team is based\b', 'the team is based'),
    (r'\borganization is foundational\b', 'organization is foundational'),
    (r'\borganization makes sure\b', 'organization makes sure'),
    (r'\bdeep part of our\b', 'deep part of our'),
    (r'\bat [A-Z][a-zA-Z0-9\s]+, we\b', 'at Company, we'),
    (r'\bwe are a\b', 'we are a'),
    (r'\bwe\'re a\b', 'we\'re a'),
    (r'\bwe’re a\b', 'we’re a'),
    (r'\bour goal is\b', 'our goal is'),
    (r'\bour vision is\b', 'our vision is'),
    (r'\bour team\b', 'our team'),
    (r'\babout (?:us|the|our|scale|anthropic|coreweave|openai|databricks|nebius)\b', 'about us/company'),
    (r'^\s*(?:as an?|in this role)[^.]*?(?:you will join|welcome to)\b', 'introductory join')
]

matched_records = []
for j in jobs:
    ev = j.get('responsibilityEvidence') or ''
    hit = None
    for pat, label in SUSPECT_PATTERNS:
        if re.search(pat, ev, re.I):
            hit = label
            break
    if hit:
        matched_records.append((j['jobId'], j['companyName'], j['jobTitle'], hit, ev))

print(f"Total jobs evaluated: {len(jobs)}")
print(f"Total suspect evidence records found: {len(matched_records)}")
for r in matched_records:
    print(f"{r[0]} | {r[1]} | {r[2]} | Hit: {r[3]}")
    print(f"   Excerpt: {r[4]}")
    print()
