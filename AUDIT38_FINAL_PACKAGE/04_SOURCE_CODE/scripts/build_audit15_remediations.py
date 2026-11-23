import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

with open('reports/audit15_candidate_inspection_raw.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

# Ensure job_ae42444b365c6fd0 is present
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

print(f"Total candidates to evaluate: {len(candidates)}")

# For each candidate, let's review
results = []
for c in candidates:
    jid = c['jobId']
    j = jobs[jid]
    jd = j['jobDescription']
    ev = j.get('responsibilityEvidence', '')
    res = {
        'jobId': jid,
        'company': j['companyName'],
        'title': j['jobTitle'],
        'category': j['category'],
        'reason': j['classificationReason'],
        'matched_pattern': c['pattern_matched'],
        'current_evidence': ev,
        'status': '', # 'REPLACED' or 'RETAINED_VALID'
        'new_evidence': '',
        'rationale': ''
    }
    results.append(res)

with open('reports/audit15_candidate_eval_template.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("Saved template to reports/audit15_candidate_eval_template.json")
