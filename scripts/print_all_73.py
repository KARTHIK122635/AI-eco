import json

with open('reports/audit14_73_flagged_candidates.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

print(f"Total candidates: {len(candidates)}")
for c in candidates:
    print(f"[{c['index']:2d}] {c['jobId']} | {c['company']} | {c['title']} | {c['flag_pattern']}")
    print(f"     Reason: {c['reason']}")
    print(f"     Ev: {c['current_evidence'][:120]}")
    print()
