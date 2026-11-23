import json

with open('reports/all_87_targets_detailed.json', 'r', encoding='utf-8') as f:
    targets = json.load(f)

for t in targets[24:37]:
    print(f"[{t['index']}] {t['jobId']} | {t['company']} | {t['title']}")
    print(f"     Reason: {t['reason']}")
    print(f"     Current: {t['current_evidence']}")
    print("-" * 50)
