import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

inspect_ids = [
    'job_1b9058f92fab34da',
    'job_366b4bea010eed1f',
    'job_4a7d1b688879c80b',
    'job_4dec34f8f167d351',
    'job_ff7804510a9b3b72',
    'job_a76aae0327db4822',
    'job_953d904c00132369',
    'job_ba5d0da6c2aa3192',
    'job_692c453001241683',
    'job_0fccf7a2e05aac14'
]

for jid in inspect_ids:
    j = jobs[jid]
    print(f"=== {jid} | {j['companyName']} | {j['jobTitle']} | Cat: {j['category']} ===")
    print("Desc preview:", repr(j['jobDescription'][:400]))
    print()
