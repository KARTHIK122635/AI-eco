import json

def main():
    records = [json.loads(line) for line in open('reports/stage3_enrichment_results.jsonl', encoding='utf-8')]
    print(f"Total candidates: {len(records)}")
    for i, r in enumerate(records, 1):
        v_type = type(r.get('enriched_value')).__name__
        val_str = str(r.get('enriched_value'))
        if len(val_str) > 50:
            val_str = val_str[:47] + "..."
        print(f"{i:02d}. [{r['entity_type']}] {r['record_id']} -> {r['field_name']} ({v_type}): {val_str}")

if __name__ == '__main__':
    main()
