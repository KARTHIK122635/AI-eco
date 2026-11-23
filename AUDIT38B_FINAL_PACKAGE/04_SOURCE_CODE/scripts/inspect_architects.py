import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

for j in jobs:
    if 'applied ai architect' in j['jobTitle'].lower() and 'anthropic' in j['companyName'].lower():
        ev = j.get('responsibilityEvidence') or ''
        if 'as an applied ai' in ev.lower():
            desc = j['jobDescription']
            # Find where 'architect innovative' or 'guide customers' or similar is
            print(j['jobId'], j['jobTitle'])
            for phrase in ["You'll combine", "You’ll combine", "Working closely", "guide customers"]:
                if phrase in desc:
                    idx = desc.find(phrase)
                    print(f"  Found {phrase}: {repr(desc[idx:idx+150])}")
