import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import csv
import sqlite3
import hashlib
from datetime import datetime, timezone
from scripts.build_audit12_evidence_map import extract_clean_evidence, SPECIFIC_TARGET_EXCERPTS, contains_boilerplate

def apply_audit12():
    print("=== Step 1: Loading canonical JSONL ===")
    with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
        raw_lines = [line.strip() for line in f if line.strip()]

    parsed_records = [json.loads(line) for line in raw_lines]
    jobs = [p['content']['data'] for p in parsed_records]
    print(f"Loaded {len(jobs)} canonical jobs.")

    print("\n=== Step 2: Applying substantive evidence extractions ===")
    updated_count = 0
    updated_records = []
    for i, j in enumerate(jobs):
        old_ev = j.get('responsibilityEvidence') or ''
        new_ev, changed = extract_clean_evidence(j)
        desc = j.get('jobDescription') or ''
        
        # Validation checks
        assert new_ev in desc, f"Verbatim error on {j['jobId']}: {new_ev}"
        assert not contains_boilerplate(new_ev), f"Boilerplate detected on {j['jobId']}: {new_ev}"
        
        if changed:
            updated_count += 1
            updated_records.append((j['jobId'], j['companyName'], j['jobTitle'], old_ev, new_ev))
            j['responsibilityEvidence'] = new_ev
            parsed_records[i]['content']['data']['responsibilityEvidence'] = new_ev

    print(f"Total jobs updated: {updated_count}")

    # Confirm the 6 mandated targets specifically
    for jid, expected in SPECIFIC_TARGET_EXCERPTS.items():
        j = [x for x in jobs if x['jobId'] == jid][0]
        actual = j['responsibilityEvidence']
        assert actual == expected, f"Mismatch on target {jid}!\nExpected: {expected}\nActual: {actual}"
    print("Confirmed: All specific targets matched exactly!")

    print("\n=== Step 3: Writing updated data/canonical/canonical_jobs.jsonl ===")
    with open('data/canonical/canonical_jobs.jsonl', 'w', encoding='utf-8') as f:
        for p in parsed_records:
            f.write(json.dumps(p, ensure_ascii=False) + '\n')
    print("Successfully wrote canonical_jobs.jsonl")

    print("\n=== Step 4: Exporting data/canonical/canonical_jobs.csv ===")
    csv_columns = list(jobs[0].keys())

    with open('data/canonical/canonical_jobs.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for j in jobs:
            row = {}
            for col in csv_columns:
                val = j.get(col)
                if val is None:
                    row[col] = ''
                elif isinstance(val, (list, dict)):
                    row[col] = json.dumps(val, ensure_ascii=False)
                elif isinstance(val, bool):
                    row[col] = str(val)
                elif isinstance(val, (int, float)):
                    row[col] = str(val)
                else:
                    row[col] = str(val)
            writer.writerow(row)
    print("Successfully exported canonical_jobs.csv")

    print("\n=== Step 5: Updating data/normalized/ai_ecosystem.db (ai_jobs table) ===")
    db_path = 'data/normalized/ai_ecosystem.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM ai_jobs")
    ai_jobs_count = cur.fetchone()[0]
    assert ai_jobs_count == 1930, f"Expected 1930 ai_jobs, got {ai_jobs_count}"

    for j in jobs:
        cur.execute("""
            UPDATE ai_jobs
            SET responsibility_evidence = ?
            WHERE job_id = ?
        """, (j['responsibilityEvidence'], j['jobId']))

    conn.commit()

    # Integrity check
    cur.execute("PRAGMA integrity_check;")
    integrity = cur.fetchone()[0]
    assert integrity == 'ok', f"Database integrity check failed: {integrity}"
    print(f"SQLite PRAGMA integrity_check: {integrity}")

    # Check total database rows across all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    total_db_rows = 0
    table_counts = {}
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = cur.fetchone()[0]
        table_counts[t] = cnt
        total_db_rows += cnt
    conn.close()

    print(f"SQLite table row counts: {table_counts}")
    print(f"Total SQLite rows preserved: {total_db_rows}")
    assert total_db_rows == 6745, f"Expected 6745 total rows, got {total_db_rows}"

    print("\n=== Step 6: Updating reports/stage2_semantic_classification_audit.csv ===")
    semantic_report_path = 'reports/stage2_semantic_classification_audit.csv'
    semantic_rows = []
    with open(semantic_report_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            semantic_rows.append(r)

    jobs_by_id = {j['jobId']: j for j in jobs}
    for r in semantic_rows:
        jid = r['Job ID']
        if jid in jobs_by_id:
            r['Source evidence supporting explanation'] = jobs_by_id[jid]['responsibilityEvidence']

    with open(semantic_report_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(semantic_rows)
    print(f"Successfully updated {semantic_report_path} ({len(semantic_rows)} rows)")

    print("\n=== Step 7: Verifying reports/stage2_classification_reason_quality_audit.csv ===")
    quality_audit_path = 'reports/stage2_classification_reason_quality_audit.csv'
    q_rows = []
    with open(quality_audit_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        q_fieldnames = reader.fieldnames
        for r in reader:
            q_rows.append(r)

    pass_count = sum(1 for r in q_rows if r['audit_status'] == 'PASS')
    review_count = sum(1 for r in q_rows if r['audit_status'] == 'REQUIRES_REVIEW')
    fail_count = sum(1 for r in q_rows if r['audit_status'] == 'FAIL')
    print(f"Quality audit breakdown: {pass_count} PASS, {review_count} REQUIRES_REVIEW, {fail_count} FAIL")
    assert pass_count == 1878 and review_count == 52 and fail_count == 0

    print("\n=== Step 8: Updating reports/stage2_quality_metrics.json ===")
    metrics_path = 'reports/stage2_quality_metrics.json'
    with open(metrics_path, 'r', encoding='utf-8') as f:
        metrics = json.load(f)

    metrics['audit_version'] = "Audit 12 – Final Semantic Evidence Corrections"
    metrics['generated_at'] = datetime.now(timezone.utc).isoformat()
    metrics['evidence_metrics']['responsibility_evidence_coverage'] = 1930
    metrics['evidence_metrics']['responsibility_verbatim_match_pct'] = 100.0
    metrics['evidence_metrics']['introductory_evidence_snippets_eliminated'] = updated_count
    metrics['evidence_metrics']['promotional_boilerplate_in_evidence'] = 0

    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print("Successfully updated reports/stage2_quality_metrics.json")

    print("\n=== Summary of corrections applied ===")
    print(f"Total jobs in dataset: {len(jobs)}")
    print(f"Total evidence excerpts updated to substantive duties: {updated_count}")
    print("All checks completed successfully!")

if __name__ == '__main__':
    apply_audit12()
