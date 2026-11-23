"""
scripts/inspect_phase6_sheets.py
================================
Read-only inspection script for Phase VI Google Sheets Dashboard Integration.
Inspects existing worksheets, headers, dimensions, and charts without writing anything.
"""

import os
import sys
import json

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.google_sheets_client import load_existing_credentials, get_sheets_service

SPREADSHEET_ID = "194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI"

def main():
    creds = load_existing_credentials()
    if not creds or not creds.valid:
        print("[ERROR] Credentials not found or invalid.")
        sys.exit(1)

    service = get_sheets_service(creds)
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID, includeGridData=False).execute()

    print("=" * 80)
    print("SPREADSHEET INSPECTION REPORT")
    print("=" * 80)
    print("Title:          ", meta.get("properties", {}).get("title"))
    print("Spreadsheet ID: ", SPREADSHEET_ID)
    print("Locale:         ", meta.get("properties", {}).get("locale"))
    print("Time Zone:      ", meta.get("properties", {}).get("timeZone"))
    print("\nWorksheets & Charts:")

    sheet_names = []
    for s in meta.get("sheets", []):
        props = s.get("properties", {})
        title = props.get("title")
        sheet_id = props.get("sheetId")
        grid = props.get("gridProperties", {})
        charts = s.get("charts", [])
        sheet_names.append(title)
        print(f"  - Sheet ID {sheet_id:>10}: '{title}' | Rows: {grid.get('rowCount'):>5}, Cols: {grid.get('columnCount'):>3} | Charts: {len(charts)}")
        for c in charts:
            spec = c.get("spec", {})
            print(f"      * Chart ID {c.get('chartId')}: '{spec.get('title')}' (Type: {spec.get('basicChart', {}).get('chartType')})")

    # Now inspect header rows of each sheet (row 1 only)
    print("\n" + "=" * 80)
    print("WORKSHEET HEADERS (Row 1)")
    print("=" * 80)

    # Batch get row 1 for all sheets
    ranges = [f"'{name}'!1:1" for name in sheet_names]
    resp = service.spreadsheets().values().batchGet(
        spreadsheetId=SPREADSHEET_ID,
        ranges=ranges
    ).execute()

    headers_by_sheet = {}
    for vr in resp.get("valueRanges", []):
        r_str = vr.get("range", "")
        # Extract sheet title from range string e.g. "'Startups'!A1:Z1"
        s_title = r_str.split("!")[0].strip("'")
        rows = vr.get("values", [])
        hdr = rows[0] if rows else []
        headers_by_sheet[s_title] = hdr
        print(f"\nSheet '{s_title}' ({len(hdr)} columns):")
        for idx, col in enumerate(hdr):
            print(f"    Col {idx+1:>2}: {col}")

    # Also inspect Dashboard sheet cells to see layout
    print("\n" + "=" * 80)
    print("DASHBOARD LAYOUT INSPECTION (A1:N35)")
    print("=" * 80)
    dash_resp = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'Dashboard'!A1:N35",
        valueRenderOption="FORMULA"
    ).execute()
    dash_rows = dash_resp.get("values", [])
    for r_idx, row in enumerate(dash_rows):
        non_empty = [(c_idx, val) for c_idx, val in enumerate(row) if val]
        if non_empty:
            cells_str = ", ".join(f"[{chr(65+c)}={v}]" if c < 26 else f"[Col{c+1}={v}]" for c, v in non_empty)
            print(f"Row {r_idx+1:>2}: {cells_str}")

    # Inspect Sync_Log
    print("\n" + "=" * 80)
    print("SYNC LOG INSPECTION (A1:J10)")
    print("=" * 80)
    sync_resp = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'Sync_Log'!A1:J10"
    ).execute()
    for r in sync_resp.get("values", []):
        print(r)

if __name__ == "__main__":
    main()
