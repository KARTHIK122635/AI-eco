"""
Data Transformation and Field Mapping Module for Google Sheets Integration.
Preserves 100% of SQLite source fields (provenance, evidence, timestamps) without loss.
Computes dynamic 6-month eligibility & 24h freshness, handles NULLs safely, and prevents formula injection.
"""

import sqlite3
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple, Optional

from core.rolling_window import (
    compute_rolling_window,
    parse_publication_timestamp,
    classify_freshness,
)

PRIMARY_KEYS: Dict[str, str] = {
    "Startups": "startup_id",
    "Products": "product_id",
    "Research_Papers": "paper_id",
    "AI_News": "news_id",
    "AI_Jobs": "job_id",
    "GitHub_Repositories": "repo_id",
    "GitHub_Metrics": "snapshot_id",
    "Collection_Logs": "run_id",
}

TABLE_TO_SHEET_MAP: Dict[str, str] = {
    "ai_startups": "Startups",
    "ai_products": "Products",
    "ai_research_papers": "Research_Papers",
    "ai_news": "AI_News",
    "ai_jobs": "AI_Jobs",
    "github_repositories": "GitHub_Repositories",
    "github_metrics_history": "GitHub_Metrics",
    "collection_logs": "Collection_Logs",
}


def sanitize_cell_value(val: Any) -> Any:
    """
    Safely normalizes cell values for Google Sheets:
    - None -> empty string ""
    - int/float -> numeric value
    - bool -> string "TRUE"/"FALSE"
    - str -> trimmed string, escaping leading formula triggers (=, +, -, @)
    Preserves internal commas, quotes, and newlines safely.
    """
    if val is None:
        return ""
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"

    s = str(val).strip()
    # Prevent formula injection if leading character is a formula operator
    if s.startswith(("=", "+", "-", "@")) and not s.replace(".", "", 1).replace("-", "", 1).isdigit():
        return "'" + s
    return s


def get_worksheet_schema(db_path: str) -> Dict[str, List[str]]:
    """
    Dynamically maps all source columns from SQLite tables into worksheet columns,
    appending calculated fields. Guarantees zero loss of provenance or evidence fields.
    """
    uri = f"file:{os.path.abspath(db_path)}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cursor = conn.cursor()

    schema_map = {}
    for tbl_name, sheet_name in TABLE_TO_SHEET_MAP.items():
        cursor.execute(f"PRAGMA table_info({tbl_name})")
        db_cols = [r[1] for r in cursor.fetchall()]

        # Determine calculated columns to append
        if sheet_name in ("Startups", "Products", "Research_Papers", "AI_News", "AI_Jobs"):
            calc_cols = ["is_eligible_6_months", "is_fresh_24h", "last_synced_at"]
        else:
            calc_cols = ["last_synced_at"]

        # Ensure no duplicates if columns already exist
        full_cols = [c for c in db_cols]
        for cc in calc_cols:
            if cc not in full_cols:
                full_cols.append(cc)

        schema_map[sheet_name] = full_cols

    conn.close()
    return schema_map


