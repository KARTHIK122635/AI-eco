import json
import re

with open('reports/audit15_candidate_inspection_raw.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

print(f"Loaded {len(candidates)} candidates.")

# Let's inspect the minimum cited ones first:
cited_ids = [
    'job_21e78cd8d02add0c', # STEM Fellow UK
    'job_91fd8017f05b1d94', # SWE Fellow Canada
    'job_f3d068e4db415d90', # SWE Fellow UK
    'job_3286c737ec6d7b38', # SWE Fellow US
    'job_cf830bd9939b555e', # Engagement Manager PS
    'job_d28e40a44928956a', # Engagement Manager PS
    'job_f724f26481fd28a7', # Engagement Manager PS
    'job_ac9cb76ba1d920bd', # Engagement Manager PS
    'job_a94a61fdf09a6a38', # Engagement Manager PS
    'job_d937a79251d4723a', # Senior Applied AI Engineer
    'job_fe54132e071496e6', # Senior Applied AI Engineer
    'job_011867a56e3a13b5', # Subcontracts Manager PS
    'job_a2d39f78a759c157', # SVP Data Science Lead
]

for c in candidates:
    if c['jobId'] in cited_ids:
        print(f"=== CITED: {c['jobId']} | {c['company']} | {c['title']} ===")
        print(f"Reason: {c['reason']}")
        print(f"Current Ev: {c['current_evidence']}")
        print(f"Description excerpt (first 500 chars):\n{c['job_description'][:500]}")
        print("-" * 50)
