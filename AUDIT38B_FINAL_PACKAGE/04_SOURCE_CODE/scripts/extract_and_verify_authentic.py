import zipfile
import os
import sqlite3
import hashlib
import shutil

print("=== STEP 1: EXTRACTING & VERIFYING AUTHENTIC AUDIT 19 DATABASE ===")

os.makedirs("source", exist_ok=True)
os.makedirs("reports", exist_ok=True)
z = zipfile.ZipFile("audit19_recovery_source_bundle.zip")

# Extract source/audit19_original_database.db
db_bytes = z.read("audit19_recovery_source_bundle/source/audit19_original_database.db")
out_db = "source/audit19_original_database.db"
with open(out_db, "wb") as f:
    f.write(db_bytes)

actual_sha = hashlib.sha256(open(out_db, "rb").read()).hexdigest()
size = os.path.getsize(out_db)
print(f"Extracted {out_db}: size={size}, sha256={actual_sha}")
assert actual_sha == "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d", "Hash mismatch!"
assert size == 20770816, f"Expected size 20770816, got {size}"

# Check SQLite
conn = sqlite3.connect(out_db)
cur = conn.cursor()
cur.execute("PRAGMA integrity_check")
ic = cur.fetchone()[0]
print(f"PRAGMA integrity_check: {ic}")
assert ic == "ok", f"Integrity check failed: {ic}"

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print(f"Tables in authentic Audit 19 DB ({len(tables)}): {tables}")

for canon in ["ai_startups", "ai_products", "ai_research_papers", "ai_news", "ai_jobs"]:
    assert canon in tables, f"Missing canonical table {canon}"
    cnt = cur.execute(f"SELECT COUNT(*) FROM {canon}").fetchone()[0]
    print(f"  {canon}: {cnt} rows")

cur.execute("SELECT COUNT(*) FROM enrichment_audit_log")
rows_count = cur.fetchone()[0]
print(f"Rows in enrichment_audit_log: {rows_count}")
assert rows_count == 366, f"Expected 366 rows, got {rows_count}"

cur.execute("PRAGMA table_info(enrichment_audit_log)")
cols = [r[1] for r in cur.fetchall()]
print(f"Columns in enrichment_audit_log ({len(cols)}): {cols}")
assert len(cols) == 13, f"Expected 13 columns, got {len(cols)}"

# Check NULLs vs empty strings
cur.execute("SELECT COUNT(*) FROM enrichment_audit_log WHERE original_value IS NULL")
print(f"NULL original_value: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM enrichment_audit_log WHERE original_value = ''")
print(f"Empty string original_value: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM enrichment_audit_log WHERE enriched_value IS NULL")
print(f"NULL enriched_value: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM enrichment_audit_log WHERE enriched_value = ''")
print(f"Empty string enriched_value: {cur.fetchone()[0]}")

cur.execute("SELECT DISTINCT enriched_at FROM enrichment_audit_log LIMIT 5")
print(f"Sample enriched_at: {cur.fetchall()}")

conn.close()

# Also extract exports
json_bytes = z.read("audit19_recovery_source_bundle/exports/audit19_enrichment_audit_log_366.json")
with open("reports/audit19_original_366_records.json", "wb") as f:
    f.write(json_bytes)

csv_bytes = z.read("audit19_recovery_source_bundle/exports/audit19_vs_audit23_reconciliation.csv")
with open("reports/audit19_to_audit23_reconciliation.csv", "wb") as f:
    f.write(csv_bytes)

csv_366_bytes = z.read("audit19_recovery_source_bundle/exports/audit19_enrichment_audit_log_366.csv")
with open("reports/audit19_enrichment_audit_log_366.csv", "wb") as f:
    f.write(csv_366_bytes)

# Replace copies across workspace
shutil.copy2("source/audit19_original_database.db", "reports/audit19_original_baseline.db")
shutil.copy2("audit19_recovery_source_bundle.zip", "reports/audit19_recovery_source_bundle.zip")

print("Copied authentic database to reports/audit19_original_baseline.db")
print("Copied authentic recovery bundle to reports/audit19_recovery_source_bundle.zip")
print("=== STEP 1 COMPLETED SUCCESSFULLY ===")
