"""
Master CLI Script for Phase IV Google Sheets Integration.
Coordinates Stage 1 through Stage 10 adhering to user approval gates.
"""

import sys
import os
import argparse
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.google_sheets_client import (
    SCOPES,
    DEFAULT_CLIENT_SECRETS_FILE,
    DEFAULT_TOKEN_FILE,
    load_existing_credentials,
    get_sheets_service,
    check_connectivity,
)
from core.sheets_transformer import extract_and_transform_dataset, WORKSHEET_COLUMNS
from core.sheets_sync_engine import (
    SHEET_LIST,
    load_sheets_config,
    save_sheets_config,
    create_ecosystem_spreadsheet,
    sync_all_data,
    verify_spreadsheet_contents,
)
from core.sheets_dashboard_builder import build_executive_dashboard

CANDIDATE_DB = os.path.join("data", "working", "candidate_rolling_ai_ecosystem.db")


def preview_stage():
    print("=" * 80)
    print("PHASE IV — COMPLETE GOOGLE SHEETS INTEGRATION PREVIEW")
    print("=" * 80)

    # 1. Verify Authentication & Token
    creds = load_existing_credentials(DEFAULT_TOKEN_FILE)
    if not creds or not creds.valid:
        print("[ERROR] Valid Google OAuth credentials not found in secrets/!")
        return False

    service = get_sheets_service(creds)
    conn = check_connectivity(service)
    print(f"Google Cloud Auth Status   : VALID & AUTHENTICATED")
    print(f"API Connectivity Check     : {conn.get('status')} (HTTP {conn.get('http_status')})")
    print(f"Authorized Scopes          : {creds.scopes}")

    # 2. Database Extraction Preview
    data = extract_and_transform_dataset(CANDIDATE_DB)
    print("\nCandidate Database Extraction Summary:")
    print(f"{'Sheet Name':<22} | {'Rows':<8} | {'Columns':<8} | {'Eligible 6M':<12} | {'Fresh 24H':<10}")
    print("-" * 72)
    tot_rows = 0
    tot_6m = 0
    tot_24h = 0
    for s_name, s_info in data.items():
        tot_rows += s_info["total_extracted"]
        tot_6m += s_info["eligible_6m_count"]
        tot_24h += s_info["fresh_24h_count"]
        print(f"{s_name:<22} | {s_info['total_extracted']:>7}  | {len(s_info['columns']):>7}  | {s_info['eligible_6m_count']:>11}  | {s_info['fresh_24h_count']:>9}")
    print("-" * 72)
    print(f"{'TOTAL CORE DATA':<22} | {tot_rows:>7}  | {'-':>7}  | {tot_6m:>11}  | {tot_24h:>9}")

    print("\nProposed Google Spreadsheet Structure:")
    print(f"Target Title: AI Ecosystem Intelligence Dashboard")
    print(f"Total Worksheets (11):")
    for i, s in enumerate(SHEET_LIST, 1):
        desc = "Operational Data Tab"
        if s == "Dashboard":
            desc = "Executive KPI Cards & Distribution Visualizations"
        elif s == "Sync_Log":
            desc = "Real-time Synchronization Audit Telemetry"
        elif s == "Data_Dictionary":
            desc = "Comprehensive Schema & Business Rule Metadata Catalog"
        print(f"  {i:>2}. {s:<22} : {desc}")

    print("\nReady for Approval Gate 1: Spreadsheet Creation.")
    return True


def create_spreadsheet_stage():
    print("=" * 80)
    print("PHASE IV — STAGE 2: CREATING GOOGLE SPREADSHEET")
    print("=" * 80)
    creds = load_existing_credentials(DEFAULT_TOKEN_FILE)
    if not creds or not creds.valid:
        print("[ERROR] Credentials invalid or expired.")
        return False

    service = get_sheets_service(creds)
    ss_id, ss_url, sheet_id_map = create_ecosystem_spreadsheet(service)
    print(f"[SUCCESS] Spreadsheet created successfully!")
    print(f"Spreadsheet ID  : {ss_id}")
    print(f"Spreadsheet URL : {ss_url}")
    print(f"Worksheets Initialized ({len(sheet_id_map)}): {list(sheet_id_map.keys())}")
    return True


