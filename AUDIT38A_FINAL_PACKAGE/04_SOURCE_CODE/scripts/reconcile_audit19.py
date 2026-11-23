"""
Audit 19 to Audit 24 Historical Reconciliation Script.
Reconciles the original 366 Audit 19 records against subsequent database states using
exact key-level matching (record_id, entity_type, field_name) without positional slicing.
"""

import sqlite3
import csv
import json
import os
import sys

def reconcile(db_path: str = "data/normalized/ai_ecosystem.db",
              baseline_db_path: str = "reports/audit19_original_baseline.db",
              json_export_path: str = "reports/audit19_original_366_records.json",
              csv_output_path: str = "reports/audit19_to_audit23_reconciliation.csv"):
    
    # 1. Read baseline 366 records
    if os.path.exists(baseline_db_path):
        conn_19 = sqlite3.connect(baseline_db_path)
        conn_19.row_factory = sqlite3.Row
        cur_19 = conn_19.cursor()
        cur_19.execute("SELECT * FROM enrichment_audit_log")
        audit19_rows = [dict(r) for r in cur_19.fetchall()]
        conn_19.close()
    elif os.path.exists(json_export_path):
        with open(json_export_path, 'r', encoding='utf-8') as f:
            audit19_rows = json.load(f)
    else:
        raise FileNotFoundError(f"Neither {baseline_db_path} nor {json_export_path} found!")

    audit19_map = {(r['record_id'], r['entity_type'], r['field_name']): r for r in audit19_rows}
    assert len(audit19_map) == 366, f"Expected 366 unique Audit 19 keys, got {len(audit19_map)}"

    # 2. Read active / backup records from database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM enrichment_audit_log")
    active_rows = [dict(r) for r in c.fetchall()]

    c.execute("SELECT * FROM enrichment_audit_log_backup_20261122_054906")
    backup_rows = [dict(r) for r in c.fetchall()]

    conn.close()

    active_map = {(r['record_id'], r['entity_type'], r['field_name']): r for r in active_rows}
    backup_map = {(r['record_id'], r['entity_type'], r['field_name']): r for r in backup_rows}

    # Combined active keys
    active_keys = set(active_map.keys()) | set(backup_map.keys())

    # 3. Exact Key Matching (Audit 24 Requirement)
    surviving_keys = set(audit19_map.keys()) & active_keys
    missing_keys = set(audit19_map.keys()) - active_keys
    post_audit19_keys = active_keys - set(audit19_map.keys())

    print(f"Audit 19 original records: {len(audit19_map)}")
    print(f"Surviving keys in active/backup: {len(surviving_keys)}")
    print(f"Restored keys missing from active/backup: {len(missing_keys)}")
    print(f"Post-Audit 19 additions: {len(post_audit19_keys)}")

    assert len(surviving_keys) == 42, f"Expected 42 surviving keys, got {len(surviving_keys)}"
    assert len(missing_keys) == 324, f"Expected 324 missing keys, got {len(missing_keys)}"
    assert len(post_audit19_keys) == 24, f"Expected 24 post-Audit 19 keys, got {len(post_audit19_keys)}"

    # 4. Generate Reconciliation Records
    reconciliation_rows = []
    row_num = 1

    # Surviving 42 records
    for k in sorted(surviving_keys):
        r19 = audit19_map[k]
        ract = active_map.get(k) or backup_map.get(k)
        reconciliation_rows.append({
            "row_number": row_num,
            "record_id": k[0],
            "entity_type": k[1],
            "field_name": k[2],
            "recovery_status": "RECOVERED_IN_AUDIT_22_AND_23",
            "audit19_enriched_value": json.dumps(r19['enriched_value'], ensure_ascii=False) if isinstance(r19['enriched_value'], (list, dict)) else str(r19['enriched_value']),
            "active_enriched_value": str(ract.get('enriched_value')),
            "audit19_validation_status": r19['validation_status'],
            "active_validation_status": str(ract.get('validation_status')),
            "source_url": r19.get('source_url', ''),
            "notes": "Exact Audit 19 key surviving and preserved in active/backup SQLite tables."
        })
        row_num += 1

    # Restored 324 records
    for k in sorted(missing_keys):
        r19 = audit19_map[k]
        reconciliation_rows.append({
            "row_number": row_num,
            "record_id": k[0],
            "entity_type": k[1],
            "field_name": k[2],
            "recovery_status": "RESTORED_FROM_AUDIT_19_SOURCE",
            "audit19_enriched_value": json.dumps(r19['enriched_value'], ensure_ascii=False) if isinstance(r19['enriched_value'], (list, dict)) else str(r19['enriched_value']),
            "active_enriched_value": "NOT_PRESENT_IN_ACTIVE_TABLES",
            "audit19_validation_status": r19['validation_status'],
            "active_validation_status": "N/A",
            "source_url": r19.get('source_url', ''),
            "notes": "Original Audit 19 record recovered and restored into audit19_enrichment_audit_log_archive."
        })
        row_num += 1

    # Post-Audit 19 additions (24)
    for k in sorted(post_audit19_keys):
        ract = active_map.get(k) or backup_map.get(k)
        reconciliation_rows.append({
            "row_number": row_num,
            "record_id": k[0],
            "entity_type": k[1],
            "field_name": k[2],
            "recovery_status": "ADDED_POST_AUDIT_19",
            "audit19_enriched_value": "NOT_PRESENT_IN_AUDIT_19",
            "active_enriched_value": str(ract.get('enriched_value')),
            "audit19_validation_status": "N/A",
            "active_validation_status": str(ract.get('validation_status')),
            "source_url": str(ract.get('source_url', '')),
            "notes": "Record added in subsequent audit iterations (Audit 21/22/23)."
        })
        row_num += 1

    # Write CSV
    os.makedirs(os.path.dirname(csv_output_path), exist_ok=True)
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "row_number", "record_id", "entity_type", "field_name", "recovery_status",
            "audit19_enriched_value", "active_enriched_value",
            "audit19_validation_status", "active_validation_status",
            "source_url", "notes"
        ])
        writer.writeheader()
        writer.writerows(reconciliation_rows)

    print(f"Successfully generated {csv_output_path} with {len(reconciliation_rows)} rows.")

    # Write JSON export if needed
    with open(json_export_path, 'w', encoding='utf-8') as f:
        json.dump(audit19_rows, f, indent=2, ensure_ascii=False)
    print(f"Successfully exported {json_export_path} with {len(audit19_rows)} records.")


if __name__ == "__main__":
    reconcile()
