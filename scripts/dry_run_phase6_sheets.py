"""
scripts/dry_run_phase6_sheets.py
Performs a strictly READ-ONLY dry-run inspection of the Google Spreadsheet
and generates a structured comparison against proposed Phase VI updates.
DO NOT WRITE OR MUTATE SPREADSHEET DATA.
"""

import os
import sys
import json
import csv

# Ensure repo root is on path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.google_sheets_client import load_existing_credentials, get_sheets_service

SPREADSHEET_ID = "194VUo-VyuEiqSIk-4xq9z2ZA_NiD9UkiOU_nP0IzuLI"

def run_dry_run_audit():
    creds = load_existing_credentials()
    if not creds or not creds.valid:
        print("ERROR: Credentials not found or invalid.")
        return

    service = get_sheets_service(creds)
    if not service:
        print("ERROR: Could not initialize Google Sheets service.")
        return

    print("Fetching live spreadsheet metadata (READ-ONLY)...")
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = spreadsheet.get("sheets", [])

    live_sheets = {}
    for s in sheets:
        props = s["properties"]
        title = props["title"]
        grid = props.get("gridProperties", {})
        live_sheets[title] = {
            "sheet_id": props["sheetId"],
            "row_count": grid.get("rowCount", 0),
            "column_count": grid.get("columnCount", 0),
            "index": props.get("index", 0)
        }

    # Load local exported CSVs
    exports_dir = os.path.join(REPO_ROOT, "data", "exports", "phase6")
    repos_csv = os.path.join(exports_dir, "github_repositories.csv")
    metrics_csv = os.path.join(exports_dir, "github_metrics.csv")
    assocs_csv = os.path.join(exports_dir, "github_associations.csv")
    analytics_csv = os.path.join(exports_dir, "github_analytics.csv")
    manifest_path = os.path.join(exports_dir, "export_manifest.json")

    with open(repos_csv, "r", encoding="utf-8") as f:
        repos_data = list(csv.reader(f))
    with open(metrics_csv, "r", encoding="utf-8") as f:
        metrics_data = list(csv.reader(f))
    with open(assocs_csv, "r", encoding="utf-8") as f:
        assocs_data = list(csv.reader(f))
    with open(analytics_csv, "r", encoding="utf-8") as f:
        analytics_data = list(csv.reader(f))

    # Fetch existing headers of GitHub_Repositories and GitHub_Metrics
    gh_repos_range = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="GitHub_Repositories!A1:Z1"
    ).execute().get("values", [[]])[0]

    gh_metrics_range = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="GitHub_Metrics!A1:Z1"
    ).execute().get("values", [[]])[0]

    diff_report = {
        "spreadsheet_id": SPREADSHEET_ID,
        "spreadsheet_title": spreadsheet.get("properties", {}).get("title"),
        "live_worksheets_count": len(live_sheets),
        "live_worksheets": live_sheets,
        "proposed_changes": {
            "new_worksheets_to_add": [
                {
                    "title": "GitHub_Associations",
                    "proposed_rows": len(assocs_data), # 193
                    "proposed_cols": len(assocs_data[0]), # 11
                    "cells_to_write": len(assocs_data) * len(assocs_data[0])
                },
                {
                    "title": "GitHub_Analytics",
                    "proposed_rows": len(analytics_data), # 48
                    "proposed_cols": len(analytics_data[0]), # 8
                    "cells_to_write": len(analytics_data) * len(analytics_data[0])
                }
            ],
            "worksheets_to_evolve": [
                {
                    "title": "GitHub_Repositories",
                    "live_rows": live_sheets.get("GitHub_Repositories", {}).get("row_count"),
                    "live_cols": live_sheets.get("GitHub_Repositories", {}).get("column_count"),
                    "live_header_cols": len(gh_repos_range),
                    "proposed_rows": len(repos_data), # 193
                    "proposed_cols": len(repos_data[0]), # 25
                    "cells_to_write": len(repos_data) * len(repos_data[0]),
                    "header_diff": {
                        "live_headers": gh_repos_range,
                        "proposed_headers": repos_data[0],
                        "added_columns": [c for c in repos_data[0] if c not in gh_repos_range]
                    }
                },
                {
                    "title": "GitHub_Metrics",
                    "live_rows": live_sheets.get("GitHub_Metrics", {}).get("row_count"),
                    "live_cols": live_sheets.get("GitHub_Metrics", {}).get("column_count"),
                    "live_header_cols": len(gh_metrics_range),
                    "proposed_rows": len(metrics_data), # 211
                    "proposed_cols": len(metrics_data[0]), # 17
                    "cells_to_write": len(metrics_data) * len(metrics_data[0]),
                    "header_diff": {
                        "live_headers": gh_metrics_range,
                        "proposed_headers": metrics_data[0],
                        "added_columns": [c for c in metrics_data[0] if c not in gh_metrics_range]
                    }
                }
            ],
            "dashboard_updates": {
                "target_range": "Dashboard!A26:L45",
                "cells_to_write": 20 * 12, # 240 cells
                "charts_to_add": [
                    {"chart_id": 7, "title": "GitHub Repository Lifecycle Distribution", "type": "PIE"},
                    {"chart_id": 8, "title": "Top AI Research Repositories by Stargazers", "type": "BAR"}
                ]
            },
            "unmodified_worksheets": [
                "Startups", "Products", "Research_Papers", "AI_News", "AI_Jobs", "Collection_Logs"
            ]
        }
    }

    print("\n--- DRY RUN SUMMARY ---")
    print(f"Spreadsheet Title: {diff_report['spreadsheet_title']}")
    print(f"Total Live Sheets: {diff_report['live_worksheets_count']}")
    print(f"New sheets to add: {[s['title'] for s in diff_report['proposed_changes']['new_worksheets_to_add']]}")
    print(f"Sheets to evolve: {[s['title'] for s in diff_report['proposed_changes']['worksheets_to_evolve']]}")
    print(f"Sheets untouched: {diff_report['proposed_changes']['unmodified_worksheets']}")
    
    total_cells = (
        len(repos_data) * len(repos_data[0]) +
        len(metrics_data) * len(metrics_data[0]) +
        len(assocs_data) * len(assocs_data[0]) +
        len(analytics_data) * len(analytics_data[0]) +
        240
    )
    print(f"Total estimated cells to update: {total_cells}")

    # Output JSON summary
    out_path = os.path.join(REPO_ROOT, "reports", "phase6_dashboard", "dry_run_summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(diff_report, f, indent=2)
    print(f"Dry run summary written to: {out_path}")

if __name__ == "__main__":
    run_dry_run_audit()
