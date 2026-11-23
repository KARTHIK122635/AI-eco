import sys
import os

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_ROOT)

from core.google_sheets_client import load_existing_credentials, get_sheets_service, DEFAULT_TOKEN_FILE
from core.sheets_sync_engine import load_sheets_config

def main():
    cfg = load_sheets_config()
    ss_id = cfg['spreadsheet_id']
    service = get_sheets_service(load_existing_credentials(DEFAULT_TOKEN_FILE))

    print("=== DASHBOARD ROWS 7-20 INSPECTION ===")
    res_f = service.spreadsheets().values().get(spreadsheetId=ss_id, range="Dashboard!A7:X20", valueRenderOption="FORMULA").execute()
    res_v = service.spreadsheets().values().get(spreadsheetId=ss_id, range="Dashboard!A7:X20", valueRenderOption="FORMATTED_VALUE").execute()

    f_rows = res_f.get("values", [])
    v_rows = res_v.get("values", [])

    for r_idx, (fr, vr) in enumerate(zip(f_rows, v_rows)):
        row_num = r_idx + 7
        print(f"\nRow {row_num}:")
        for c_idx in range(min(len(fr), len(vr))):
            f_val = fr[c_idx] if c_idx < len(fr) else ""
            v_val = vr[c_idx] if c_idx < len(vr) else ""
            if str(f_val).strip() or str(v_val).strip():
                col_name = chr(65 + c_idx)
                print(f"  {col_name}{row_num}: Val='{v_val}', Formula='{f_val}'")

if __name__ == "__main__":
    main()
