import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

target_ids = [
    'job_84ec2ec6b9367148',
    'job_d3243e36ab914802',
    'job_38be0729c2816ee2',
    'job_87e7a826e1904b7b',
    'job_0186f49221af64aa',
    'job_8341f8a6faee8aef',
    'job_c4a4457141216031',
    'job_205d2992ea142ea2',
    'job_7cd7101cda12baa2',
    'job_ae1e07a4aa366094',
    'job_b3d1e130c59fe4fc',
    'job_3d50e2974f8de07f',
    'job_44dd96877e47a62c',
    'job_038d41b8c91f9424',
    'job_70b073ff12a85c03'
]

for jid in target_ids:
    j = jobs[jid]
    print(f"=== {jid}: {j['jobTitle']} ({j['companyName']}) ===")
    print("Reason:", j.get('classificationReason'))
    desc = j['jobDescription']
    # Look for responsibilities or what you'll do
    idx = -1
    for kw in ['responsibilities', 'responsibility', 'what you\'ll do', 'what you will do', 'you will']:
        m = re.search(r'\b' + kw + r'\b', desc, re.I)
        if m:
            idx = m.start()
            break
    if idx != -1:
        print("RESPONSIBILITY SNIPPET:")
        print(desc[idx:idx+600])
    else:
        print("FIRST 600 CHARS:")
        print(desc[:600])
    print("-" * 60)
