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

    print(f"Target Spreadsheet: {ss_id}")
    print("Updating Data_Dictionary!G2 with literal documentation text...")

    # Update using RAW input option so Google Sheets treats it strictly as literal string
    update_res = service.spreadsheets().values().update(
        spreadsheetId=ss_id,
        range="Data_Dictionary!G2",
        valueInputOption="RAW",
        body={"values": [["=COUNTA(), =COUNTIF()"]]}
    ).execute()

    print("Update API response:", update_res)

    # Read back formatted value and formula
    val_res = service.spreadsheets().values().get(
        spreadsheetId=ss_id,
        range="Data_Dictionary!G2",
        valueRenderOption="FORMATTED_VALUE"
    ).execute()

    form_res = service.spreadsheets().values().get(
        spreadsheetId=ss_id,
        range="Data_Dictionary!G2",
        valueRenderOption="FORMULA"
    ).execute()

    display_val = val_res.get("values", [[""]])[0][0]
    formula_val = form_res.get("values", [[""]])[0][0]

    print(f"\nVerification Results for Data_Dictionary!G2:")
    print(f"  Formatted Value: {repr(display_val)}")
    print(f"  Formula Value  : {repr(formula_val)}")

    assert display_val == "=COUNTA(), =COUNTIF()", f"Display value mismatch: {display_val}"
    assert formula_val == "=COUNTA(), =COUNTIF()", f"Formula value mismatch: {formula_val}"
    assert "#ERROR!" not in display_val, f"Error still present in cell: {display_val}"
    print("\nSUCCESS: Data_Dictionary!G2 now displays literal documentation text without error.")

if __name__ == "__main__":
    main()
