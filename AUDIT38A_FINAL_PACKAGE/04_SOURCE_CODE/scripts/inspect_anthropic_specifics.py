import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

target_ids = [
    'job_49ea2bf597ea9b3b',
    'job_b678befa49d8eca6',
    'job_ef2b2e6a4d0da47e',
    'job_1e8b2d8ee5e34329',
    'job_b9afa5fa330d4cfe',
    'job_9e3c061de5f3230d',
    'job_5239de691155afc1',
    'job_3eb7f06aac9c95df',
    'job_f3386228b7398977',
    'job_7bfbdf8b1ac820ea'
]

for jid in target_ids:
    j = jobs[jid]
    print(f"=== {jid}: {j['jobTitle']} ===")
    print("Reason:", j.get('classificationReason'))
    desc = j.get('jobDescription')
    # Print lines that look like responsibilities
    lines = desc.split('\n')
    print("Sample lines:")
    for l in lines:
        l_s = l.strip()
        if any(w in l_s.lower() for w in ['responsibilities', 'you will', 'design', 'build', 'develop', 'manage', 'execute', 'lead', 'evaluate', 'partner']):
            print("  *", l_s[:150])
    print()
