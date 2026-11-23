import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

uncertain_jobs = [j for j in jobs if j['category'] == 'UNCERTAIN']

out = []
for i, j in enumerate(uncertain_jobs):
    out.append({
        'index': i + 1,
        'jobId': j['jobId'],
        'companyName': j['companyName'],
        'jobTitle': j['jobTitle'],
        'category': j['category'],
        'classificationReason': j['classificationReason'],
        'responsibilityEvidence': j.get('responsibilityEvidence'),
        'qualificationEvidence': j.get('qualificationEvidence'),
        'jobDescription_snippet': (j.get('jobDescription') or '')[:400].replace('\n', ' ')
    })

with open('reports/uncertain_117_details.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"Dumped {len(out)} uncertain jobs to reports/uncertain_117_details.json")
