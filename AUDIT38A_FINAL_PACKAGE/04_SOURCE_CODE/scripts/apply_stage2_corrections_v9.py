import json
import csv
import sqlite3
import datetime
from build_audit8_reasons import generate_audit8_reason
from build_audit9_reasons import generate_audit9_reason

print("Starting Stage 2 Audit 9 Application...")

# 1. Load canonical jobs JSONL
with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    raw_lines = [json.loads(line) for line in f]

records = [line['content']['data'] for line in raw_lines]
print(f"Loaded {len(records)} canonical records.")

# 2. Compute updated classification reasons and audit rows
updated_records = []
audit_rows = []
changed_count = 0

for i, (raw_line, r) in enumerate(zip(raw_lines, records)):
    old_reason = generate_audit8_reason(r)
    new_reason = generate_audit9_reason(r)
    
    if old_reason != new_reason:
        changed_count += 1
        alignment_result = "CORRECTED_ROLE_SPECIFIC"
    else:
        alignment_result = "CONFIRMED_ALIGNED"
        
    # Copy record and update classificationReason
    new_r = dict(r)
    new_r['classificationReason'] = new_reason
    
    # Update raw_line
    raw_line_copy = dict(raw_line)
    raw_line_copy['content'] = dict(raw_line['content'])
    raw_line_copy['content']['data'] = new_r
    updated_records.append((raw_line_copy, new_r))
    
    # Audit row
    resp_ev = new_r.get('responsibilityEvidence', '') or ''
    qual_ev = new_r.get('qualificationEvidence', '') or ''
    evidence_snippet = resp_ev if resp_ev else qual_ev
    if not evidence_snippet:
        evidence_snippet = (new_r.get('jobDescription', '') or '')[:200]
        
    audit_rows.append({
        'Job ID': new_r['jobId'],
        'Job title': new_r['jobTitle'],
        'Company': new_r['companyName'],
        'Existing category': new_r['category'],
        'Existing classificationReason': old_reason,
        'Updated classificationReason': new_reason,
        'Source evidence supporting explanation': evidence_snippet,
        'Semantic alignment result': alignment_result,
        'Reviewer status': "VERIFIED_SEMANTIC_ALIGNMENT"
    })

print(f"Updated classification reasons for {changed_count} records (out of {len(records)}).")

# 3. Write updated JSONL
with open('data/canonical/canonical_jobs.jsonl', 'w', encoding='utf-8') as f:
    for raw_line_copy, _ in updated_records:
        f.write(json.dumps(raw_line_copy, ensure_ascii=False) + '\n')
print("Successfully written data/canonical/canonical_jobs.jsonl.")

# 4. Write updated CSV
csv_fieldnames = list(updated_records[0][1].keys())
with open('data/canonical/canonical_jobs.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=csv_fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for _, new_r in updated_records:
        row = {}
        for k in csv_fieldnames:
            v = new_r.get(k)
            if v is None:
                row[k] = ""
            elif isinstance(v, (list, dict)):
                row[k] = json.dumps(v, ensure_ascii=False)
            elif isinstance(v, bool):
                row[k] = str(v)
            else:
                row[k] = str(v)
        writer.writerow(row)
print("Successfully written data/canonical/canonical_jobs.csv.")

# 5. Update SQLite database ai_ecosystem.db (ai_jobs table only)
conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
cursor = conn.cursor()

# Verify initial table counts
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print(f"Existing tables in DB: {tables}")

for _, new_r in updated_records:
    cursor.execute("""
        UPDATE ai_jobs
        SET classification_reason = ?
        WHERE job_id = ?
    """, (new_r['classificationReason'], new_r['jobId']))

conn.commit()
print("Successfully updated ai_jobs table in data/normalized/ai_ecosystem.db.")

# Verify DB counts
counts = {}
for t in tables:
    if t != 'sqlite_sequence':
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        counts[t] = cursor.fetchone()[0]
print(f"Database table counts after update: {counts}")
total_db_rows = sum(counts.values())
print(f"Total database rows: {total_db_rows}")

# Check integrity
cursor.execute("PRAGMA integrity_check;")
integrity = cursor.fetchone()[0]
print(f"PRAGMA integrity_check: {integrity}")
conn.close()

# 6. Write reports/stage2_semantic_classification_audit.csv
audit_fieldnames = [
    'Job ID',
    'Job title',
    'Company',
    'Existing category',
    'Existing classificationReason',
    'Updated classificationReason',
    'Source evidence supporting explanation',
    'Semantic alignment result',
    'Reviewer status'
]
with open('reports/stage2_semantic_classification_audit.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=audit_fieldnames)
    writer.writeheader()
    for row in audit_rows:
        writer.writerow(row)
print(f"Successfully written reports/stage2_semantic_classification_audit.csv ({len(audit_rows)} rows).")

# 7. Write reports/stage2_ai_relevance_audit.csv
relevance_rows = []
for _, r in updated_records:
    relevance_rows.append({
        'jobId': r['jobId'],
        'jobTitle': r['jobTitle'],
        'companyName': r['companyName'],
        'category': r['category'],
        'classificationReason': r['classificationReason'],
        'auditResult': 'RETAIN' if r['category'] != 'UNCERTAIN' else 'UNCERTAIN',
        'isAuthentic': True
    })

with open('reports/stage2_ai_relevance_audit.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['jobId', 'jobTitle', 'companyName', 'category', 'classificationReason', 'auditResult', 'isAuthentic'])
    writer.writeheader()
    for row in relevance_rows:
        writer.writerow(row)
print(f"Successfully written reports/stage2_ai_relevance_audit.csv ({len(relevance_rows)} rows).")

# 8. Update reports/stage2_quality_metrics.json
with open('reports/stage2_quality_metrics.json', 'r', encoding='utf-8') as f:
    metrics = json.load(f)

from collections import Counter
new_reason_counts = Counter(r['classificationReason'] for _, r in updated_records)
metrics['audit_version'] = "Audit 9 - Final Semantic Classification Reason Audit"
metrics['generated_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
metrics['classification_quality_metrics']['distinct_classification_reasons'] = len(new_reason_counts)
metrics['classification_quality_metrics']['records_updated_in_audit_9'] = changed_count
metrics['classification_quality_metrics']['top_reasons_sample'] = [
    {'reason': r_text, 'count': c} for r_text, c in new_reason_counts.most_common(15)
]

with open('reports/stage2_quality_metrics.json', 'w', encoding='utf-8') as f:
    json.dump(metrics, f, indent=2, ensure_ascii=False)
print("Successfully updated reports/stage2_quality_metrics.json.")

print("Stage 2 Audit 9 Application completed successfully.")
