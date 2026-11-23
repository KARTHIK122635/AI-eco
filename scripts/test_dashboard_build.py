import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.google_sheets_client import load_existing_credentials, get_sheets_service
from core.sheets_sync_engine import load_sheets_config
from core.sheets_dashboard_builder import build_executive_dashboard

cfg = load_sheets_config()
ss_id = cfg.get("spreadsheet_id")
sheet_id_map = cfg.get("sheet_ids", {})
dash_id = sheet_id_map.get("Dashboard")

creds = load_existing_credentials("secrets/google_sheets_token.json")
service = get_sheets_service(creds)

print("Building executive dashboard on sheet ID:", dash_id)
res = build_executive_dashboard(service, ss_id, dash_id)
print("Result:", res)
