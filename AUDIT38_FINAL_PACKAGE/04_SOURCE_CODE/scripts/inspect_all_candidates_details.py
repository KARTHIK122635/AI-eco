import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

with open('reports/audit15_candidate_inspection_raw.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

# Ensure job_ae42444b365c6fd0 is included
all_c_ids = [c['jobId'] for c in candidates]
if 'job_ae42444b365c6fd0' not in all_c_ids:
    j = jobs['job_ae42444b365c6fd0']
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

print(f"Total candidates: {len(candidates)}")

# Let's inspect each candidate
# For each candidate, print:
# - current evidence
# - sentences in job description containing keywords from reason or duties
for idx, c in enumerate(candidates, 1):
    jid = c['jobId']
    j = jobs[jid]
    jd = j['jobDescription']
    reason = j['classificationReason']
    ev = j.get('responsibilityEvidence', '')
    
    print(f"\n==================== [{idx:02d}] {jid} | {j['companyName']} | {j['jobTitle']} ====================")
    print(f"Reason: {reason}")
    print(f"Current Ev: {ev}")
    
    # Let's search for sections in JD
    # Print potential duty sentences
    # Split by newlines or common punctuation
    lines = [line.strip() for line in re.split(r'[\r\n]+', jd) if line.strip()]
    if len(lines) <= 2:
        # If no newlines, split by sentences
        lines = [s.strip() for s in re.split(r'(?<=[.!?])\s+', jd) if s.strip()]
    
    print(f"Total lines/sentences: {len(lines)}")
    # Find sentences that mention duty verbs
    duty_lines = []
    for line in lines:
        if any(verb in line.lower() for verb in ['lead', 'manage', 'build', 'design', 'develop', 'own', 'execute', 'partner', 'ensure', 'coordinate', 'implement', 'support', 'responsible for', 'oversee']):
            # Filter out lines with promotional words
            if not any(promo in line.lower() for promo in ['is at the forefront', 'our mission', 'we believe', 'we are seeking', 'who should apply', 'about wpp', 'about scale', 'welcome remote']):
                duty_lines.append(line)
    
    print("Top candidate duty sentences:")
    for d in duty_lines[:5]:
        print(f"  * {d[:120]}...")
