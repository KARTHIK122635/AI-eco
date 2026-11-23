import sys
import os
import json

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_ROOT)

from core.google_sheets_client import load_existing_credentials, get_sheets_service, DEFAULT_TOKEN_FILE
from core.sheets_sync_engine import load_sheets_config, SHEET_LIST

def main():
    cfg = load_sheets_config()
    ss_id = cfg['spreadsheet_id']
    creds = load_existing_credentials(DEFAULT_TOKEN_FILE)
    service = get_sheets_service(creds)

    print(f"Auditing Spreadsheet: {ss_id}\n")
    print(f"{'Worksheet':<22} | {'Header (Col A)':<20} | {'Data Rows':<10} | {'Total Non-Empty'}")
    print("-" * 70)

    sheet_counts = {}
    core_total = 0
    grand_total = 0

    core_sheets = [
        "Startups", "Products", "Research_Papers", "AI_News", 
        "AI_Jobs", "GitHub_Repositories", "GitHub_Metrics", "Collection_Logs"
    ]

    for title in SHEET_LIST:
        if title == "Dashboard":
            continue
        res = service.spreadsheets().values().get(spreadsheetId=ss_id, range=f"{title}!A1:A").execute()
        vals = res.get('values', [])
        header = vals[0][0] if len(vals) > 0 else "<EMPTY>"
        data_count = max(0, len(vals) - 1)
        sheet_counts[title] = data_count
        grand_total += data_count
        if title in core_sheets:
            core_total += data_count
        print(f"{title:<22} | {header:<20} | {data_count:<10} | {len(vals)}")

    print("-" * 70)
    print(f"Eight Core Database Worksheets Total : {core_total}")
    print(f"Data_Dictionary Rows                 : {sheet_counts.get('Data_Dictionary', 0)}")
    print(f"Sync_Log Rows                        : {sheet_counts.get('Sync_Log', 0)}")
    print(f"Core + Data_Dictionary Subtotal      : {core_total + sheet_counts.get('Data_Dictionary', 0)}")
    print(f"Grand Total (Core + Dict + Sync_Log) : {grand_total}")

    print("\nReading Sync_Log rows:")
    sync_log_res = service.spreadsheets().values().get(spreadsheetId=ss_id, range="Sync_Log!A1:J10").execute()
    for i, row in enumerate(sync_log_res.get('values', [])):
        print(f"  Row {i+1}: {row}")

if __name__ == "__main__":
    main()
