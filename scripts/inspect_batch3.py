import json

with open('reports/all_87_targets_detailed.json', 'r', encoding='utf-8') as f:
    targets = json.load(f)

for t in targets[40:60]:
    print(f"[{t['index']}] {t['jobId']} | {t['company']} | {t['title']}")
    print(f"     Reason: {t['reason']}")
    print(f"     Current: {t['current_evidence'][:100]}...")
    desc = t['description']
    for kw in ['Key responsibilities', 'Responsibilities', 'Responsibilities:', 'What you’ll do', 'What you\'ll do', 'What you will do', 'You will:', 'About the role:']:
        p = desc.find(kw)
        if p != -1:
            print(f"     Found {kw}: {desc[p:p+300]}...")
            break
    print("-" * 50)
