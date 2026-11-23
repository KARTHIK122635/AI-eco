import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

print(f"Auditing all {len(records)} records for semantic alignment:")

issues = []

for r in records:
    jid = r['jobId']
    t = r['jobTitle']
    tl = t.lower()
    cat = r['category']
    reason = r['classificationReason']
    rl = reason.lower()
    
    # 1. Recruiter reasons assigned to non-recruiter titles
    if 'recruiting' in rl or 'candidate sourcing' in rl:
        if not re.search(r'\brecruit|\btalent\b|\bsourcer\b', tl) or any(k in tl for k in ['cloud sourcing', 'data center', 'power', 'cooling', 'ofci', 'strategic sourcing']):
            if not ('talent' in tl or 'recruiting' in tl):
                issues.append((r, "Recruiting reason assigned to non-HR role"))
            elif 'cloud sourcing' in tl or 'cooling' in tl or 'ofci' in tl:
                issues.append((r, "Recruiting reason assigned to procurement/hardware role"))

    # 2. Legal contract reason assigned to recruiter or non-legal
    if 'reviews, negotiates, and manages commercial vendor contracts' in rl:
        if 'talent' in tl or 'sourcer' in tl or 'recruiter' in tl:
            issues.append((r, "Legal contract reason assigned to recruiting role"))
            
    # 3. Mentorship / intern reason assigned to senior/staff
    if 'under team mentorship' in rl or 'under engineering team mentorship' in rl:
        if any(k in tl for k in ['staff', 'senior', 'principal', 'lead', 'manager', 'director']):
            issues.append((r, "Intern/mentorship reason assigned to senior/staff role"))
            
    # 4. Engineering manager reason assigned to individual contributor
    if 'leads software engineering teams' in rl:
        if not any(k in tl for k in ['manager', 'director', 'lead', 'head', 'vp']):
            issues.append((r, "Engineering manager reason assigned to IC"))

    # 5. Core ML model training reason assigned to non-technical or sales
    if 'designs, trains, and optimizes machine learning' in rl:
        if any(k in tl for k in ['account manager', 'sales', 'marketing', 'recruiter', 'counsel']):
            issues.append((r, "ML model training reason assigned to non-technical/sales role"))

print(f"Total potential mismatches identified: {len(issues)}")
for r, msg in issues:
    print(f"[{msg}] {r['jobId']} | {r['category']} | {r['jobTitle']}")
    print(f"     Reason: {r['classificationReason']}")
