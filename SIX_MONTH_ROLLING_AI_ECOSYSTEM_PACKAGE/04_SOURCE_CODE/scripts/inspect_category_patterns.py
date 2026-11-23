import json
import re
from collections import defaultdict, Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

print(f"Loaded {len(records)} records")

# Let's inspect all records in each category to develop precise rules
def inspect_category_patterns(cat_name):
    cat_recs = [r for r in records if r['category'] == cat_name]
    print(f"\n==================== {cat_name} ({len(cat_recs)} records) ====================")
    titles = [r['jobTitle'] for r in cat_recs]
    for t, count in Counter(titles).most_common(25):
        print(f"  {count:2d}x {t}")

for c in ['AI_INFRASTRUCTURE', 'CORE_AI_ML', 'AI_PRODUCT_SOLUTIONS', 'NON_AI_TECH', 'UNCERTAIN']:
    inspect_category_patterns(c)
