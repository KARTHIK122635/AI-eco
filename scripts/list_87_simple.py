import json

with open('reports/all_87_targets_detailed.json', 'r', encoding='utf-8') as f:
    targets = json.load(f)

print(f"Total targets: {len(targets)}")

# Print index, jobId, company, title, current evidence snippet
for t in targets:
    print(f"[{t['index']:2d}] {t['jobId']} | {t['company']} | {t['title']}")
    print(f"     Reason: {t['reason']}")
    print(f"     Current: {t['current_evidence'][:90]}...")
