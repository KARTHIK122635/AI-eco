import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.google_sheets_client import load_existing_credentials, get_sheets_service

creds = load_existing_credentials('secrets/google_sheets_token.json')
service = get_sheets_service(creds)
ss_id = '194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI'
meta = service.spreadsheets().get(spreadsheetId=ss_id).execute()
for s in meta.get('sheets', []):
    props = s.get('properties', {})
    gp = props.get('gridProperties', {})
    t = props.get('title')
    sid = props.get('sheetId')
    rc = gp.get('rowCount')
    cc = gp.get('columnCount')
    print(f"{t:<22}: Sheet ID={sid}, Rows={rc}, Cols={cc}")
