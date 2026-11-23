import json
import re

with open('reports/audit15_candidate_inspection_raw.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

# Also check if job_ae42444b365c6fd0 is present
all_ids = {c['jobId'] for c in candidates}
if 'job_ae42444b365c6fd0' not in all_ids:
    with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            j = json.loads(line)['content']['data']
            if j['jobId'] == 'job_ae42444b365c6fd0':
                candidates.append({
                    'jobId': j['jobId'],
                    'company': j['companyName'],
                    'title': j['jobTitle'],
                    'category': j['category'],
                    'reason': j['classificationReason'],
                    'pattern_matched': 'building: We’re building',
                    'current_evidence': j.get('responsibilityEvidence', ''),
                    'job_description': j['jobDescription']
                })
                break

print(f"Total candidates to evaluate: {len(candidates)}")

# Let's inspect each candidate's jobDescription to find candidate replacements
for idx, c in enumerate(candidates, 1):
    jid = c['jobId']
    title = c['title']
    company = c['company']
    reason = c['reason']
    ev = c['current_evidence']
    jd = c['job_description']
    pat = c['pattern_matched']
    
    print(f"\n[{idx:02d}] {jid} | {company} | {title}")
    print(f"     Reason: {reason}")
    print(f"     Matched: {pat}")
    print(f"     Current: {ev[:120]}...")
