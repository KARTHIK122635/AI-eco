import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

anthropic_ote = [j for j in jobs if j['companyName'] == 'Anthropic' and j.get('compensationType') == 'ANNUAL_OTE']
print(f"Total Anthropic ANNUAL_OTE records: {len(anthropic_ote)}")

for idx, j in enumerate(anthropic_ote, 1):
    print(f"\n{idx}. {j['jobId']} | {j['jobTitle']}")
    print(f"   Salary: {j.get('currency')} {j.get('salaryMin')} - {j.get('salaryMax')}")
    print(f"   URL: {j['applicationUrl']}")
