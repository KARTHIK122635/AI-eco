import json
from collections import Counter
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

# Let's import the updated function from build_audit9_reasons
# We will edit build_audit9_reasons.py directly.
