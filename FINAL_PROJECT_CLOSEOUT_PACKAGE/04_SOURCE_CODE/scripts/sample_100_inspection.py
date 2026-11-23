import json
import random
from collections import defaultdict
import sys
sys.path.append('scripts')
from build_audit8_reasons import records, generate_audit8_reason

# 1. Target examples from user prompt
target_jids = {
    'job_8f652cc76da624e7': 'Data Engineer, Product',
    'job_3bb94e0bcc526fe4': 'AI Infrastructure Operations, Demand Planning',
    'job_aaed61f362acc050': 'Applied AI Architect',
    'job_66f13e9130efa2e2': 'Account Executive, AI Native',
    'job_89f4cca3c62134a7': 'Forward Deployed Engineering Intern (AI Agent)',
    'job_800f8b9de6ea2b31': 'Anthropic Fellows Program, Economics & Policy',
    'job_46ab92d6b3d90f5e': 'Hardware Systems Architect',
    'job_5757352c69c94652': 'Autonomous Systems Security Engineer',
    'job_82529721fad25dda': 'Corporate Accounting'
}

by_cat = defaultdict(list)
for r in records:
    by_cat[r['category']].append(r)

# Select ~15 records per category, including targets
sample_records = []
target_records = [r for r in records if r['jobId'] in target_jids]
sample_records.extend(target_records)

random.seed(42)
for cat, recs in sorted(by_cat.items()):
    cat_non_target = [r for r in recs if r['jobId'] not in target_jids]
    sample_records.extend(random.sample(cat_non_target, min(14, len(cat_non_target))))

print(f"Total sampled records for inspection: {len(sample_records)}")
assert len(sample_records) >= 100

# Write to inspection report file and print summary
with open('reports/audit8_sample_100_inspection.md', 'w', encoding='utf-8') as f:
    f.write("# Audit 8: Sample Inspection of 100+ Records Across All Seven Categories\n\n")
    f.write(f"Total inspected records: {len(sample_records)}\n\n")
    f.write("| # | Job ID | Company | Job Title | Category | Classification Reason (Audit 8) |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
    for idx, r in enumerate(sample_records, 1):
        reason = generate_audit8_reason(r)
        f.write(f"| {idx} | `{r['jobId']}` | {r['companyName']} | {r['jobTitle']} | **`{r['category']}`** | {reason} |\n")

print("Generated reports/audit8_sample_100_inspection.md successfully!")
