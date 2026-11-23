import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

# Test user review examples
target_titles = [
    "AI Outcomes Manager, Financial Services",
    "Data Center Asset Management, Commercial Associate",
    "Anthropic Fellows Program, The Anthropic Institute (Economics & Policy)"
]

for title in target_titles:
    matching = [j for j in jobs if title.lower() in j['jobTitle'].lower()]
    for j in matching:
        print("=" * 80)
        print(f"Title: {j['jobTitle']} ({j['companyName']})")
        print(f"Current Category: {j['category']}")
        print(f"Current Reason: {j.get('classificationReason')}")
        print(f"Current Resp Ev: {j.get('responsibilityEvidence')}")
        print(f"Current Qual Ev: {j.get('qualificationEvidence')}")
