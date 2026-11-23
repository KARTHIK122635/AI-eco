import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

sample_titles = [
    'Engineering Manager, Connectivity',
    'Staff Infrastructure Engineer, Cluster Infrastructure',
    'Staff+ Software Engineer, Platform Connectivity',
    'Technical Program Manager, Science Strategy & Communications',
    'Strategic Finance Manager, BU Partnership',
    'Technical Support Engineer II',
    'Senior Staff Software Engineer, AI Runtime',
    'AI R&D Engineer – Model Training',
    'Senior Backend Software Engineer, Cloud Monetization Platform',
    'Senior Site Reliability Engineer, Data Platform',
    'Artifact AI Engineer / Consultant'
]

for title in sample_titles:
    matches = [j for j in jobs if title.lower() in j['jobTitle'].lower()]
    for m in matches:
        print(f"{m['jobId']} | {m['companyName']} | {m['jobTitle']}")
        print("  Current Evidence:", m.get('responsibilityEvidence'))
        print("  Current Reason:", m.get('classificationReason'))
        print()
