import json

with open('reports/audit15_candidate_inspection_raw.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

for idx, c in enumerate(candidates, 1):
    print(f"[{idx:02d}] {c['jobId']} | {c['company']} | {c['title']}")
    print(f"     Pat: {c['pattern_matched']}")
    print(f"     Ev: {c['current_evidence'][:110]}...")
    print()
