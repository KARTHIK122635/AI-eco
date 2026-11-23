import sys
import os
import json

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_ROOT)

from core.google_sheets_client import load_existing_credentials, get_sheets_service, DEFAULT_TOKEN_FILE
from core.sheets_sync_engine import load_sheets_config
from core.sheets_transformer import extract_and_transform_dataset, PRIMARY_KEYS
from core.sheets_data_dictionary import DATA_DICTIONARY_ROWS, DATA_DICTIONARY_COLUMNS

CANDIDATE_DB = os.path.join(WORKSPACE_ROOT, "data", "working", "candidate_rolling_ai_ecosystem.db")

def main():
    cfg = load_sheets_config()
    ss_id = cfg['spreadsheet_id']
    creds = load_existing_credentials(DEFAULT_TOKEN_FILE)
    service = get_sheets_service(creds)
    extracted = extract_and_transform_dataset(CANDIDATE_DB)

    # 1. Investigate GitHub_Metrics PKs
    print("=== INVESTIGATING GITHUB_METRICS PKs ===")
    gh_info = extracted["GitHub_Metrics"]
    src_rows = gh_info["rows"]
    res = service.spreadsheets().values().get(spreadsheetId=ss_id, range="GitHub_Metrics!A1:B10").execute()
    dst_vals = res.get("values", [])
    print("Source GitHub_Metrics cols:", gh_info["columns"])
    print("Source Row 1 (first 5 cols):", src_rows[0][:5])
    print("Dest Row 1 (Header):", dst_vals[0])
    print("Dest Row 2 (Data):", dst_vals[1] if len(dst_vals) > 1 else "None")
    print("Source Row 1 PK type:", type(src_rows[0][0]), repr(src_rows[0][0]))
    print("Dest Row 2 PK type:", type(dst_vals[1][0]), repr(dst_vals[1][0]))

    # 2. Investigate Sample Row mismatches for Startups
    print("\n=== INVESTIGATING SAMPLE MISMATCHES (Startups) ===")
    st_info = extracted["Startups"]
    res_st = service.spreadsheets().values().get(spreadsheetId=ss_id, range="Startups!A1:Z3").execute()
    st_dst = res_st.get("values", [])
    src_r0 = st_info["rows"][0]
    dst_r0 = st_dst[1]
    cols = st_info["columns"]
    for i, (c, s) in enumerate(zip(cols, src_r0)):
        d = dst_r0[i] if i < len(dst_r0) else "<MISSING>"
        if str(s) != str(d):
            print(f"Col {i} ({c}): src={type(s).__name__} '{s}' != dst={type(d).__name__} '{d}'")

    # 3. Investigate AI_Jobs Truncations
    print("\n=== INVESTIGATING AI_JOBS TRUNCATIONS ===")
    jobs_info = extracted["AI_Jobs"]
    res_jobs = service.spreadsheets().values().get(spreadsheetId=ss_id, range="AI_Jobs!A1:AJ1965").execute()
    jobs_dst = res_jobs.get("values", [])
    jobs_src = jobs_info["rows"]
    jobs_cols = jobs_info["columns"]
    trunc_count = 0
    for r_idx, (s_row, d_row) in enumerate(zip(jobs_src, jobs_dst[1:])):
        for c_idx, s_val in enumerate(s_row):
            if s_val is not None and isinstance(s_val, str) and len(s_val) > 100:
                d_val = d_row[c_idx] if c_idx < len(d_row) else ""
                if len(d_val) < len(s_val):
                    trunc_count += 1
                    if trunc_count <= 5:
                        print(f"Truncation #{trunc_count} at Row {r_idx+2}, Col {jobs_cols[c_idx]}:")
                        print(f"  src len={len(s_val)}, dst len={len(d_val)}")
                        print(f"  src tail: {repr(s_val[-40:])}")
                        print(f"  dst tail: {repr(d_val[-40:])}")

    # 4. Investigate Data_Dictionary mismatch
    print("\n=== INVESTIGATING DATA_DICTIONARY MISMATCH ===")
    res_dict = service.spreadsheets().values().get(spreadsheetId=ss_id, range="Data_Dictionary!A1:H160").execute()
    dict_dst = res_dict.get("values", [])[1:]
    for r_idx, (src_r, dst_r) in enumerate(zip(DATA_DICTIONARY_ROWS, dict_dst)):
        for c_idx, (s_val, d_val) in enumerate(zip(src_r, dst_r)):
            if str(s_val) != str(d_val):
                print(f"Dict Row {r_idx+2}, Col {DATA_DICTIONARY_COLUMNS[c_idx]}: src='{s_val}' != dst='{d_val}'")

if __name__ == "__main__":
    main()
