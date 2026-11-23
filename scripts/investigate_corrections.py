"""
Investigate Stage 2 Quality Issues:
1. Salary regex patterns across descriptions
2. Classification rules and edge cases
3. Employer websites
4. Skills separation (required vs preferred)
"""

import json
import re
from collections import Counter

JSONL_PATH = "data/canonical/canonical_jobs.jsonl"

with open(JSONL_PATH, "r", encoding="utf-8") as f:
    jobs = [json.loads(line)["content"]["data"] for line in f if line.strip()]

print(f"Total jobs loaded: {len(jobs)}")

# 1. Inspect Salary Disclosures
# Find jobs where salary is currently None, but description contains salary keywords
salary_keywords = [
    "annual salary", "compensation range", "base salary", "salary range",
    "$", "usd", "£", "gbp", "€", "eur", "ote"
]

has_salary_mention = []
currently_null = []
for j in jobs:
    desc = j["jobDescription"] or ""
    desc_lower = desc.lower()
    has_mention = any(k in desc_lower for k in ["annual salary:", "compensation range", "salary range", "base salary:", "salary:"])
    if has_mention:
        has_salary_mention.append(j)
        if j["salaryMin"] is None:
            currently_null.append(j)

print(f"\n--- SALARY AUDIT ---")
print(f"Jobs with explicit salary keywords in description: {len(has_salary_mention)}")
print(f"Jobs currently with salaryMin=None but have salary keywords: {len(currently_null)}")

# Inspect sample unextracted salary snippets
print("\nSample 10 unextracted salary snippets:")
for j in currently_null[:10]:
    desc = j["jobDescription"] or ""
    # find lines or sentences with salary or $
    snippets = []
    for s in re.split(r'[.\n]', desc):
        if any(k in s.lower() for k in ["annual salary", "salary range", "compensation range", "$", "£", "€"]):
            snippets.append(s.strip())
    print(f"\n[{j['companyName']}] {j['jobTitle']} (ID: {j['jobId']}):")
    for sn in snippets[:3]:
        print(f"   -> {sn[:120]}")
