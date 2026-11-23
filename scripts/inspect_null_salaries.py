import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

null_jobs = [j for j in jobs if j.get('salaryMin') is None]
print(f"Total jobs with null salary: {len(null_jobs)}")

# Search for the user's specific examples first
user_examples = [
    ("Together AI", "Director of Brand"),
    ("Together AI", "Solutions Architect"),
    ("CoreWeave", "Software Engineer, Inference"),
    ("CoreWeave", "Executive Assistant"),
    ("Databricks", "Data Science Intern"),
    ("Cresta", "Software Engineer Intern"),
    ("Squid Support", "AI Engineer"),
    ("LINKIT", "AI Machine Learning Engineer")
]

print("=== Checking User Confirmed Examples ===")
for comp_sub, title_sub in user_examples:
    found = [j for j in jobs if comp_sub.lower() in j['companyName'].lower() and title_sub.lower() in j['jobTitle'].lower()]
    for j in found:
        print(f"\nMatch: {j['jobId']} | {j['companyName']} | {j['jobTitle']} | Current salary: {j.get('salaryMin')}")
        desc = j.get('jobDescription', '')
        # Find any numbers or salary keywords
        lines = [line for line in desc.split('\n') if any(w in line.lower() for w in ['salary', 'compensation', 'pay', 'hour', 'month', '$', '€', 'cad', 'ote', 'k'])]
        for l in lines[:5]:
            print(f"  Line: {l.strip()[:150]}")
