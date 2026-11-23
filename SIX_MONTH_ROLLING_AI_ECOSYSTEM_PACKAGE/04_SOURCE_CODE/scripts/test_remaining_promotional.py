import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

from test_audit15_remediations import remediations

# Apply remediations in memory
for jid, (new_ev, status, rationale) in remediations.items():
    jobs[jid]['responsibilityEvidence'] = new_ev

# Test regex patterns on the entire dataset
patterns = [
    r'\b(?:at\s+[A-Za-z0-9\s]+,?\s+)?(?:we\s+are|we\'re|is)\s+seeking\b',
    r'\bwe(?:\'re|\s+are)\s+building\b',
    r'\bwho\s+should\s+apply\b',
    r'\babout\s+(?:the\s+role|wpp|scale|anthropic|databricks|coreweave|our|us)\b',
    r'\bforefront\s+of\b',
    r'\bteam\s+is\s+focused\s+on\b',
    r'\bwelcome\s+(?:remote\s+)?applicants\b',
    r'\bfounded\s+by\b',
    r'\bjoin\s+(?:our|the|us)\b',
    r'\bour\s+mission\b',
    r'\btrusted\s+growth\s+partner\b',
    r'\bplay\s+a\s+(?:critical|key|pivotal)\s+role\b',
    r'\bcollaborative\s+work:\s*get\s+invited\b',
    r'\bwe\s+are\s+looking\s+for\b|\bwe\'re\s+looking\s+for\b',
    r'\bthe\s+ideal\s+candidate\b'
]

hits = []
for jid, j in jobs.items():
    ev = j.get('responsibilityEvidence', '') or ''
    for p in patterns:
        m = re.search(p, ev, re.IGNORECASE)
        if m:
            hits.append((jid, j['companyName'], j['jobTitle'], p, m.group(0), ev[:100]))
            break

print(f"Remaining hits across all 1,930 records: {len(hits)}")
for h in hits:
    print(f"  {h[0]} | {h[1]} | {h[2]} | Pat: {h[3]} ('{h[4]}')")
    print(f"     Ev: {h[5]}...")
