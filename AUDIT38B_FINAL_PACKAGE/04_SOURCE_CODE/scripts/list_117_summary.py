import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

uncertain_jobs = [j for j in jobs if j['category'] == 'UNCERTAIN']

for i, j in enumerate(uncertain_jobs):
    desc = (j.get('jobDescription') or '').replace('\n', ' ')
    print(f"[{i+1:3d}] {j['jobId']} | {j['companyName']} | {j['jobTitle']}")
    print(f"      Resp: {str(j.get('responsibilityEvidence'))[:120]}")
    print(f"      Desc: {desc[:150]}...")
