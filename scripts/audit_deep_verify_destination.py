import sys
import os
import sqlite3
import json

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_ROOT)

from core.google_sheets_client import load_existing_credentials, get_sheets_service, DEFAULT_TOKEN_FILE
from core.sheets_sync_engine import load_sheets_config
from core.sheets_transformer import (
    extract_and_transform_dataset,
    WORKSHEET_COLUMNS,
    PRIMARY_KEYS,
    TABLE_TO_SHEET_MAP
)
from core.sheets_data_dictionary import DATA_DICTIONARY_ROWS, DATA_DICTIONARY_COLUMNS

CANDIDATE_DB = os.path.join(WORKSPACE_ROOT, "data", "working", "candidate_rolling_ai_ecosystem.db")

def main():
    cfg = load_sheets_config()
    ss_id = cfg['spreadsheet_id']
    creds = load_existing_credentials(DEFAULT_TOKEN_FILE)
    service = get_sheets_service(creds)

    print("=" * 80)
    print("DEEP VERIFICATION OF DESTINATION RECORDS")
    print(f"Spreadsheet ID: {ss_id}")
    print("=" * 80)

    extracted = extract_and_transform_dataset(CANDIDATE_DB)

    audit_summary = {}

    for sheet_name, db_info in extracted.items():
        print(f"\n--- Auditing Worksheet: {sheet_name} ---")
        expected_cols = db_info["columns"]
        expected_rows = db_info["rows"]
        pk_name = db_info["primary_key"]
        expected_count = len(expected_rows)

        # Read back all values from sheet
        res = service.spreadsheets().values().get(
            spreadsheetId=ss_id,
            range=f"{sheet_name}!A1:ZZ"
        ).execute()
        sheet_values = res.get("values", [])

        if not sheet_values:
            print(f"  [ERROR] Worksheet {sheet_name} is completely empty!")
            audit_summary[sheet_name] = {"status": "EMPTY"}
            continue

        sheet_headers = sheet_values[0]
        sheet_data_rows = sheet_values[1:]
        actual_count = len(sheet_data_rows)

        # 1. Header & Column Position Check
        header_match = (sheet_headers == expected_cols)
        header_diff = []
        if not header_match:
            header_diff = [
                f"Pos {i}: expected {ec}, got {sc}" 
                for i, (ec, sc) in enumerate(zip(expected_cols, sheet_headers)) 
                if ec != sc
            ]
            if len(expected_cols) != len(sheet_headers):
                header_diff.append(f"Len diff: expected {len(expected_cols)}, got {len(sheet_headers)}")

        # 2. Primary Key Analysis
        source_pks = [r[0] for r in expected_rows]
        dest_pks = [r[0] if len(r) > 0 else None for r in sheet_data_rows]

        null_pks = sum(1 for pk in dest_pks if pk is None or str(pk).strip() == "")
        dup_pks = len(dest_pks) - len(set(dest_pks))
        missing_pks = set(source_pks) - set(dest_pks)
        extra_pks = set(dest_pks) - set(source_pks)
        order_match = (source_pks == dest_pks)

        # 3. Provenance & Sample Content Verification
        # Sample first row, middle row, last row
        sample_indices = [0, len(expected_rows) // 2, len(expected_rows) - 1]
        sample_checks = []
        cell_truncation_detected = 0

        for idx in sample_indices:
            src_row = expected_rows[idx]
            dst_row = sheet_data_rows[idx] if idx < len(sheet_data_rows) else []
            
            # Pad dst_row with empty strings if trailing empty cells omitted by Sheets API
            padded_dst = dst_row + [""] * (len(src_row) - len(dst_row))
            
            # Compare each cell (as string representation)
            mismatches = []
            for col_idx, (s_val, d_val) in enumerate(zip(src_row, padded_dst)):
                # Normalize types to str
                s_str = "" if s_val is None else str(s_val)
                d_str = "" if d_val is None else str(d_val)
                if s_str != d_str:
                    # check for bool representation e.g. True vs TRUE
                    if s_str.upper() == d_str.upper():
                        continue
                    mismatches.append(f"Col {expected_cols[col_idx]}: src='{s_str[:30]}' != dst='{d_str[:30]}'")
            
            sample_checks.append({
                "row_idx": idx,
                "pk": src_row[0],
                "mismatch_count": len(mismatches),
                "mismatches": mismatches
            })

        # Check for truncation across entire sheet: check if any cell in dst has shorter length than src
        for r_idx, (src_r, dst_r) in enumerate(zip(expected_rows, sheet_data_rows)):
            for c_idx, s_val in enumerate(src_r):
                if s_val is not None and isinstance(s_val, str) and len(s_val) > 100:
                    d_val = dst_r[c_idx] if c_idx < len(dst_r) else ""
                    if len(d_val) < len(s_val):
                        cell_truncation_detected += 1

        print(f"  Rows count            : expected={expected_count}, actual={actual_count} (MATCH={expected_count == actual_count})")
        print(f"  Headers ({len(sheet_headers)} cols) : MATCH={header_match}")
        if header_diff:
            print(f"    Header diffs: {header_diff}")
        print(f"  Primary Keys          : nulls={null_pks}, dups={dup_pks}, missing={len(missing_pks)}, extra={len(extra_pks)}")
        print(f"  Row Order Match       : {order_match}")
        print(f"  Cell Truncations      : {cell_truncation_detected}")
        print(f"  Sample Row Checks     : all sample rows match={all(sc['mismatch_count'] == 0 for sc in sample_checks)}")

        audit_summary[sheet_name] = {
            "expected_count": expected_count,
            "actual_count": actual_count,
            "count_match": (expected_count == actual_count),
            "header_match": header_match,
            "null_pks": null_pks,
            "dup_pks": dup_pks,
            "missing_pks_count": len(missing_pks),
            "extra_pks_count": len(extra_pks),
            "order_match": order_match,
            "cell_truncation_detected": cell_truncation_detected,
            "sample_checks": sample_checks
        }

    # Verify Data_Dictionary
    print("\n--- Auditing Worksheet: Data_Dictionary ---")
    res_dict = service.spreadsheets().values().get(spreadsheetId=ss_id, range="Data_Dictionary!A1:ZZ").execute()
    dict_vals = res_dict.get("values", [])
    dict_headers = dict_vals[0] if dict_vals else []
    dict_rows = dict_vals[1:] if len(dict_vals) > 1 else []
    dict_header_match = (dict_headers == DATA_DICTIONARY_COLUMNS)
    dict_count_match = (len(dict_rows) == len(DATA_DICTIONARY_ROWS))
    print(f"  Headers: match={dict_header_match} (cols={len(dict_headers)})")
    print(f"  Rows: expected={len(DATA_DICTIONARY_ROWS)}, actual={len(dict_rows)} (MATCH={dict_count_match})")
    
    # Check dictionary row content match
    dict_mismatches = 0
    for r_idx, (src_r, dst_r) in enumerate(zip(DATA_DICTIONARY_ROWS, dict_rows)):
        for c_idx, s_val in enumerate(src_r):
            d_val = dst_r[c_idx] if c_idx < len(dst_r) else ""
            if str(s_val) != str(d_val):
                dict_mismatches += 1
    print(f"  Content mismatches across 152 rows: {dict_mismatches}")

    # Verify Sync_Log
    print("\n--- Auditing Worksheet: Sync_Log ---")
    res_log = service.spreadsheets().values().get(spreadsheetId=ss_id, range="Sync_Log!A1:ZZ").execute()
    log_vals = res_log.get("values", [])
    log_headers = log_vals[0] if log_vals else []
    log_rows = log_vals[1:] if len(log_vals) > 1 else []
    print(f"  Headers: cols={len(log_headers)}, {log_headers}")
    print(f"  Total Logged Runs: {len(log_rows)}")
    for i, r in enumerate(log_rows):
        print(f"    Entry {i+1}: ID={r[0]}, Timestamp={r[1]}, Records={r[3]}, Status={r[8]}")

if __name__ == "__main__":
    main()
