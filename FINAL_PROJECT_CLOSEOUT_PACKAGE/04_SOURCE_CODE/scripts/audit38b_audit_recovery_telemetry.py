"""
Audit 38B: Recovery Telemetry Audit & Classification
===================================================
Inspects all 6 collection_logs rows in the packaged working database.
Audits the 5 STAGE_LEVEL_RECOVERY rows:
- 4 rows with end_time=NULL and status=COMPLETED -> INVALID_COMPLETION_TELEMETRY (MISSING_END_TIME)
- 1 row with end_time < start_time by ~4.9ms -> INVALID_COMPLETION_TELEMETRY (NEGATIVE_DURATION_CLOCK_SKEW)
- 1 routine incremental run with valid start/end times -> VALID_TELEMETRY

Strictly preserves historical timestamps without fabrication.
Exports audit38b_recovery_telemetry_audit.csv.
"""

import sqlite3
import csv
import os
from datetime import datetime, timezone

WORKSPACE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(WORKSPACE_DIR, "data", "working", "rolling_ai_ecosystem.db")
OUTPUT_CSV = os.path.join(WORKSPACE_DIR, "audit38b_recovery_telemetry_audit.csv")

def parse_iso(ts_str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None

def audit_recovery_telemetry():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT run_id, execution_type, status, start_time, end_time, 
               original_run_id, recovery_run_id, lease_owner, last_heartbeat
        FROM collection_logs
        ORDER BY run_id
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    print(f"Auditing {len(rows)} collection_logs rows...")

    audit_records = []
    for r in rows:
        run_id = r["run_id"]
        exec_type = r["execution_type"]
        status = r["status"]
        st_str = r["start_time"]
        et_str = r["end_time"]
        orig_id = r["original_run_id"]
        rec_id = r["recovery_run_id"]
        lease_owner = r["lease_owner"]

        st_dt = parse_iso(st_str)
        et_dt = parse_iso(et_str)

        duration_sec = None
        duration_ms = None
        has_end_time = (et_str is not None)
        timestamp_order_valid = False

        if st_dt and et_dt:
            delta = (et_dt - st_dt).total_seconds()
            duration_sec = round(delta, 6)
            duration_ms = round(delta * 1000.0, 3)
            timestamp_order_valid = (delta >= 0.0)

        # Classify telemetry validity
        if exec_type == "ROUTINE_DAILY_INCREMENTAL":
            if status == "COMPLETED" and has_end_time and timestamp_order_valid:
                telemetry_status = "VALID_TELEMETRY"
                defect_finding = "Clean terminal telemetry; valid start and end timestamps."
            else:
                telemetry_status = "INVALID_TELEMETRY"
                defect_finding = "Routine run telemetry anomaly."
        elif exec_type == "STAGE_LEVEL_RECOVERY":
            if not has_end_time:
                telemetry_status = "INVALID_COMPLETION_TELEMETRY"
                defect_finding = "Historical recovery run marked COMPLETED without persisting end_time. Missing terminal completion timestamp."
            elif not timestamp_order_valid:
                telemetry_status = "INVALID_COMPLETION_TELEMETRY"
                defect_finding = f"Negative execution duration ({duration_ms} ms). End timestamp was captured prior to pipeline execution start."
            else:
                telemetry_status = "VALID_RECOVERY_TELEMETRY"
                defect_finding = "Recovery run completed with valid start and end timestamps."
        else:
            telemetry_status = "UNKNOWN_EXECUTION_TYPE"
            defect_finding = "Unrecognized execution type."

        # Recommended future validation policy
        policy_verdict = "PASS" if telemetry_status.startswith("VALID") else "FAIL_NON_CONFORMING"

        audit_records.append({
            "run_id": run_id,
            "execution_type": exec_type,
            "recorded_status": status,
            "start_time": st_str or "NULL",
            "end_time": et_str or "NULL",
            "duration_seconds": duration_sec if duration_sec is not None else "N/A",
            "duration_milliseconds": duration_ms if duration_ms is not None else "N/A",
            "has_end_time": "YES" if has_end_time else "NO",
            "end_time_ge_start_time": "YES" if timestamp_order_valid else ("NO" if (st_dt and et_dt) else "N/A"),
            "original_run_id": orig_id or "NULL",
            "recovery_run_id": rec_id or "NULL",
            "lease_owner": lease_owner or "NULL",
            "telemetry_audit_classification": telemetry_status,
            "defect_finding": defect_finding,
            "validation_policy_verdict": policy_verdict
        })

    fieldnames = [
        "run_id", "execution_type", "recorded_status", "start_time", "end_time",
        "duration_seconds", "duration_milliseconds", "has_end_time", "end_time_ge_start_time",
        "original_run_id", "recovery_run_id", "lease_owner",
        "telemetry_audit_classification", "defect_finding", "validation_policy_verdict"
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(audit_records)

    print(f"[PASS] Generated {OUTPUT_CSV} with {len(audit_records)} telemetry evaluations.")
    print("\nTelemetry Breakdown:")
    for ar in audit_records:
        print(f"  [{ar['run_id']}] {ar['execution_type']:24} | {ar['telemetry_audit_classification']:30} | Duration: {ar['duration_milliseconds']} ms")

if __name__ == "__main__":
    audit_recovery_telemetry()
