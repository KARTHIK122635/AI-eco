import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]
uncertain_jobs = [j for j in jobs if j['category'] == 'UNCERTAIN']

for i in range(87, len(uncertain_jobs)):
    d = uncertain_jobs[i]
    print(f"[{i+1}] {d['jobId']} | {d['companyName']} | {d['jobTitle']}")
    print('  Resp:', str(d.get('responsibilityEvidence'))[:140])
    print('  Qual:', str(d.get('qualificationEvidence'))[:140])
    desc = (d.get('jobDescription') or '').replace('\n', ' ')
    print('  Desc:', desc[:180])
    print('-'*50)
