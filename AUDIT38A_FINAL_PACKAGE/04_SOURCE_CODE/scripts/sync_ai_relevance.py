import json
import csv

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

# Synchronize stage2_ai_relevance_audit.csv
ai_rel_path = 'reports/stage2_ai_relevance_audit.csv'
with open(ai_rel_path, 'r', encoding='utf-8') as f:
    old_rows = {r['jobId']: r for r in csv.DictReader(f)}

new_rows = []
for j in jobs:
    jid = j['jobId']
    old_r = old_rows.get(jid, {})
    new_rows.append({
        'jobId': jid,
        'jobTitle': j['jobTitle'],
        'companyName': j['companyName'],
        'category': j['category'],
        'classificationReason': j['classificationReason'],
        'auditResult': old_r.get('auditResult', 'RETAIN'),
        'isAuthentic': old_r.get('isAuthentic', 'True')
    })

with open(ai_rel_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['jobId', 'jobTitle', 'companyName', 'category', 'classificationReason', 'auditResult', 'isAuthentic'])
    writer.writeheader()
    writer.writerows(new_rows)

print(f"Synchronized {ai_rel_path} with latest canonical jobs ({len(new_rows)} rows).")
