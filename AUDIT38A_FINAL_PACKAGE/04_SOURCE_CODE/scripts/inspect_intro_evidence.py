import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

count = 0
for j in jobs:
    ev = (j.get('responsibilityEvidence') or '').strip()
    if ev.startswith('We are looking for') or ev.startswith('We are seeking') or ev.startswith('About ') or ev.startswith('Join '):
        count += 1
        print(f"[{count}] {j['jobId']} | {j['companyName']} - {j['jobTitle']}")
        print(f"  Current Reason: {j.get('classificationReason')}")
        print(f"  Current Ev:     {ev}")
        desc = j.get('jobDescription') or ''
        # Look for 'responsibilit', 'duties', 'what you will do', etc.
        lines = [l.strip() for l in desc.split('\n') if l.strip()]
        resp_lines = []
        capture = False
        for l in lines:
            if any(k in l.lower() for k in ['responsibilit', 'what you will do', 'what you\'ll do', 'you will:', 'key responsibilities', 'your mission', 'your role']):
                capture = True
                continue
            if capture:
                if any(k in l.lower() for k in ['qualification', 'requirements', 'what you bring', 'what we look for', 'about you', 'skills']):
                    break
                if len(l) > 30:
                    resp_lines.append(l)
        print("  Found potential resp lines:")
        for rl in resp_lines[:3]:
            print(f"    * {rl}")
        print("-" * 60)
        if count >= 8:
            break
