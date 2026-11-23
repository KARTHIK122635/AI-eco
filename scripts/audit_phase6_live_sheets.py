import sys
import os
import json
import sqlite3

sys.path.insert(0, os.path.abspath("."))
from core.google_sheets_client import load_existing_credentials, get_sheets_service

creds = load_existing_credentials()
service = get_sheets_service(creds)
SPREADSHEET_ID = "194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI"

meta = service.spreadsheets().get(
    spreadsheetId=SPREADSHEET_ID,
    includeGridData=False
).execute()

print("=== 1. WORKSHEETS ===")
for s in meta.get("sheets", []):
    props = s["properties"]
    title = props["title"]
    sheet_id = props["sheetId"]
    grid = props.get("gridProperties", {})
    charts = s.get("charts", [])
    print(f"{props.get('index')}: {title:<20} | ID: {sheet_id:<11} | Rows: {grid.get('rowCount'):<5} | Cols: {grid.get('columnCount'):<4} | Charts: {len(charts)}")

print("\n=== 2. CHARTS ===")
for s in meta.get("sheets", []):
    for c in s.get("charts", []):
        cid = c["chartId"]
        spec = c["spec"]
        pos = c.get("position", {})
        anchor = pos.get("overlayPosition", {}).get("anchorCell", {})
        chart_type = spec.get("basicChart", {}).get("chartType") or ("PIE" if "pieChart" in spec else "UNKNOWN")
        print(f"Chart ID: {cid} | Title: '{spec.get('title')}' | Type: {chart_type}")
        print(f"  Anchor: sheetId={anchor.get('sheetId')}, row={anchor.get('rowIndex')}, col={anchor.get('columnIndex')}")
        sources = []
        if "basicChart" in spec:
            bc = spec["basicChart"]
            for domain in bc.get("domains", []):
                sources.append(("domain", domain.get("domain", {}).get("sourceRange", {}).get("sources", [])))
            for series in bc.get("series", []):
                sources.append(("series", series.get("series", {}).get("sourceRange", {}).get("sources", [])))
        elif "pieChart" in spec:
            pc = spec["pieChart"]
            sources.append(("domain", pc.get("domain", {}).get("sourceRange", {}).get("sources", [])))
            sources.append(("series", pc.get("series", {}).get("sourceRange", {}).get("sources", [])))
        print(f"  Sources: {sources}")

print("\n=== 3. DASHBOARD POPULATED ROWS (1 to 65) ===")
dash_res = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range="Dashboard!A1:Z65"
).execute()
dash_vals = dash_res.get("values", [])
print(f"Total populated rows returned on Dashboard: {len(dash_vals)}")
for idx, r in enumerate(dash_vals):
    if any(cell.strip() for cell in r if cell):
        non_empty = [f"{col_name}:{val}" for col_name, val in zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", r) if val.strip()]
        print(f"Row {idx+1}: {non_empty[:6]}")

print("\n=== 4. ROW COUNTS IN LIVE WORKSHEETS ===")
for sname in ["Dashboard", "Startups", "Products", "Research_Papers", "AI_News", "AI_Jobs", "GitHub_Repositories", "GitHub_Metrics", "Collection_Logs", "Sync_Log", "Data_Dictionary"]:
    res = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sname}!A:A"
    ).execute()
    vals = res.get("values", [])
    print(f"{sname:<20}: {len(vals)} populated rows (header + data)")

print("\n=== 5. INVESTIGATE COLLECTION LOGS DISCREPANCY ===")
# Check SQLite collection_logs
conn = sqlite3.connect("file:data/working/phase5_github_candidate.db?mode=ro", uri=True)
c = conn.cursor()
c.execute("SELECT count(*) FROM collection_logs;")
db_coll_count = c.fetchone()[0]
print(f"SQLite phase5_github_candidate.db collection_logs count: {db_coll_count}")
c.execute("SELECT run_id, execution_type, start_time, status FROM collection_logs;")
for r in c.fetchall():
    print(f"  DB Log: {r}")
conn.close()

# Also check other databases for collection_logs
for db_name, db_file in [
    ("Canonical", "data/normalized/ai_ecosystem.db"),
    ("Audit19", "source/audit19_original_database.db"),
    ("Baseline", "data/working/rolling_ai_ecosystem.db"),
    ("Candidate", "data/working/candidate_rolling_ai_ecosystem.db")
]:
    conn_other = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
    c_other = conn_other.cursor()
    try:
        c_other.execute("SELECT count(*) FROM collection_logs;")
        cnt = c_other.fetchone()[0]
        print(f"SQLite {db_name} collection_logs count: {cnt}")
    except Exception as e:
        print(f"SQLite {db_name} collection_logs error: {e}")
    conn_other.close()

# Fetch some rows from live Collection_Logs worksheet to see what is there
coll_res = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range="Collection_Logs!A1:E10"
).execute()
print("\nFirst 10 rows in live Collection_Logs worksheet:")
for r in coll_res.get("values", []):
    print(" ", r)
