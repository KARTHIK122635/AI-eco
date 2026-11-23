import sys
import os

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_ROOT)

from core.google_sheets_client import load_existing_credentials, get_sheets_service, DEFAULT_TOKEN_FILE
from core.sheets_sync_engine import load_sheets_config
from core.sheets_transformer import extract_and_transform_dataset

def main():
    cfg = load_sheets_config()
    ss_id = cfg['spreadsheet_id']
    service = get_sheets_service(load_existing_credentials(DEFAULT_TOKEN_FILE))
    extracted = extract_and_transform_dataset('data/working/candidate_rolling_ai_ecosystem.db')

    jobs_src = extracted['AI_Jobs']['rows']
    jobs_cols = extracted['AI_Jobs']['columns']

    check_rows = [1024, 1532, 1586, 1605]
    for r_num in check_rows:
        src_idx = r_num - 2
        res = service.spreadsheets().values().get(spreadsheetId=ss_id, range=f'AI_Jobs!A{r_num}:AJ{r_num}').execute()
        dst_row = res.get('values', [])[0]
        src_row = jobs_src[src_idx]
        for c_idx, (s, d) in enumerate(zip(src_row, dst_row)):
            if isinstance(s, str) and str(s) != str(d):
                starts_quote = s.startswith("'")
                equals_without_quote = (s[1:] == d)
                print(f"Row {r_num}, Col {jobs_cols[c_idx]}:")
                print(f"  src starts with single quote: {starts_quote}")
                print(f"  src[:15]: {repr(s[:15])}")
                print(f"  dst[:15]: {repr(d[:15])}")
                print(f"  src[1:] == dst: {equals_without_quote}")

if __name__ == "__main__":
    main()
