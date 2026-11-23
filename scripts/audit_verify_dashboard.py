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

    print("=" * 80)
    print("DASHBOARD FORMULA & VALUE AUDIT")
    print(f"Spreadsheet ID: {ss_id}")
    print("=" * 80)

    # 1. Read KPI formulas and evaluated values
    res_formulas = service.spreadsheets().values().get(
        spreadsheetId=ss_id,
        range="Dashboard!A4:J5",
        valueRenderOption="FORMULA"
    ).execute()
    
    res_values = service.spreadsheets().values().get(
        spreadsheetId=ss_id,
        range="Dashboard!A4:J5",
        valueRenderOption="FORMATTED_VALUE"
    ).execute()

    headers = res_values.get("values", [[]])[0]
    formulas = res_formulas.get("values", [[], []])[1]
    values = res_values.get("values", [[], []])[1]

    expected_kpis = {
        "Total Startups": "1,307",
        "Total Products": "1,316",
        "Total Research Papers": "1,060",
        "Total AI News": "1,138",
        "Total AI Jobs": "1,963",
        "Six-Month Eligible Content": "3,302",
        "Fresh Content (24 Hours)": "15",
        "Tracked GitHub Repositories": "190",
        "GitHub Metric Snapshots": "205",
        "Pipeline Collection Runs": "6"
    }

    print("\n--- KPI Cards Verification ---")
    all_kpi_match = True
    for h, f, v in zip(headers, formulas, values):
        exp = expected_kpis.get(h, "<Unknown>")
        # Normalize v to remove commas or compare directly
        matched = (v.replace(",", "") == exp.replace(",", ""))
        if not matched:
            all_kpi_match = False
        print(f"  {h:<30}: Evaluated={v:<8} (Expected={exp:<8}, Match={matched})")
        print(f"    Formula: {f}")

    print(f"\nAll 10 KPI Cards Match Expected Baseline: {all_kpi_match}")

    # 2. Check for formula errors across the entire Dashboard sheet
    print("\n--- Scanning Entire Dashboard Sheet for Formula Errors ---")
    res_dash_all = service.spreadsheets().values().get(
        spreadsheetId=ss_id,
        range="Dashboard!A1:Z60",
        valueRenderOption="FORMATTED_VALUE"
    ).execute()
    dash_rows = res_dash_all.get("values", [])
    
    error_tokens = ["#ERROR!", "#REF!", "#VALUE!", "#N/A", "#DIV/0!", "#NAME?"]
    detected_errors = []
    for r_idx, row in enumerate(dash_rows):
        for c_idx, cell in enumerate(row):
            if any(err in str(cell) for err in error_tokens):
                col_letter = chr(65 + c_idx)
                detected_errors.append(f"Cell {col_letter}{r_idx+1}: {cell}")

    if detected_errors:
        print(f"  Detected {len(detected_errors)} errors on Dashboard:")
        for err in detected_errors:
            print(f"    {err}")
    else:
        print("  Zero formula errors detected on Dashboard! All cells evaluate cleanly.")

    # 3. Read metadata of all Charts on Dashboard
    print("\n--- Auditing Native Google Charts ---")
    meta = service.spreadsheets().get(
        spreadsheetId=ss_id,
        ranges=["Dashboard"],
        fields="sheets(properties,charts)"
    ).execute()

    charts = meta["sheets"][0].get("charts", [])
    print(f"Total Native Charts Configured on Dashboard: {len(charts)}")

    for i, c in enumerate(charts):
        cid = c.get("chartId")
        spec = c.get("spec", {})
        title = spec.get("title", "<No Title>")
        chart_type = ""
        source_ranges = []

        if "basicChart" in spec:
            b_spec = spec["basicChart"]
            chart_type = b_spec.get("chartType")
            legend = b_spec.get("legendPosition")
            for dom in b_spec.get("domains", []):
                src = dom.get("domain", {}).get("sourceRange", {})
                source_ranges.append(f"Domain: SheetId {src.get('sheetId')}, Rows {src.get('startRowIndex')}:{src.get('endRowIndex')}, Cols {src.get('startColumnIndex')}:{src.get('endColumnIndex')}")
            for ser in b_spec.get("series", []):
                src = ser.get("series", {}).get("sourceRange", {})
                source_ranges.append(f"Series: SheetId {src.get('sheetId')}, Rows {src.get('startRowIndex')}:{src.get('endRowIndex')}, Cols {src.get('startColumnIndex')}:{src.get('endColumnIndex')}")
        elif "pieChart" in spec:
            p_spec = spec["pieChart"]
            chart_type = f"PIE ({p_spec.get('pieHole', 0)})"
            legend = p_spec.get("legendPosition")
            dom_src = p_spec.get("domain", {}).get("sourceRange", {})
            ser_src = p_spec.get("series", {}).get("sourceRange", {})
            source_ranges.append(f"Domain: SheetId {dom_src.get('sheetId')}, Rows {dom_src.get('startRowIndex')}:{dom_src.get('endRowIndex')}, Cols {dom_src.get('startColumnIndex')}:{dom_src.get('endColumnIndex')}")
            source_ranges.append(f"Series: SheetId {ser_src.get('sheetId')}, Rows {ser_src.get('startRowIndex')}:{ser_src.get('endRowIndex')}, Cols {ser_src.get('startColumnIndex')}:{ser_src.get('endColumnIndex')}")

        print(f"\n  Chart #{i+1} (ID: {cid}): \"{title}\"")
        print(f"    Type: {chart_type}, Legend: {legend}")
        for sr in source_ranges:
            print(f"    Source Range: {sr}")

    # 4. Check Query Tables on Dashboard
    print("\n--- Auditing Dynamic Query Tables on Dashboard ---")
    query_cells = [
        ("AI Job Vacancies by Taxonomy", "Dashboard!A8"),
        ("AI Startups by Focus Domain", "Dashboard!E8"),
        ("Vacancy Verification Lifecycle", "Dashboard!I8"),
        ("Research Papers by Domain", "Dashboard!M8"),
        ("Commercial Products by Task", "Dashboard!Q8"),
        ("AI News by Editorial Category", "Dashboard!U8"),
    ]
    for label, cell in query_cells:
        q_form = service.spreadsheets().values().get(
            spreadsheetId=ss_id,
            range=cell,
            valueRenderOption="FORMULA"
        ).execute().get("values", [[""]])[0][0]
        q_val = service.spreadsheets().values().get(
            spreadsheetId=ss_id,
            range=cell,
            valueRenderOption="FORMATTED_VALUE"
        ).execute().get("values", [[""]])[0][0]
        print(f"  {label:<35} at {cell}: Evaluated=\"{q_val}\"")
        print(f"    Formula: {q_form}")

if __name__ == "__main__":
    main()
