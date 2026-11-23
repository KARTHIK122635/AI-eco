import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import csv
import json

with open('reports/stage2_semantic_classification_audit.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    sem_headers = reader.fieldnames
    sem_row = next(reader)

print("Semantic Audit Headers:", sem_headers)
print("Semantic Audit Sample Row:")
for k, v in sem_row.items():
    print(f"  {k}: {v[:80] if v else v}")

with open('reports/stage2_classification_reason_quality_audit.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    qual_headers = reader.fieldnames
    qual_row = next(reader)

print("\nQuality Audit Headers:", qual_headers)
print("Quality Audit Sample Row:")
for k, v in qual_row.items():
    print(f"  {k}: {v[:80] if v else v}")

with open('reports/stage2_quality_metrics.json', 'r', encoding='utf-8') as f:
    metrics = json.load(f)

print("\nQuality Metrics Keys:", list(metrics.keys()))
