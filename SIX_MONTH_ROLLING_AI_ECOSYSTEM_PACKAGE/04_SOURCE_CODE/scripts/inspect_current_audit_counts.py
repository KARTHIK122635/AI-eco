import csv
from collections import Counter

with open('reports/stage2_semantic_classification_audit.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    align_counts = Counter(row['Semantic alignment result'] for row in reader)

print("Semantic alignment result counts:", align_counts)

with open('reports/stage2_classification_reason_quality_audit.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    qual_counts = Counter(row['audit_status'] for row in reader)

print("Quality audit status counts:", qual_counts)
