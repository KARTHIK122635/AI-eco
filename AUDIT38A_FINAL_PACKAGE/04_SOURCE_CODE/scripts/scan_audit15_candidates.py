import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

# Let's inspect potential introductory / promotional / team-overview / candidate patterns:
# Specific phrases from the identified minimum investigations:
# 1. "Collaborative Work: Get invited" (Fellowship roles)
# 2. "Scale AI is at the forefront" (Engagement Manager, Subcontracts Manager)
# 3. "Scale's Global Public Sector team is focused on using AI" (Senior Applied AI Engineer)
# 4. "About WPP Media" / "About [Company]" (SVP Data Science Lead)
# 5. "Who should apply" (STEM Fellow)

PATTERNS = [
    r'collaborative work:\s*get invited',
    r'is at the forefront of',
    r'team is focused on using ai',
    r'\babout (?:wpp|scale|anthropic|coreweave|together|cresta|labelbox|snorkel|nebius|databricks|google|meta|microsoft|wolt|nabla|voodoo)\b',
    r'\bwe’re building\b|\bwe are building\b',
    r'\bwho should apply\b',
    r'\bour team is\b|\bour team has\b|\bour team sits\b|\bour team builds\b',
    r'\bthe ideal candidate\b',
    r'\bwe are looking for\b|\bwe’re looking for\b',
    r'\bjoin our\b|\bjoin the\b',
    r'\bwelcome to\b',
    r'\btrusted growth partner\b',
    r'\blooking for an?\b',
    r'\bplay a (?:pivotal|critical|key) role\b',
    r'\bwho you are\b',
    r'\bwhat you will need\b|\bwhat you\'ll need\b',
    r'\bqualifications\b',
]

hits = []
for j in jobs:
    ev = j.get('responsibilityEvidence', '') or ''
    matched = []
    for pat in PATTERNS:
        if re.search(pat, ev, re.IGNORECASE):
            matched.append(pat)
    if matched:
        hits.append((j, matched, ev))

print(f"Total matching candidate jobs: {len(hits)}")
for idx, (j, matched, ev) in enumerate(hits, 1):
    print(f"[{idx:2d}] {j['jobId']} | {j['companyName']} | {j['jobTitle']} | Pat: {matched}")
    print(f"     Ev: {ev[:120]}...")
