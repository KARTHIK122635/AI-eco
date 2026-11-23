import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

uncertain_jobs = [j for j in jobs if j['category'] == 'UNCERTAIN']

with open('reports/all_117_uncertain_full.txt', 'w', encoding='utf-8') as f:
    for i, j in enumerate(uncertain_jobs):
        f.write(f"=== RECORD {i+1}/117 ===\n")
        f.write(f"ID: {j['jobId']}\n")
        f.write(f"Company: {j['companyName']}\n")
        f.write(f"Title: {j['jobTitle']}\n")
        f.write(f"Category: {j['category']}\n")
        f.write(f"Resp Evidence: {j.get('responsibilityEvidence')}\n")
        f.write(f"Qual Evidence: {j.get('qualificationEvidence')}\n")
        f.write(f"Description:\n{j.get('jobDescription')}\n")
        f.write("\n" + "="*50 + "\n\n")

print(f"Wrote all 117 uncertain jobs to reports/all_117_uncertain_full.txt")
