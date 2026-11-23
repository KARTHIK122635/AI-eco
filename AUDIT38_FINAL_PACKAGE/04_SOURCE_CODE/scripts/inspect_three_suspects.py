import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

for jid in ['job_db2382f595bbb7fd', 'job_38af1bff8a24f3e0', 'job_14dc84751adf9885']:
    j = jobs[jid]
    print(f"=== {jid}: {j['jobTitle']} at {j['companyName']} ===")
    print("Classification reason:", j.get('classificationReason'))
    desc = j.get('jobDescription')
    print("Full Desc:")
    print(desc)
    print("=" * 60)
