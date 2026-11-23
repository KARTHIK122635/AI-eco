import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

em_target = "Leads software engineering teams, technical project delivery, and engineering architecture."
matches = [j for j in jobs if j.get('classificationReason') == em_target]
print(f"Total jobs with exact EM reason: {len(matches)}")
for m in matches:
    print(f"{m['jobId']} | {m['companyName']} | {m['jobTitle']} | {m['category']}")
