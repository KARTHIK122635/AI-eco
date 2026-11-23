import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line) for line in f]

print(f"Total records: {len(records)}")

examples = [
    ("Scale AI", "AI Safety Residency"),
    ("Together AI", "Technical Writer Intern"),
    ("Snorkel AI", "Research Fellow"),
    ("CoreWeave", "Recruiter, Data Center Operations"),
    ("CoreWeave", "Recruiting Operations Specialist"),
    ("Databricks", "Data Science Intern"),
    ("Databricks", "PhD GenAI Research Scientist Intern"),
    ("Figure AI", "Team Manager"),
]

for company, title_substr in examples:
    matches = [r for r in records if company.lower() in r['content']['data']['companyName'].lower() and title_substr.lower() in r['content']['data']['jobTitle'].lower()]
    print(f"\n--- Looking for {company} - {title_substr} (Found {len(matches)}) ---")
    for m in matches:
        d = m['content']['data']
        print(f"ID: {d['jobId']} | Company: {d['companyName']} | Title: {d['jobTitle']}")
        print(f"Current Salary: min={d['salaryMin']}, max={d['salaryMax']}, curr={d['currency']}, type={d['compensationType']}, period={d['compensationPeriod']}")
        desc = d['jobDescription']
        # search for dollar signs or numbers in desc
        lines = [line.strip() for line in desc.split('\n') if '$' in line or 'hour' in line.lower() or 'bonus' in line.lower() or 'salary' in line.lower() or 'compensation' in line.lower() or 'pay' in line.lower()]
        for l in lines[:10]:
            print(f"   Snippet: {l[:140]}")
