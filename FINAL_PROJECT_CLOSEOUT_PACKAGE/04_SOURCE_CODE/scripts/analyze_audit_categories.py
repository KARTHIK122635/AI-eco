import json
import csv
import re
from collections import defaultdict, Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

# Let's inspect the 93 candidate records
# Let's see which ones have genuine grammar/formatting defects (FAIL)
# vs which ones have terminology gaps
# vs which ones have category alignment questions (REQUIRES_REVIEW)

print(f"Total canonical records: {len(records)}")
