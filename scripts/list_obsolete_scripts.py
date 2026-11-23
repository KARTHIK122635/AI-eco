import os
import csv
import ast

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLASS_PATH = os.path.join(WORKSPACE_ROOT, "reports", "project_cleanup", "project_classification.csv")

with open(CLASS_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    obsolete = [r for r in reader if r["category"] == "OBSOLETE"]

print(f"Total OBSOLETE scripts in first pass: {len(obsolete)}")
for r in obsolete:
    p = os.path.join(WORKSPACE_ROOT, r["relative_path"])
    size = os.path.getsize(p) if os.path.exists(p) else 0
    print(f"  {r['relative_path']:<45} ({size:>6} bytes)")
