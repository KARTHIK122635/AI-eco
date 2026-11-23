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

print(f"Total matching candidates: {len(matches)}")
for idx, (jid, (j, name, matched_text, ev)) in enumerate(matches.items(), 1):
    print(f"[{idx:2d}] {jid} | {j['companyName']} | {j['jobTitle']} | Pat: {name} ('{matched_text}')")
    print(f"     Ev: {ev[:100]}...")