def approved_sync_stage():
    print("=" * 80)
    print("PHASE IV — STAGE 5: EXECUTING APPROVED SYNCHRONIZATION")
    print("=" * 80)
    cfg = load_sheets_config()
    ss_id = cfg.get("spreadsheet_id")
    sheet_id_map = cfg.get("sheet_ids", {})

    if not ss_id:
        print("[ERROR] Spreadsheet ID not found in config! Run create_spreadsheet first.")
        return False

    creds = load_existing_credentials(DEFAULT_TOKEN_FILE)
    service = get_sheets_service(creds)

    print(f"Target Spreadsheet ID : {ss_id}")
    print(f"Starting batch synchronization of 11 worksheets...")

    summary = sync_all_data(
        service=service,
        spreadsheet_id=ss_id,
        sheet_id_map=sheet_id_map,
        candidate_db_path=CANDIDATE_DB,
        batch_size=500
    )

    print("\nSynchronization Summary:")
    print(f"Sync ID         : {summary['sync_id']}")
    print(f"Status          : {summary['status']}")
    print(f"Total Rows      : {summary['total_records_synced']}")
    print(f"API Batches     : {summary['api_batches']}")
    print(f"Duration        : {summary['duration_seconds']}s")
    for s_name, s_info in summary["sheets_synced"].items():
        print(f"  - {s_name:<22}: {s_info['rows']} rows in {s_info['batches']} batches")
    return True


def build_dashboard_stage():
    print("=" * 80)
    print("PHASE IV — STAGE 6 & 7: BUILDING EXECUTIVE DASHBOARD & CHARTS")
    print("=" * 80)
    cfg = load_sheets_config()
    ss_id = cfg.get("spreadsheet_id")
    sheet_id_map = cfg.get("sheet_ids", {})
    dash_id = sheet_id_map.get("Dashboard")

    if not ss_id or dash_id is None:
        print("[ERROR] Spreadsheet ID or Dashboard sheet ID not found in config!")
        return False

    creds = load_existing_credentials(DEFAULT_TOKEN_FILE)
    service = get_sheets_service(creds)

    res = build_executive_dashboard(service, ss_id, dash_id)
    print(f"[SUCCESS] Dashboard configured: {res}")
    return True


def verify_stage():
    print("=" * 80)
    print("PHASE IV — STAGE 8: VERIFYING SPREADSHEET CONTENTS AGAINST DATABASE")
    print("=" * 80)
    cfg = load_sheets_config()
    ss_id = cfg.get("spreadsheet_id")
    if not ss_id:
        print("[ERROR] Spreadsheet ID not found in config!")
        return False

    creds = load_existing_credentials(DEFAULT_TOKEN_FILE)
    service = get_sheets_service(creds)

    res = verify_spreadsheet_contents(service, ss_id, CANDIDATE_DB)
    print(f"Verification Status: {res['status']}")
    print(f"{'Sheet Name':<22} | {'Expected':<10} | {'Actual':<10} | {'Status':<10}")
    print("-" * 60)
    for s_name, s_info in res["sheets"].items():
        status = "MATCH" if s_info["matched"] else "MISMATCH"
        print(f"{s_name:<22} | {s_info['expected_count']:>9}  | {s_info['actual_count']:>9}  | {status:<10}")
    return res["status"] == "PASSED"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="preview", choices=["preview", "create_spreadsheet", "dry_run_sync", "approved_sync", "build_dashboard", "verify"])
    args = parser.parse_args()

    if args.mode == "preview":
        ok = preview_stage()
    elif args.mode == "create_spreadsheet":
        ok = create_spreadsheet_stage()
    elif args.mode == "dry_run_sync":
        ok = preview_stage()
    elif args.mode == "approved_sync":
        ok = approved_sync_stage()
    elif args.mode == "build_dashboard":
        ok = build_dashboard_stage()
    elif args.mode == "verify":
        ok = verify_stage()
    else:
        ok = False

    sys.exit(0 if ok else 1)
