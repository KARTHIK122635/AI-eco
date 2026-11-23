"""
Check Existing Data Duplication for Startup Proposals
=====================================================
"""

import json
import sqlite3

def main():
    conn = sqlite3.connect("data/normalized/ai_ecosystem.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    with open("data/stage3/gemini_enrichment_results.jsonl", "r", encoding="utf-8") as f:
        proposals = [json.loads(line) for line in f if line.strip()]

    startup_props = [p for p in proposals if p["entity_type"] == "startup"]
    print(f"Analyzing {len(startup_props)} startup proposals for duplication:")
    print("=" * 100)

    for p in startup_props:
        rec_id = p["record_id"]
        field = p["field_name"]
        proposed = p["proposed_value"]
        cur.execute("SELECT * FROM ai_startups WHERE startup_id = ?", (rec_id,))
        row = dict(cur.fetchone())

        existing_focus = row.get("ai_focus_area")
        existing_ev = row.get("ai_evidence")
        existing_desc = row.get("description")

        is_dup = False
        dup_detail = []
        if field == "ai_specialization":
            if proposed == existing_focus:
                is_dup = True
                dup_detail.append(f"Matches existing ai_focus_area: '{existing_focus}'")
            if existing_focus and proposed and proposed.lower() in existing_focus.lower():
                is_dup = True
                dup_detail.append(f"Subsumed in existing ai_focus_area: '{existing_focus}'")
        elif field == "technologies":
            # Check if proposed technologies are already listed in ai_evidence
            if isinstance(proposed, list) and existing_ev:
                items_in_ev = [item for item in proposed if item.lower() in existing_ev.lower()]
                if len(items_in_ev) == len(proposed):
                    is_dup = True
                    dup_detail.append(f"All proposed technologies {proposed} already present in existing ai_evidence: '{existing_ev}'")

        print(f"Proposal: {p['proposal_id'][:8]}... | Record: {row['entity_name']} ({rec_id})")
        print(f"  Field:           {field}")
        print(f"  Proposed Value:  {proposed}")
        print(f"  Existing Focus:  {existing_focus}")
        print(f"  Existing Ev:     {existing_ev}")
        print(f"  Is Duplicate?    {'YES (NO NEW ENRICHMENT)' if is_dup else 'NO'}")
        if is_dup:
            print(f"  Duplication:     {'; '.join(dup_detail)}")
        print("-" * 100)

if __name__ == "__main__":
    main()
