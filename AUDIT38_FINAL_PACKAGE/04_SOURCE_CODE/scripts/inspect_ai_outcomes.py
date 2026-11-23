import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

for j in jobs:
    if "AI Outcomes Manager, Financial Services" in j['jobTitle']:
        print(f"Job ID: {j['jobId']}")
        desc = j.get('jobDescription', '')
        sections = re.split(r'\b(About the role|Key responsibilities|Responsibilities|Minimum qualifications|Preferred qualifications|Logistics|You may be a good fit if)\b', desc, flags=re.I)
        for i in range(1, len(sections), 2):
            print(f"[{sections[i]}]: {sections[i+1][:250].strip()}\n")
        break
