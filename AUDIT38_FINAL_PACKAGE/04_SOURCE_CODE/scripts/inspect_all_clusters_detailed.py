import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

with open('reports/all_repeated_clusters.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in clusters dump: {len(lines)}")
