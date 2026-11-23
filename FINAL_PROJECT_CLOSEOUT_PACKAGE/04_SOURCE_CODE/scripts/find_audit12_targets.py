import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

target_titles = [
    "Digital Campaigns, Policy Advocacy",
    "Public Policy, Strategic Advisory",
    "Research Associate, Biology",
    "Research Scientist, Life Sciences (Chemistry)",
    "Research Scientist, Life Sciences (Large Molecules, Antibody Design)",
    "Data Acquisition Lead, Frontier Environments"
]

matched = []
for t in target_titles:
    m = [j for j in jobs if t.lower() in j['jobTitle'].lower()]
    matched.append((t, m))

for t, hits in matched:
    print(f"=== Target: {t} (found {len(hits)}) ===")
    for h in hits:
        print(f"  ID: {h['jobId']} | {h['companyName']} - {h['jobTitle']}")
        print(f"  Category: {h['category']}")
        print(f"  Reason: {h['classificationReason']}")
        print(f"  Current Resp Evidence:\n    \"{h.get('responsibilityEvidence')}\"")
        print(f"  Current Qual Evidence:\n    \"{h.get('qualificationEvidence')}\"")
        print("  Description Snippet:")
        desc = (h.get('jobDescription') or '').replace('\n', ' ')
        print(f"    {desc[:300]}...")
        print()
