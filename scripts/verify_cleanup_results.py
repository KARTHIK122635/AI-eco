import sys
import os
import hashlib
import sqlite3
import subprocess

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_ROOT)

from core.google_sheets_client import load_existing_credentials, get_sheets_service, DEFAULT_TOKEN_FILE
from core.sheets_sync_engine import load_sheets_config, execute_with_backoff

EXPECTED_HASHES = {
    "Canonical DB": ("data/normalized/ai_ecosystem.db", "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d"),
    "Audit19 DB": ("source/audit19_original_database.db", "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"),
    "Baseline Working DB": ("data/working/rolling_ai_ecosystem.db", "cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127"),
    "Candidate DB": ("data/working/candidate_rolling_ai_ecosystem.db", "eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198"),
}

EXPECTED_ROW_COUNTS = {
    "Startups": 1307,
    "Products": 1316,
    "Research_Papers": 1060,
    "AI_News": 1138,
    "AI_Jobs": 1963,
    "GitHub_Repositories": 190,
    "GitHub_Metrics": 205,
    "Collection_Logs": 6,
    "Data_Dictionary": 152,
    "Sync_Log": 2
}

EXPECTED_KPIS = {
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

EXPECTED_CHARTS = {
    95220720: "AI Job Vacancies by Taxonomy Category",
    1823106458: "AI Startup Domain & Focus Area Distribution",
    1057234590: "Vacancy Verification & Lifecycle Status Distribution",
    329083026: "Research Paper Domain Category Distribution",
    1272405867: "Commercial AI Product Categories",
    2083097885: "AI News Editorial Category Distribution"
}

def main():
    cfg = load_sheets_config()
    ss_id = cfg['spreadsheet_id']
    service = get_sheets_service(load_existing_credentials(DEFAULT_TOKEN_FILE))

    print("=" * 80)
    print("PHASE IV POST-CLEANUP FINAL COMPREHENSIVE VERIFICATION")
    print(f"Spreadsheet ID: {ss_id}")
    print("=" * 80)

    # 1. Verify Data_Dictionary!G2
    print("\n[1/6] Verifying Data_Dictionary!G2 literal metadata text...")
    val_res = service.spreadsheets().values().get(spreadsheetId=ss_id, range="Data_Dictionary!G2", valueRenderOption="FORMATTED_VALUE").execute()
    form_res = service.spreadsheets().values().get(spreadsheetId=ss_id, range="Data_Dictionary!G2", valueRenderOption="FORMULA").execute()
    g2_val = val_res.get("values", [[""]])[0][0]
    g2_form = form_res.get("values", [[""]])[0][0]
    print(f"  Formatted Value : {repr(g2_val)}")
    print(f"  Formula Value   : {repr(g2_form)}")
    assert g2_val == "=COUNTA(), =COUNTIF()", f"Data Dictionary value mismatch: {g2_val}"
    assert g2_val != "#ERROR!", f"Data Dictionary still displays error!"
    print("  -> Data_Dictionary!G2 verified: Displays literal text with 0 errors.")

    # 2. Verify Dashboard Charts
    print("\n[2/6] Verifying exactly 6 intended dashboard charts...")
    meta = service.spreadsheets().get(spreadsheetId=ss_id, ranges=["Dashboard"], fields="sheets(properties,charts)").execute()
    charts = meta["sheets"][0].get("charts", [])
    print(f"  Total charts found: {len(charts)}")
    assert len(charts) == 6, f"Expected exactly 6 charts, got {len(charts)}"
    for c in charts:
        cid = c.get("chartId")
        title = c.get("spec", {}).get("title")
        expected_title = EXPECTED_CHARTS.get(cid)
        print(f"  Chart [ID: {cid:<10}]: \"{title}\" (Match={title == expected_title})")
        assert title == expected_title, f"Chart {cid} title mismatch: {title} != {expected_title}"
    print("  -> All 6 charts match exact intended IDs, titles, and specifications.")

    # 3. Verify All 10 KPI Cards
    print("\n[3/6] Verifying all 10 live KPI values on Dashboard...")
    kpi_res = service.spreadsheets().values().get(spreadsheetId=ss_id, range="Dashboard!A4:J5", valueRenderOption="FORMATTED_VALUE").execute()
    kpi_vals = kpi_res.get("values", [[], []])
    headers = kpi_vals[0]
    values = kpi_vals[1]
    for h, v in zip(headers, values):
        exp = EXPECTED_KPIS.get(h)
        match = (v.replace(",", "") == exp.replace(",", ""))
        print(f"  {h:<30}: Evaluated={v:<8} (Expected={exp:<8}, Match={match})")
        assert match, f"KPI mismatch on {h}: {v} != {exp}"
    print("  -> All 10 KPI card values verified identical.")

    # 4. Verify Dynamic Aggregation Tables
    print("\n[4/6] Verifying all 6 dynamic query aggregation tables on Dashboard...")
    query_checks = [
        ("AI Job Vacancies by Taxonomy", "Dashboard!A9", "NON_TECHNICAL"),
        ("AI Startups by Focus Domain", "Dashboard!D9", "Applied AI & Automation"),
        ("Vacancy Lifecycle Status", "Dashboard!G9", "ACTIVE"),
        ("Research Papers by Domain", "Dashboard!J9", "cs.CV"),
        ("Commercial Products by Task", "Dashboard!M9", "gradio"),
        ("AI News by Editorial Category", "Dashboard!P9", "General AI & Industry")
    ]
    for label, cell, leading_cat in query_checks:
        val = service.spreadsheets().values().get(spreadsheetId=ss_id, range=cell).execute().get("values", [[""]])[0][0]
        print(f"  {label:<32} at {cell}: Leading Category='{val}' (Expected='{leading_cat}')")
        assert val == leading_cat, f"Query table mismatch at {cell}: {val} != {leading_cat}"
    print("  -> All 6 query tables verified live and intact.")

    # 5. Verify All 8 Data Worksheets + Dictionary + Sync Log Row Counts
    print("\n[5/6] Verifying row counts across all data sheets...")
    for sheet_name, exp_rows in EXPECTED_ROW_COUNTS.items():
        res = service.spreadsheets().values().get(spreadsheetId=ss_id, range=f"{sheet_name}!A2:A").execute()
        actual_rows = len(res.get("values", []))
        match = (actual_rows == exp_rows)
        print(f"  {sheet_name:<22}: Rows={actual_rows:>5} (Expected={exp_rows:>5}, Match={match})")
        assert match, f"Row count mismatch on {sheet_name}: {actual_rows} != {exp_rows}"
    print("  -> All data worksheet row counts remain 100% unchanged.")

    # 6. Verify Database Hashes & Protected State
    print("\n[6/6] Verifying database SHA-256 hashes and governance state...")
    for name, (path, exp_hash) in EXPECTED_HASHES.items():
        h = hashlib.sha256()
        with open(os.path.join(WORKSPACE_ROOT, path), "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        actual = h.hexdigest()
        assert actual == exp_hash, f"Hash mismatch on {name}!"
        print(f"  {name:<22}: {actual} (MATCH)")

    # Proposals
    cand_db = os.path.join(WORKSPACE_ROOT, "data", "working", "candidate_rolling_ai_ecosystem.db")
    conn = sqlite3.connect(f"file:{cand_db}?mode=ro", uri=True)
    c = conn.cursor()
    c.execute("SELECT approval_status, count(*) FROM enrichment_proposals GROUP BY approval_status")
    props = c.fetchall()
    assert props == [('PENDING_APPROVAL', 20)], f"Proposals altered: {props}"
    conn.close()
    print("  -> All 20 enrichment proposals remain PENDING_APPROVAL.")

    # Task Scheduler
    sch_res = subprocess.run(['schtasks', '/query', '/fo', 'CSV'], capture_output=True, text=True)
    has_ecosystem = any(k in sch_res.stdout.lower() for k in ['ecosystem', 'rolling_ai', 'ai_daily'])
    assert not has_ecosystem, "Active scheduled tasks detected!"
    print("  -> Windows Task Scheduler remains disabled.")

    print("\n" + "=" * 80)
    print("ALL VERIFICATION CHECKS PASSED — DASHBOARD CLEANUP 100% VERIFIED")
    print("=" * 80)

if __name__ == "__main__":
    main()
