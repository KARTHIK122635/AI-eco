import sqlite3
import csv
import json
import os

def export_all_attempt_ids():
    conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    attempts = {}
    tables_to_check = [
        ('llm_enrichment_logs', 'active_logs'),
        ('llm_enrichment_logs_backup_20261122_054711', 'backup_logs_054711'),
        ('llm_enrichment_logs_backup_20261122_054906', 'backup_logs_054906'),
        ('llm_enrichment_results', 'active_results'),
        ('llm_enrichment_results_backup_20261122_054711', 'backup_results_054711'),
        ('llm_enrichment_results_backup_20261122_054906', 'backup_results_054906'),
        ('llm_review_queue', 'active_queue'),
        ('llm_review_queue_backup_20261122_054711', 'backup_queue_054711'),
        ('llm_review_queue_backup_20261122_054906', 'backup_queue_054906')
    ]

    for tbl, source_tag in tables_to_check:
        try:
            c.execute(f"SELECT * FROM {tbl}")
            for r in c.fetchall():
                d = dict(r)
                att_id = d.get('attempt_id')
                if att_id:
                    if att_id not in attempts:
                        attempts[att_id] = {
                            'attempt_id': att_id,
                            'record_id': d.get('record_id'),
                            'entity_type': d.get('entity_type'),
                            'field_name': d.get('field_name'),
                            'source_version': d.get('source_version'),
                            'attempt_number': d.get('attempt_number', 1),
                            'validation_status': d.get('validation_status'),
                            'provider': d.get('provider', 'offline'),
                            'model': d.get('model', 'heuristic-keyword-v1'),
                            'logged_at': d.get('logged_at') or d.get('created_at') or d.get('queued_at'),
                            'found_in_tables': set()
                        }
                    attempts[att_id]['found_in_tables'].add(tbl)
        except Exception as e:
            print(f"Error reading {tbl}: {e}")

    conn.close()

    print(f"Total unique attempt_ids aggregated: {len(attempts)}")

    os.makedirs('reports', exist_ok=True)
    out_csv = 'reports/all_attempt_ids.csv'
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'attempt_id', 'record_id', 'entity_type', 'field_name', 'source_version',
            'attempt_number', 'validation_status', 'provider', 'model', 'logged_at', 'source_tables'
        ])
        for att_id, info in sorted(attempts.items(), key=lambda x: (x[1]['entity_type'] or '', x[1]['record_id'] or '')):
            writer.writerow([
                info['attempt_id'],
                info['record_id'],
                info['entity_type'],
                info['field_name'],
                info['source_version'],
                info['attempt_number'],
                info['validation_status'],
                info['provider'],
                info['model'],
                info['logged_at'],
                ";".join(sorted(info['found_in_tables']))
            ])
    print(f"Wrote {len(attempts)} attempt records to {out_csv}")

if __name__ == '__main__':
    export_all_attempt_ids()
