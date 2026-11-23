import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]
uncertain_jobs = [j for j in jobs if j['category'] == 'UNCERTAIN']

print(f"Total: {len(uncertain_jobs)}")
short_descs = []
for i, j in enumerate(uncertain_jobs):
    desc = j.get('jobDescription') or ''
    resp = j.get('responsibilityEvidence') or ''
    qual = j.get('qualificationEvidence') or ''
    if len(desc.strip()) < 300 or not resp:
        short_descs.append((i+1, j['jobId'], j['companyName'], j['jobTitle'], len(desc.strip()), bool(resp), bool(qual)))

print(f"Found {len(short_descs)} records with short desc (<300 chars) or missing resp:")
for item in short_descs:
    print(item)
