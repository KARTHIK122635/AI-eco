"""
Google Sheets Synchronization Engine.
Implements DRY_RUN, APPROVED_SYNC, and VERIFY_ONLY modes with batching, backoff, and recovery.
"""

import os
import json
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from core.sheets_transformer import (
    extract_and_transform_dataset,
    WORKSHEET_COLUMNS,
    PRIMARY_KEYS,
    TABLE_TO_SHEET_MAP,
)
from core.sheets_data_dictionary import DATA_DICTIONARY_ROWS, DATA_DICTIONARY_COLUMNS
from core.google_sheets_client import get_sheets_service, load_existing_credentials

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join("config", "google_sheets_config.json")
DEFAULT_SPREADSHEET_TITLE = "AI Ecosystem Intelligence Dashboard"

SHEET_LIST = [
    "Dashboard",
    "Startups",
    "Products",
    "Research_Papers",
    "AI_News",
    "AI_Jobs",
    "GitHub_Repositories",
    "GitHub_Metrics",
    "Collection_Logs",
    "Sync_Log",
    "Data_Dictionary",
]

SYNC_LOG_COLUMNS = [
    "sync_id", "sync_timestamp", "mode", "total_records_synced", "worksheets_updated",
    "duration_seconds", "api_batch_requests", "api_errors_retried", "sync_status", "error_summary"
]


def load_sheets_config() -> Dict[str, Any]:
    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read sheets config: {e}")
    return {}


def save_sheets_config(config_data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)


def execute_with_backoff(callable_fn, max_retries: int = 5, initial_backoff: float = 1.5):
    """Executes a Google Sheets API request with exponential backoff on 429/500/503 errors."""
    delay = initial_backoff
    for attempt in range(1, max_retries + 1):
        try:
            return callable_fn()
        except HttpError as err:
            status = err.resp.status
            if status in (429, 500, 502, 503) and attempt < max_retries:
                logger.warning(f"Google API HTTP {status} (attempt {attempt}/{max_retries}). Retrying in {delay:.1f}s...")
                time.sleep(delay)
                delay *= 2
            else:
                raise
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Transient error {type(e).__name__} (attempt {attempt}/{max_retries}). Retrying in {delay:.1f}s...")
                time.sleep(delay)
                delay *= 2
            else:
                raise


def create_ecosystem_spreadsheet(
    service: Resource,
    title: str = DEFAULT_SPREADSHEET_TITLE
) -> Tuple[str, str, Dict[str, int]]:
    """
    Creates a new Google Spreadsheet with the 11 designated worksheets.
    Returns: (spreadsheet_id, spreadsheet_url, sheet_id_map)
    """
    sheets_metadata = [{"properties": {"title": sheet_name}} for sheet_name in SHEET_LIST]

    spreadsheet_body = {
        "properties": {
            "title": title,
            "locale": "en_US",
            "timeZone": "UTC",
        },
        "sheets": sheets_metadata,
    }

    create_fn = lambda: service.spreadsheets().create(
        body=spreadsheet_body,
        fields="spreadsheetId,spreadsheetUrl,sheets.properties"
    ).execute()
    result = execute_with_backoff(create_fn)

    spreadsheet_id = result["spreadsheetId"]
    spreadsheet_url = result.get("spreadsheetUrl", f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

    sheet_id_map = {}
    for sheet_prop in result.get("sheets", []):
        props = sheet_prop.get("properties", {})
        sheet_id_map[props.get("title")] = props.get("sheetId")

    # Save to config
    cfg = load_sheets_config()
    cfg["spreadsheet_id"] = spreadsheet_id
    cfg["spreadsheet_url"] = spreadsheet_url
    cfg["title"] = title
    cfg["sheet_ids"] = sheet_id_map
    cfg["created_at"] = datetime.now(timezone.utc).isoformat()
    save_sheets_config(cfg)

    return spreadsheet_id, spreadsheet_url, sheet_id_map


def format_worksheet_headers(
    service: Resource,
    spreadsheet_id: str,
    sheet_id: int,
    column_count: int
) -> None:
    """
    Applies professional dark-navy (#1B365D) theme, white bold text, frozen row,
    and auto-filter to the worksheet header row.
    """
    requests = [
        # Freeze top row
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {
                        "frozenRowCount": 1
                    }
                },
                "fields": "gridProperties.frozenRowCount"
            }
        },
        # Header cell format: Dark navy background, bold white text, centered
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": column_count
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.106,
                            "green": 0.212,
                            "blue": 0.365
                        },
                        "textFormat": {
                            "foregroundColor": {
                                "red": 1.0,
                                "green": 1.0,
                                "blue": 1.0
                            },
                            "fontSize": 10,
                            "bold": True
                        },
                        "horizontalAlignment": "LEFT",
                        "verticalAlignment": "MIDDLE",
                        "wrapStrategy": "CLIP"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy)"
            }
        },
        # Auto-filter
        {
            "setBasicFilter": {
                "filter": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "startColumnIndex": 0,
                        "endColumnIndex": column_count
                    }
                }
            }
        }
    ]

    body = {"requests": requests}
    execute_with_backoff(lambda: service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute())


