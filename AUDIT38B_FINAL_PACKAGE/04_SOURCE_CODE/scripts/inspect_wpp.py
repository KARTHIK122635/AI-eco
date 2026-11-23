import json

with open('reports/audit15_candidate_inspection_raw.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

c_dict = {c['jobId']: c for c in candidates}
c = c_dict['job_a2d39f78a759c157']
jd = c['job_description']

chunks = [p.strip() for p in jd.split('.') if p.strip()]
print(f"Total chunks in WPP: {len(chunks)}")
for i, ch in enumerate(chunks[:30]):
    print(f"[{i:02d}] {ch}")
