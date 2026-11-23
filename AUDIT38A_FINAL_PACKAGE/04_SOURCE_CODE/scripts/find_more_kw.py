import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

for kw in ['Monetization', 'Data Platform', 'Consultant', 'Artifact']:
    matches = [j for j in jobs if kw.lower() in j['jobTitle'].lower() or kw.lower() in (j.get('responsibilityEvidence') or '').lower()]
    print(f"=== Keyword: {kw} (found {len(matches)}) ===")
    for m in matches[:5]:
        print(f"  {m['jobId']} | {m['companyName']} | {m['jobTitle']}")
        print(f"    Evidence: {m.get('responsibilityEvidence')[:120]}...")
