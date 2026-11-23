import sqlite3
import shutil
import hashlib

print("=== STEP 2: SYNCHRONIZING AUDIT19 ARCHIVE TABLE IN ACTIVE DATABASE ===")

db_path = "data/normalized/ai_ecosystem.db"
src_db_path = "source/audit19_original_database.db"

conn_src = sqlite3.connect(src_db_path)
conn_src.row_factory = sqlite3.Row
cur_src = conn_src.cursor()
cur_src.execute("SELECT * FROM enrichment_audit_log")
src_rows = [dict(r) for r in cur_src.fetchall()]
conn_src.close()

assert len(src_rows) == 366, f"Expected 366 rows from source, got {len(src_rows)}"

conn_dst = sqlite3.connect(db_path)
cur_dst = conn_dst.cursor()

# Drop existing archive table and recreate
cur_dst.execute("DROP TABLE IF EXISTS audit19_enrichment_audit_log_archive")
cur_dst.execute("""
CREATE TABLE audit19_enrichment_audit_log_archive (
    record_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    field_name TEXT NOT NULL,
    original_value TEXT,
    enriched_value TEXT,
    source_url TEXT,
    evidence TEXT,
    confidence_score REAL,
    enrichment_method TEXT,
    provider TEXT,
    model TEXT,
    enriched_at TEXT,
    validation_status TEXT,
    PRIMARY KEY (record_id, entity_type, field_name)
)
""")

for r in src_rows:
    cur_dst.execute("""
    INSERT INTO audit19_enrichment_audit_log_archive VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        r['record_id'], r['entity_type'], r['field_name'],
        r['original_value'], r['enriched_value'], r['source_url'],
        r['evidence'], r['confidence_score'], r['enrichment_method'],
        r['provider'], r['model'], r['enriched_at'], r['validation_status']
    ))

conn_dst.commit()

# Verify integrity and count
cur_dst.execute("PRAGMA integrity_check")
ic = cur_dst.fetchone()[0]
print(f"data/normalized/ai_ecosystem.db PRAGMA integrity_check: {ic}")
assert ic == "ok"

cur_dst.execute("SELECT COUNT(*) FROM audit19_enrichment_audit_log_archive")
arch_cnt = cur_dst.fetchone()[0]
print(f"audit19_enrichment_audit_log_archive rows: {arch_cnt}")
assert arch_cnt == 366

# Compare field by field
cur_dst.execute("SELECT * FROM audit19_enrichment_audit_log_archive ORDER BY record_id, entity_type, field_name")
conn_dst.row_factory = sqlite3.Row
cur_dst2 = conn_dst.cursor()
cur_dst2.execute("SELECT * FROM audit19_enrichment_audit_log_archive ORDER BY record_id, entity_type, field_name")
dst_rows = [dict(r) for r in cur_dst2.fetchall()]

conn_src = sqlite3.connect(src_db_path)
conn_src.row_factory = sqlite3.Row
cur_src = conn_src.cursor()
cur_src.execute("SELECT * FROM enrichment_audit_log ORDER BY record_id, entity_type, field_name")
src_rows2 = [dict(r) for r in cur_src.fetchall()]
conn_src.close()
conn_dst.close()

diffs = 0
for s, d in zip(src_rows2, dst_rows):
    for col in s.keys():
        if s[col] != d[col]:
            diffs += 1
print(f"Field-by-field differences between source DB and archive table: {diffs}")
assert diffs == 0, f"Found {diffs} differences!"

# Create reports/audit26_corrected.db
shutil.copy2("data/normalized/ai_ecosystem.db", "reports/audit26_corrected.db")
print("Saved reports/audit26_corrected.db successfully.")
print("=== STEP 2 COMPLETED SUCCESSFULLY ===")
