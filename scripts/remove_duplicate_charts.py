import sys
import os

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_ROOT)

from core.google_sheets_client import load_existing_credentials, get_sheets_service, DEFAULT_TOKEN_FILE
from core.sheets_sync_engine import load_sheets_config, execute_with_backoff

DUPLICATE_CHART_IDS = [
    576801750,   # AI Job Vacancies by Taxonomy Category (Duplicate)
    897190859,   # AI Startup Domain & Focus Area Distribution (Duplicate)
    528227414,   # Vacancy Verification & Lifecycle Status Distribution (Duplicate)
    882946069,   # Research Paper Domain Category Distribution (Duplicate)
    1871879945,  # Commercial AI Product Categories (Duplicate)
    1707375572   # AI News Editorial Category Distribution (Duplicate)
]

INTENDED_CHART_IDS = [
    95220720,    # AI Job Vacancies by Taxonomy Category
    1823106458,  # AI Startup Domain & Focus Area Distribution
    1057234590,  # Vacancy Verification & Lifecycle Status Distribution
    329083026,   # Research Paper Domain Category Distribution
    1272405867,  # Commercial AI Product Categories
    2083097885   # AI News Editorial Category Distribution
]

def main():
    cfg = load_sheets_config()
    ss_id = cfg['spreadsheet_id']
    service = get_sheets_service(load_existing_credentials(DEFAULT_TOKEN_FILE))

    print(f"Target Spreadsheet: {ss_id}")
    print(f"Deleting {len(DUPLICATE_CHART_IDS)} duplicate chart objects: {DUPLICATE_CHART_IDS}...")

    requests = [{"deleteEmbeddedObject": {"objectId": cid}} for cid in DUPLICATE_CHART_IDS]
    body = {"requests": requests}

    res = execute_with_backoff(lambda: service.spreadsheets().batchUpdate(
        spreadsheetId=ss_id,
        body=body
    ).execute())

    print("BatchUpdate delete response:", res)

    # Verify remaining charts
    meta = execute_with_backoff(lambda: service.spreadsheets().get(
        spreadsheetId=ss_id,
        ranges=["Dashboard"],
        fields="sheets(properties,charts)"
    ).execute())

    remaining_charts = meta["sheets"][0].get("charts", [])
    print(f"\nTotal Charts Remaining on Dashboard: {len(remaining_charts)}")
    assert len(remaining_charts) == 6, f"Expected exactly 6 charts, got {len(remaining_charts)}"

    remaining_ids = []
    print("\nRemaining Intended Charts:")
    for i, c in enumerate(remaining_charts):
        cid = c.get("chartId")
        title = c.get("spec", {}).get("title")
        remaining_ids.append(cid)
        print(f"  Chart #{i+1} [ID: {cid}]: {title}")

    assert sorted(remaining_ids) == sorted(INTENDED_CHART_IDS), f"Remaining IDs {remaining_ids} != intended {INTENDED_CHART_IDS}"
    print("\nSUCCESS: All 6 duplicate charts removed. Exactly 6 intended charts remain intact.")

if __name__ == "__main__":
    main()
