import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

anthropic_jobs = [j for j in jobs if j['companyName'].lower() == 'anthropic']
print(f"Total Anthropic jobs: {len(anthropic_jobs)}")

has_resp_section = 0
no_resp_section = []
for j in anthropic_jobs:
    desc = j['jobDescription']
    # Check for responsibilities marker
    m = re.search(r'\b(?:Key responsibilities|Responsibilities|What you\'ll do|Role Responsibilities|You will:)\b', desc, re.I)
    if m:
        has_resp_section += 1
    else:
        no_resp_section.append((j['jobId'], j['jobTitle']))

print(f"Anthropic jobs with clear responsibilities header: {has_resp_section} / {len(anthropic_jobs)}")
print(f"Without header: {len(no_resp_section)}")
if no_resp_section:
    for nr in no_resp_section[:10]:
        print(nr)
