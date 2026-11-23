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
        pos = c.get("position", {})
        print(f"Chart #{i+1} [ID: {cid}]: {title}")
        print(f"  Spec: {json.dumps(spec, indent=2)[:300]}...")
        print(f"  Position: {pos}\n")

if __name__ == "__main__":
    main()
