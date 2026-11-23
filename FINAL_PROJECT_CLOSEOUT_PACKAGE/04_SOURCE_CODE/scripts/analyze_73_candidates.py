import json
from collections import Counter

with open('reports/audit14_73_flagged_candidates.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

print(f"Total candidates: {len(candidates)}")
cats = Counter(c['category'] for c in candidates)
print("Categories:", cats)

companies = Counter(c['company'] for c in candidates)
print("Companies:", companies)

flags = Counter(c['flag_pattern'] for c in candidates)
print("Flags:", flags)

print("\n--- Listing first 20 candidates ---")
for c in candidates[:20]:
    print(f"[{c['index']}] {c['jobId']} | {c['company']} | {c['title']} | {c['flag_pattern']}")
    print(f"   Reason: {c['reason']}")
    print(f"   Ev: {c['current_evidence'][:100]}...")
