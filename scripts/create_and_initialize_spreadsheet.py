"""
Phase IV Script: Create Google Spreadsheet and Initialize Header Rows.
Creates 'AI Ecosystem Intelligence Dashboard' with 11 worksheets via Google Sheets API v4.
Initializes header rows (Row 1) with professional navy styling and frozen rows.
Does NOT populate dataset records (rows 2+ remain empty).
Prepares comprehensive synchronization dry-run preview.
"""

import sys
import os
import json
import time

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_ROOT)

from core.google_sheets_client import (
    DEFAULT_TOKEN_FILE,
    load_existing_credentials,
    get_sheets_service,
)
from core.sheets_sync_engine import (
    SHEET_LIST,
    DEFAULT_SPREADSHEET_TITLE,
    SYNC_LOG_COLUMNS,
    create_ecosystem_spreadsheet,
    format_worksheet_headers,
    load_sheets_config,
    save_sheets_config,
    execute_with_backoff,
)
from core.sheets_transformer import (
    get_worksheet_schema,
    TABLE_TO_SHEET_MAP,
    PRIMARY_KEYS,
)
from core.sheets_data_dictionary import DATA_DICTIONARY_COLUMNS

CANDIDATE_DB = os.path.join(WORKSPACE_ROOT, "data", "working", "candidate_rolling_ai_ecosystem.db")


def create_and_initialize():
    print("=" * 85)
    print("PHASE IV — GOOGLE SPREADSHEET CREATION & HEADER INITIALIZATION")
    print("=" * 85)

    # 1. Load Credentials & Build Sheets Service (Sheets API v4 only)
    creds = load_existing_credentials(DEFAULT_TOKEN_FILE)
    if not creds or not creds.valid:
        print("[ERROR] Credentials not found or invalid.")
        return False

    service = get_sheets_service(creds)
    print("[AUTH] Google Sheets API v4 service initialized successfully.")
    print("       (Zero Drive API dependencies used)")

    # 2. Create Spreadsheet with 11 Worksheets
    print(f"\n[CREATE] Creating Google Spreadsheet: '{DEFAULT_SPREADSHEET_TITLE}'...")
    ss_id, ss_url, sheet_id_map = create_ecosystem_spreadsheet(service, DEFAULT_SPREADSHEET_TITLE)
    print(f"[SUCCESS] Spreadsheet created!")
    print(f"  Spreadsheet ID  : {ss_id}")
    print(f"  Spreadsheet URL : {ss_url}")

    # 3. Verify Spreadsheet Metadata via spreadsheets.get
    print("\n[VERIFY] Reading back spreadsheet metadata via spreadsheets.get()...")
    meta = execute_with_backoff(lambda: service.spreadsheets().get(spreadsheetId=ss_id).execute())
    ss_title = meta.get("properties", {}).get("title")
    locale = meta.get("properties", {}).get("locale")
    tz = meta.get("properties", {}).get("timeZone")
    verified_sheets = meta.get("sheets", [])

    print(f"  Verified Title   : {ss_title}")
    print(f"  Locale / TimeZone: {locale} / {tz}")
    print(f"  Worksheet Count  : {len(verified_sheets)}")

    verified_sheet_ids = {}
    for s in verified_sheets:
        props = s.get("properties", {})
        title = props.get("title")
        s_id = props.get("sheetId")
        verified_sheet_ids[title] = s_id
        print(f"    - Worksheet '{title}': Sheet ID = {s_id}")

    assert len(verified_sheets) == 11, f"Expected 11 worksheets, got {len(verified_sheets)}"
    assert ss_title == DEFAULT_SPREADSHEET_TITLE, f"Title mismatch: {ss_title}"

    # 4. Initialize Header Rows (Row 1) for each worksheet
    print("\n[HEADERS] Initializing schema headers & frozen top rows (Rows 2+ remain empty)...")
    schema_map = get_worksheet_schema(CANDIDATE_DB)

    header_definitions = {}
    for tbl, sheet_name in TABLE_TO_SHEET_MAP.items():
        header_definitions[sheet_name] = schema_map[sheet_name]

    header_definitions["Sync_Log"] = SYNC_LOG_COLUMNS
    header_definitions["Data_Dictionary"] = DATA_DICTIONARY_COLUMNS
    header_definitions["Dashboard"] = [
        "AI ECOSYSTEM INTELLIGENCE DASHBOARD", "Subtitle / Telemetry", "Status",
        "KPI_1", "KPI_2", "KPI_3", "KPI_4", "KPI_5", "KPI_6", "KPI_7"
    ]

    for sheet_name, cols in header_definitions.items():
        s_id = verified_sheet_ids.get(sheet_name)
        range_name = f"{sheet_name}!A1"
        body = {"values": [cols]}

        # Write header row
        execute_with_backoff(lambda: service.spreadsheets().values().update(
            spreadsheetId=ss_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute())

        # Apply header styling (dark navy #1B365D, white bold text, frozen row, auto-filter)
        if sheet_name != "Dashboard" and s_id is not None:
            format_worksheet_headers(service, ss_id, s_id, len(cols))

        print(f"  - Initialized header for '{sheet_name}' ({len(cols)} columns, Sheet ID {s_id})")

    # 5. Verify Row 1 Header & Empty Row 2
    print("\n[VERIFY] Verifying that Row 1 contains headers and Row 2+ is completely empty...")
    for sheet_name in SHEET_LIST:
        if sheet_name == "Dashboard":
            continue
        res = execute_with_backoff(lambda: service.spreadsheets().values().get(
            spreadsheetId=ss_id,
            range=f"{sheet_name}!A1:B3"
        ).execute())
        vals = res.get("values", [])
        has_header = len(vals) >= 1
        has_data = len(vals) > 1
        print(f"  {sheet_name:<22}: Header Row 1 Present={has_header}, Data Rows Present={has_data} (0 records populated)")
        assert has_header, f"Header missing on {sheet_name}"
        assert not has_data, f"Data unexpectedly found on {sheet_name} before approved sync!"

    # 6. Save Configuration
    cfg = load_sheets_config()
    cfg["spreadsheet_id"] = ss_id
    cfg["spreadsheet_url"] = ss_url
    cfg["title"] = ss_title
    cfg["sheet_ids"] = verified_sheet_ids
    cfg["created_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cfg["status"] = "SPREADSHEET_CREATED_HEADERS_INITIALIZED"
    save_sheets_config(cfg)
    print(f"\n[CONFIG] Configuration updated at 'config/google_sheets_config.json'.")

    return ss_id, ss_url, verified_sheet_ids

if __name__ == "__main__":
    res = create_and_initialize()
    sys.exit(0 if res else 1)
