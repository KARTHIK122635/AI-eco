import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

for jid in ['job_25e3f7e51aa90718', 'job_2a9e9de2ae132ef2', 'job_32374717e76f356b', 'job_509fdfe033e3db16']:
    j = jobs[jid]
    print(f"\n==================== {jid}: {j['jobTitle']} ====================")
    print(f"Reason: {j['classificationReason']}")
    print(f"Current Ev: {j.get('responsibilityEvidence')}")
    jd = j['jobDescription']
    for kw in ['Responsibilities', 'What You’ll Do', 'What you’ll do', 'What you will do', 'In this role', 'About the Role', 'As a Principal']:
        idx = jd.find(kw)
        if idx != -1:
            print(f"  [{kw}]: {jd[idx:idx+400]}")
