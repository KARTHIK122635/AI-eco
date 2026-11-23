"""
Parse and Reconcile All API Dispatches from Audit Log
=====================================================
"""

import json
import re

def main():
    log_path = "data/stage3/gemini_enrichment_audit.log"
    with open(log_path, "r", encoding="utf-8") as f:
        log_text = f.read()

    # Find all "Initiating Gemini API call: request_id=..., record_id=..., field=..."
    pattern = r"Initiating Gemini API call: request_id=([0-9a-f\-]+), record_id=([a-zA-Z0-9_\-]+), field=([a-zA-Z0-9_\-]+)"
    dispatches = re.findall(pattern, log_text)

    print(f"Total Initiated Requests Found: {len(dispatches)}")
    unique_req_ids = set(d[0] for d in dispatches)
    print(f"Unique Request IDs: {len(unique_req_ids)}")

    # Let's inspect the timestamps and group by run sessions
    lines = log_text.splitlines()
    run_starts = []
    for i, l in enumerate(lines):
        if "Pre-execution database SHA-256" in l:
            run_starts.append((i, l))

    print(f"\nExecution Run Sessions Found: {len(run_starts)}")
    for r_i, (line_idx, l) in enumerate(run_starts, 1):
        print(f"  Session {r_i}: line {line_idx} - {l}")

if __name__ == "__main__":
    main()
