import json

with open('reports/audit15_candidate_inspection_raw.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

c_dict = {c['jobId']: c for c in candidates}

def print_jd_sections(jid):
    c = c_dict.get(jid)
    if not c:
        print(f"Not in candidates: {jid}")
        return
    print(f"\n==================== {jid}: {c['company']} | {c['title']} ====================")
    print(f"Reason: {c['reason']}")
    print(f"Current Ev: {c['current_evidence']}")
    jd = c['job_description']
    print(f"\n--- Full Job Description (length {len(jd)}) ---")
    lines = jd.split('\n')
    for idx, line in enumerate(lines):
        if line.strip():
            print(f"L{idx:02d}: {line.strip()[:140]}")

# Let's inspect Scale Engagement Manager
print_jd_sections('job_cf830bd9939b555e')
# Subcontracts Manager
print_jd_sections('job_011867a56e3a13b5')
# Senior Applied AI Engineer
print_jd_sections('job_d937a79251d4723a')
# WPP Media SVP
print_jd_sections('job_a2d39f78a759c157')
# STEM Fellow UK
print_jd_sections('job_21e78cd8d02add0c')
# SWE Fellow Canada
print_jd_sections('job_91fd8017f05b1d94')
