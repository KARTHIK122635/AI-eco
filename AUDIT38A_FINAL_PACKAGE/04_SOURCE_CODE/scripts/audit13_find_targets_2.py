import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

sample_titles_2 = [
    'Senior Backend Software Engineer, Cloud Monetization Platform',
    'Senior Site Reliability Engineer, Data Platform',
    'Artifact AI Engineer / Consultant',
    'Artifact'
]

for title in sample_titles_2:
    matches = [j for j in jobs if title.lower() in j['jobTitle'].lower()]
    for m in matches:
        print(f"{m['jobId']} | {m['companyName']} | {m['jobTitle']}")
        print("  Current Evidence:", m.get('responsibilityEvidence'))
        print("  Current Reason:", m.get('classificationReason'))
        print()
