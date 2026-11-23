import sys
import os
import json

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_ROOT)

from core.google_sheets_client import load_existing_credentials, get_sheets_service, DEFAULT_TOKEN_FILE
from core.sheets_sync_engine import load_sheets_config

def main():
    cfg = load_sheets_config()
    ss_id = cfg['spreadsheet_id']
    service = get_sheets_service(load_existing_credentials(DEFAULT_TOKEN_FILE))

    print(f"Spreadsheet ID: {ss_id}\n")

    # 1. Inspect Data_Dictionary!G1:G3
    print("--- 1. Inspect Data_Dictionary Row 2 (Provenance_or_Formula) ---")
    res_f = service.spreadsheets().values().get(
        spreadsheetId=ss_id,
        range="Data_Dictionary!A1:H3",
        valueRenderOption="FORMULA"
    ).execute()
    res_v = service.spreadsheets().values().get(
        spreadsheetId=ss_id,
        range="Data_Dictionary!A1:H3",
        valueRenderOption="FORMATTED_VALUE"
    ).execute()

    f_vals = res_f.get("values", [])
    v_vals = res_v.get("values", [])

    print("Headers:", v_vals[0] if v_vals else [])
    print("Row 2 (Formulas):", f_vals[1] if len(f_vals) > 1 else [])
    print("Row 2 (Values):", v_vals[1] if len(v_vals) > 1 else [])
    if len(v_vals) > 1 and len(v_vals[0]) > 6:
        col_g_name = v_vals[0][6]
        col_g_f = f_vals[1][6] if len(f_vals[1]) > 6 else ""
        col_g_v = v_vals[1][6] if len(v_vals[1]) > 6 else ""
        print(f"\nCell G2 ({col_g_name}):")
        print(f"  Formula         : {repr(col_g_f)}")
        print(f"  Formatted Value : {repr(col_g_v)}")

    # 2. Inspect Dashboard Charts
    print("\n--- 2. Inspect Dashboard Charts ---")
    meta = service.spreadsheets().get(
        spreadsheetId=ss_id,
        ranges=["Dashboard"],
        fields="sheets(properties,charts)"
    ).execute()

    charts = meta["sheets"][0].get("charts", [])
    print(f"Total Charts on Dashboard: {len(charts)}\n")

    for i, c in enumerate(charts):
        cid = c.get("chartId")
        spec = c.get("spec", {})
        title = spec.get("title", "<No Title>")
        chart_type = ""
        if "basicChart" in spec:
            chart_type = spec["basicChart"].get("chartType")
        elif "pieChart" in spec:
            chart_type = "PIE"
        
        pos = c.get("position", {})
        overlay = pos.get("overlayPosition", {})
        anchor = overlay.get("anchorCell", {})
        anchor_row = anchor.get("rowIndex")
        anchor_col = anchor.get("columnIndex")
        w = overlay.get("widthPixels")
        h = overlay.get("heightPixels")

        print(f"Chart #{i+1}:")
        print(f"  ID        : {cid}")
        print(f"  Title     : {title}")
        print(f"  Type      : {chart_type}")
        print(f"  Anchor    : Row {anchor_row}, Col {anchor_col} (Size: {w}x{h})")

if __name__ == "__main__":
    main()