def extract_and_transform_dataset(
    db_path: str,
    ref_time: Optional[datetime] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Extracts all datasets in read-only mode from SQLite candidate database
    and applies schema mappings, date normalization, and dynamic eligibility tags.
    """
    now_utc = ref_time or datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    now_iso = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")

    window_start, window_end = compute_rolling_window(now_utc, months=6)

    uri = f"file:{os.path.abspath(db_path)}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    schema_map = get_worksheet_schema(db_path)
    results = {}

    for tbl_name, sheet_name in TABLE_TO_SHEET_MAP.items():
        cursor.execute(f"SELECT * FROM {tbl_name}")
        rows = cursor.fetchall()
        source_count = len(rows)

        cols = schema_map[sheet_name]
        pk_field = PRIMARY_KEYS[sheet_name]

        transformed_rows: List[List[Any]] = []
        pk_seen = set()
        duplicate_count = 0
        rejected_count = 0
        rejection_reasons = []
        eligible_6m_count = 0
        fresh_24h_count = 0

        for row in rows:
            row_dict = dict(row)
            pk_val = row_dict.get(pk_field)

            # Check null primary key
            if pk_val is None or str(pk_val).strip() == "":
                rejected_count += 1
                rejection_reasons.append("NULL_PRIMARY_KEY")
                continue

            # Check duplicate primary key
            if pk_val in pk_seen:
                duplicate_count += 1
                rejected_count += 1
                rejection_reasons.append(f"DUPLICATE_KEY: {pk_val}")
                continue
            pk_seen.add(pk_val)

            # Determine publication timestamp for dynamic freshness calculation
            pub_date_raw = None
            date_type = row_dict.get("date_type")

            if sheet_name == "Startups":
                pub_date_raw = row_dict.get("founding_date") or row_dict.get("announcement_date") or row_dict.get("published_at")
            elif sheet_name == "Products":
                pub_date_raw = row_dict.get("release_date") or row_dict.get("launch_date") or row_dict.get("published_at")
            elif sheet_name == "Research_Papers":
                pub_date_raw = row_dict.get("publication_date")
            elif sheet_name == "AI_News":
                pub_date_raw = row_dict.get("published_at")
            elif sheet_name == "AI_Jobs":
                pub_date_raw = row_dict.get("posted_at")
            elif sheet_name == "GitHub_Repositories":
                pub_date_raw = row_dict.get("last_checked_at")
            elif sheet_name == "GitHub_Metrics":
                pub_date_raw = row_dict.get("snapshot_timestamp")
            elif sheet_name == "Collection_Logs":
                pub_date_raw = row_dict.get("start_time")

            is_eligible_6m = False
            is_fresh_24h = False
            freshness_status = row_dict.get("freshness_status")

            if sheet_name in ("Startups", "Products", "Research_Papers", "AI_News", "AI_Jobs"):
                if pub_date_raw:
                    dt = parse_publication_timestamp(pub_date_raw)
                    if dt:
                        fresh_res = classify_freshness(dt, ref_time=now_utc, window_start=window_start, date_type=date_type)
                        is_eligible_6m = fresh_res["in_rolling_window"]
                        is_fresh_24h = fresh_res["is_fresh_24h"]
                        freshness_status = fresh_res["status"]
                    else:
                        is_eligible_6m = False
                        is_fresh_24h = False
                        freshness_status = "UNVERIFIED_DATE" if date_type == "UNVERIFIED_DATE" else "MISSING_DATE"
                else:
                    is_eligible_6m = False
                    is_fresh_24h = False
                    freshness_status = "MISSING_DATE"

                if is_eligible_6m:
                    eligible_6m_count += 1
                if is_fresh_24h:
                    fresh_24h_count += 1
            else:
                # Repositories, metrics snapshots, and collection logs are operational entities, not content
                is_eligible_6m = False
                is_fresh_24h = False
                freshness_status = row_dict.get("status", "ACTIVE")

            # Build row matching column order
            cell_values = []
            for col in cols:
                if col == "is_eligible_6_months":
                    val = "TRUE" if is_eligible_6m else "FALSE"
                elif col == "is_fresh_24h":
                    val = "TRUE" if is_fresh_24h else "FALSE"
                elif col == "freshness_status":
                    val = freshness_status
                elif col == "last_synced_at":
                    val = now_iso
                else:
                    val = row_dict.get(col, "")
                cell_values.append(sanitize_cell_value(val))

            transformed_rows.append(cell_values)

        is_content = sheet_name in ("Startups", "Products", "Research_Papers", "AI_News", "AI_Jobs")
        results[sheet_name] = {
            "table_name": tbl_name,
            "sheet_name": sheet_name,
            "primary_key": pk_field,
            "is_content_entity": is_content,
            "source_row_count": source_count,
            "transformed_row_count": len(transformed_rows),
            "eligible_row_count": eligible_6m_count if is_content else None,
            "fresh_24h_count": fresh_24h_count if is_content else None,
            "rejected_row_count": rejected_count,
            "rejection_reasons": rejection_reasons,
            "duplicate_key_count": duplicate_count,
            "column_count": len(cols),
            "columns": cols,
            "rows": transformed_rows,
        }

    conn.close()
    return results


# Export WORKSHEET_COLUMNS compatibility for any imports
WORKSHEET_COLUMNS = {
    s: cols for s, cols in get_worksheet_schema(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "working", "candidate_rolling_ai_ecosystem.db")
    ).items()
}
