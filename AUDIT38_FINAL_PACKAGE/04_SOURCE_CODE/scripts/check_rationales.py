import json

with open("data/stage3/gemini_enrichment_results.jsonl", "r", encoding="utf-8") as f:
    for i in range(5):
        line = f.readline()
        if not line: break
        d = json.loads(line)
        print(f"[{d['record_id']}] {d['field_name']}:")
        print(f"  val_status: {d['validation_status']}")
        print(f"  rationale: {d['validation_rationale']}")
        print(f"  proposed: {d['proposed_value']}")
        print(f"  quote: {d['evidence_quote']}")
