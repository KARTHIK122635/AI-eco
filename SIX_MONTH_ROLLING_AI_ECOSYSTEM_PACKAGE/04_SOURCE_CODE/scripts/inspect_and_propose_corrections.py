import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

patterns = [
    (r'\b(?:at\s+[A-Za-z0-9\s]+,?\s+)?(?:we\s+are|we\'re|is)\s+seeking\b', 'seeking'),
    (r'\bwe(?:\'re|\s+are)\s+building\b', 'building'),
    (r'\bwho\s+should\s+apply\b', 'who should apply'),
    (r'\babout\s+(?:the\s+role|wpp|scale|anthropic|databricks|coreweave|our|us)\b', 'about'),
    (r'\bforefront\s+of\b', 'forefront'),
    (r'\bteam\s+is\s+focused\s+on\b', 'team is focused on'),
    (r'\bwelcome\s+(?:remote\s+)?applicants\b', 'welcome applicants'),
    (r'\bfounded\s+by\b', 'founded by'),
    (r'\bjoin\s+(?:our|the|us)\b', 'join'),
    (r'\bour\s+mission\b', 'our mission'),
    (r'\btrusted\s+growth\s+partner\b', 'trusted growth partner'),
    (r'\bplay\s+a\s+(?:critical|key|pivotal)\s+role\b', 'play a critical role'),
    (r'\bcollaborative\s+work:\s*get\s+invited\b', 'collaborative work'),
    (r'\bwe\s+are\s+looking\s+for\b|\bwe\'re\s+looking\s+for\b', 'looking for'),
    (r'\bthe\s+ideal\s+candidate\b', 'ideal candidate')
]

matches = {}
for j in jobs:
    ev = j.get('responsibilityEvidence') or ''
    for p, name in patterns:
        m = re.search(p, ev, re.IGNORECASE)
        if m:
            matches[j['jobId']] = (j, name, m.group(0), ev)
            break

print(f"Total candidates matching patterns: {len(matches)}")

# Write candidates info to a json for detailed inspection
candidate_data = []
for jid, (j, name, matched_text, ev) in matches.items():
    candidate_data.append({
        'jobId': jid,
        'company': j['companyName'],
        'title': j['jobTitle'],
        'category': j['category'],
        'reason': j['classificationReason'],
        'pattern_matched': f"{name}: {matched_text}",
        'current_evidence': ev,
        'job_description': j['jobDescription']
    })

with open('reports/audit15_candidate_inspection_raw.json', 'w', encoding='utf-8') as f:
    json.dump(candidate_data, f, indent=2, ensure_ascii=False)

print("Saved raw candidate data to reports/audit15_candidate_inspection_raw.json")
