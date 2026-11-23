import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

# Inspect the 8 specific roles mentioned by the user
target_ids = [
    'job_16db3f40963e47c5', # Scale AI - AI Safety Residency
    'job_671b00fff11cfc18', # Together AI - Technical Writer Intern
    'job_689c9625b67fc607', # Snorkel AI - Research Fellow
    'job_ac563bb449616a82', # CoreWeave - Recruiter, Data Center Operations
    'job_bfc1bda2dd9fdcc8', # CoreWeave - Recruiting Operations Specialist
    'job_90a3078b4542f9c4', # Databricks - Data Science Intern
    'job_b031e8b7e7239b46', # Databricks - PhD GenAI Research Scientist Intern
    'job_fece52c6d4b2a2d4', # Figure AI - Team Manager
]

print("=== USER EXPLICIT TARGETS ===")
for r in records:
    if r['jobId'] in target_ids:
        print(f"\nID: {r['jobId']} | {r['companyName']} | {r['jobTitle']}")
        # print full section containing pay
        desc = r['jobDescription']
        for line in desc.split('\n'):
            if any(k in line.lower() for k in ['pay', 'salary', 'compensation', 'hourly', 'rate', 'bonus', 'stipend', '$']):
                print(f"   LINE: {line.strip()}")
