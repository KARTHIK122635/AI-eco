import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

target_ids = [
    'job_5572db9983b165e3', 'job_8b6a7fe68fff1038', 'job_9e4923f4f61926ea', 'job_c94d6cb844402565',
    'job_91933cd76e884191', 'job_d732380d4b5b6679', 'job_9d00f80e541e6fd1', 'job_4514f88d9ec70693',
    'job_a8419aebc82b1a00', 'job_8380c3e88e9c6584', 'job_86c624e1dd2c299c', 'job_7fa0c886847ad020',
    'job_2d0fc63ff4419f55', 'job_ab5ac1cc60164046', 'job_4293f2e4c2289620', 'job_0b52ba3fd883521c',
    'job_7ff814cb58f1225d', 'job_50d1df7084a06283', 'job_675a85266ca800bd', 'job_52cf5f192858c983',
    'job_707a7ad52df07edf', 'job_201518350968ce4f'
]

for jid in target_ids:
    j = jobs[jid]
    print(f"ID: {jid} | {j['companyName']} | {j['jobTitle']}")
    print(f"  Resp: {j.get('responsibilityEvidence')}")
    print(f"  Qual: {j.get('qualificationEvidence')}")
    desc = (j.get('jobDescription') or '').replace('\n', ' ')
    print(f"  Desc: {desc[:250]}")
    print('-'*60)