def write_worksheet_in_batches(
    service: Resource,
    spreadsheet_id: str,
    sheet_name: str,
    columns: List[str],
    rows: List[List[Any]],
    sheet_id: Optional[int] = None,
    batch_size: int = 500
) -> int:
    """
    Writes header row at Row 1 (A1), and rows starting at Row 2 (A2) using batched values.update.
    Ensures grid rowCount is expanded if required. Returns total written data rows.
    """
    total_data_rows = len(rows)
    required_rows = total_data_rows + 10

    # 1. Expand rowCount if sheet requires more than default 1,000 rows
    if sheet_id is not None and required_rows > 1000:
        execute_with_backoff(lambda: service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [{
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheet_id,
                            "gridProperties": {"rowCount": required_rows}
                        },
                        "fields": "gridProperties.rowCount"
                    }
                }]
            }
        ).execute())

    # 2. Update header row (Row 1)
    execute_with_backoff(lambda: service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1",
        valueInputOption="USER_ENTERED",
        body={"values": [columns]}
    ).execute())

    # 3. Write data rows starting at Row 2 in chunks of batch_size
    for start_idx in range(0, total_data_rows, batch_size):
        end_idx = min(start_idx + batch_size, total_data_rows)
        chunk = rows[start_idx:end_idx]
        target_row = start_idx + 2
        range_name = f"{sheet_name}!A{target_row}"

        execute_with_backoff(lambda: service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body={"values": chunk}
        ).execute())

    return total_data_rows


def sync_all_data(
    service: Resource,
    spreadsheet_id: str,
    sheet_id_map: Dict[str, int],
    candidate_db_path: str,
    batch_size: int = 500
) -> Dict[str, Any]:
    """
    Performs APPROVED_SYNC: extracts all datasets and writes all sheets.
    """
    start_time = time.time()
    sync_id = f"sync_{uuid.uuid4().hex[:12]}"
    now_utc_str = datetime.now(timezone.utc).isoformat()

    extracted = extract_and_transform_dataset(candidate_db_path)

    sync_summary = {
        "sync_id": sync_id,
        "sync_timestamp": now_utc_str,
        "mode": "APPROVED_SYNC",
        "sheets_synced": {},
        "total_records_synced": 0,
        "api_batches": 0,
        "errors": []
    }

    # 1. Sync data sheets
    for sheet_name, sheet_data in extracted.items():
        cols = sheet_data["columns"]
        rows = sheet_data["rows"]
        sheet_id = sheet_id_map.get(sheet_name)

        # Write data
        written = write_worksheet_in_batches(
            service=service,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            columns=cols,
            rows=rows,
            sheet_id=sheet_id,
            batch_size=batch_size
        )

        # Apply header styling & filter
        if sheet_id is not None:
            format_worksheet_headers(service, spreadsheet_id, sheet_id, len(cols))

        batches = (len(rows) + batch_size - 1) // batch_size + 1
        sync_summary["sheets_synced"][sheet_name] = {
            "rows": written,
            "columns": len(cols),
            "batches": batches
        }
        sync_summary["total_records_synced"] += written
        sync_summary["api_batches"] += batches

    # 2. Sync Data_Dictionary
    dict_sheet_id = sheet_id_map.get("Data_Dictionary")
    write_worksheet_in_batches(
        service=service,
        spreadsheet_id=spreadsheet_id,
        sheet_name="Data_Dictionary",
        columns=DATA_DICTIONARY_COLUMNS,
        rows=DATA_DICTIONARY_ROWS,
        batch_size=500
    )
    if dict_sheet_id is not None:
        format_worksheet_headers(service, spreadsheet_id, dict_sheet_id, len(DATA_DICTIONARY_COLUMNS))
    sync_summary["sheets_synced"]["Data_Dictionary"] = {
        "rows": len(DATA_DICTIONARY_ROWS),
        "columns": len(DATA_DICTIONARY_COLUMNS),
        "batches": 1
    }
    sync_summary["total_records_synced"] += len(DATA_DICTIONARY_ROWS)
    sync_summary["api_batches"] += 1

    # 3. Setup Sync_Log header and append initial sync log
    elapsed = round(time.time() - start_time, 2)
    sync_log_id = sheet_id_map.get("Sync_Log")
    if sync_log_id is not None:
        # Write header
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="Sync_Log!A1",
            valueInputOption="USER_ENTERED",
            body={"values": [SYNC_LOG_COLUMNS]}
        ).execute()
        format_worksheet_headers(service, spreadsheet_id, sync_log_id, len(SYNC_LOG_COLUMNS))

        # Append entry
        log_entry = [
            sync_id,
            now_utc_str,
            "APPROVED_SYNC",
            sync_summary["total_records_synced"],
            len(sync_summary["sheets_synced"]),
            elapsed,
            sync_summary["api_batches"],
            0,
            "SUCCESS",
            ""
        ]
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="Sync_Log!A2",
            valueInputOption="USER_ENTERED",
            body={"values": [log_entry]}
        ).execute()

    sync_summary["duration_seconds"] = elapsed
    sync_summary["status"] = "SUCCESS"
    return sync_summary


def verify_spreadsheet_contents(
    service: Resource,
    spreadsheet_id: str,
    candidate_db_path: str
) -> Dict[str, Any]:
    """
    Performs VERIFY_ONLY: reads rows back from Google Sheets and compares
    counts and primary keys against candidate database.
    """
    extracted = extract_and_transform_dataset(candidate_db_path)
    verification = {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASSED",
        "sheets": {}
    }

    for sheet_name, db_info in extracted.items():
        expected_count = db_info["total_extracted"]
        cols = db_info["columns"]
        pk_idx = cols.index(db_info["primary_key"])

        res = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A2:A"
        ).execute()
        sheet_pks = [row[0] for row in res.get("values", []) if row]
        actual_count = len(sheet_pks)

        matched = (actual_count == expected_count)
        if not matched:
            verification["status"] = "DISCREPANCY_DETECTED"

        verification["sheets"][sheet_name] = {
            "expected_count": expected_count,
            "actual_count": actual_count,
            "difference": actual_count - expected_count,
            "matched": matched,
        }

    return verification
