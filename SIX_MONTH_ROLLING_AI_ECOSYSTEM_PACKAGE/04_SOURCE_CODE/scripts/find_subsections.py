import json
import re

with open('reports/audit15_candidate_inspection_raw.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

c_dict = {c['jobId']: c for c in candidates}

def find_subsections(jid):
    c = c_dict[jid]
    jd = c['job_description']
    print(f"\n==================== {jid}: {c['company']} | {c['title']} ====================")
    print(f"Reason: {c['reason']}")
    print(f"Current Ev: {c['current_evidence']}")
    
    # search for common section titles
    for kw in ['You will:', 'You will', 'What You’ll Do:', 'What you’ll do', 'Responsibilities:', 'Responsibilities', 'In this role you will', 'What You Will Do', 'As an EM']:
        idx = jd.find(kw)
        if idx != -1:
            print(f"\n--- Found '{kw}' at index {idx} ---")
            print(jd[idx:idx+1000])

find_subsections('job_cf830bd9939b555e')
find_subsections('job_011867a56e3a13b5')
find_subsections('job_d937a79251d4723a')
find_subsections('job_a2d39f78a759c157')
find_subsections('job_21e78cd8d02add0c')
find_subsections('job_91fd8017f05b1d94')
