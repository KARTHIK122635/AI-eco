import json

with open('reports/audit15_candidate_inspection_raw.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

c_dict = {c['jobId']: c for c in candidates}

for jid in ['job_d937a79251d4723a', 'job_fe54132e071496e6', 'job_98be80cbc2ea655c', 'job_a2d39f78a759c157', 'job_21e78cd8d02add0c', 'job_91fd8017f05b1d94']:
    c = c_dict[jid]
    jd = c['job_description']
    print(f"\n==================== {jid}: {c['company']} | {c['title']} ====================")
    print(f"Reason: {c['reason']}")
    print(f"Current Ev: {c['current_evidence']}")
    # print all sentences or chunks
    # let's split by periods or see chunks
    chunks = [p.strip() for p in jd.split('.') if p.strip()]
    print(f"Total sentences/chunks: {len(chunks)}")
    for i in range(min(15, len(chunks))):
        print(f"  [{i}] {chunks[i]}")
