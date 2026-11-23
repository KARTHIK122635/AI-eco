"""
Detailed Accounting Breakdown Across All 3 Execution Sessions
============================================================
"""

import json
import re

def main():
    log_path = "data/stage3/gemini_enrichment_audit.log"
    with open(log_path, "r", encoding="utf-8") as f:
        log_lines = f.readlines()

    # Split into sessions
    sessions = []
    current_session = []
    for line in log_lines:
        if "Pre-execution database SHA-256" in line and current_session:
            sessions.append(current_session)
            current_session = [line]
        else:
            current_session.append(line)
    if current_session:
        sessions.append(current_session)

    print(f"Total Sessions: {len(sessions)}")
    for idx, s_lines in enumerate(sessions, 1):
        s_text = "".join(s_lines)
        dispatches = re.findall(r"Initiating Gemini API call: request_id=([0-9a-f\-]+), record_id=([a-zA-Z0-9_\-]+), field=([a-zA-Z0-9_\-]+)", s_text)
        failures = re.findall(r"Gemini enrichment failed for ([a-zA-Z0-9_\-]+)", s_text)
        successes = len(dispatches) - len(failures)
        print(f"\n--- Session {idx} ---")
        print(f"  First line:       {s_lines[0].strip()[:80]}")
        print(f"  Total Requests:   {len(dispatches)}")
        print(f"  Success (200):    {successes}")
        print(f"  Failed Requests:  {len(failures)}")
        if failures:
            print(f"  Failures detail:  {failures}")

    # Also check per-proposal cost in gemini_enrichment_results.jsonl
    with open("data/stage3/gemini_enrichment_results.jsonl", "r", encoding="utf-8") as f:
        proposals = [json.loads(line) for line in f if line.strip()]

    sum_cost = sum(p["usage"]["estimated_cost_usd"] for p in proposals)
    sum_prompt = sum(p["usage"]["prompt_tokens"] for p in proposals)
    sum_comp = sum(p["usage"]["candidates_tokens"] for p in proposals)
    sum_total = sum(p["usage"]["total_tokens"] for p in proposals)

    with open("data/stage3/gemini_enrichment_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)

    rep_cost = summary["usage_and_costs"]["estimated_cost_usd"]
    rep_prompt = summary["usage_and_costs"]["prompt_tokens"]
    rep_comp = summary["usage_and_costs"]["candidates_tokens"]
    rep_total = summary["usage_and_costs"]["total_tokens"]

    print("\n--- Cost and Token Reconciliation ---")
    print(f"Per-proposal sum prompt tokens:     {sum_prompt}")
    print(f"Summary prompt tokens:              {rep_prompt}")
    print(f"Per-proposal sum comp tokens:       {sum_comp}")
    print(f"Summary comp tokens:                {rep_comp}")
    print(f"Per-proposal sum total tokens:      {sum_total}")
    print(f"Summary total tokens:               {rep_total}")
    print(f"Per-proposal sum cost (USD):        ${sum_cost:.6f} (${sum_cost:.8f})")
    print(f"Summary cost (USD):                 ${rep_cost:.6f} (${rep_cost:.8f})")
    print(f"Exact Difference:                   ${abs(rep_cost - sum_cost):.8f}")

    # Calculate exact unrounded vs rounded
    pricing_prompt = 0.075 / 1_000_000
    pricing_comp = 0.30 / 1_000_000
    calc_from_totals = (rep_prompt * pricing_prompt) + (rep_comp * pricing_comp)
    print(f"Calculated directly from tokens:    ${calc_from_totals:.8f}")

if __name__ == "__main__":
    main()
