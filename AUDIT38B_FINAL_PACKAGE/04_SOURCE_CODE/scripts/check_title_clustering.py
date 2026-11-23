import json
from collections import defaultdict
import sys
sys.path.append('scripts')
from build_audit8_reasons import records, generate_audit8_reason

reasons_to_titles = defaultdict(list)
for r in records:
    reason = generate_audit8_reason(r)
    reasons_to_titles[reason].append((r['category'], r['companyName'], r['jobTitle']))

print(f"Total distinct reasons: {len(reasons_to_titles)}")

# Let's inspect each reason and its distinct titles
for i, (reason, jobs) in enumerate(sorted(reasons_to_titles.items(), key=lambda x: len(x[1]), reverse=True)):
    unique_titles = sorted(list(set(j[2] for j in jobs)))
    cat = jobs[0][0]
    print(f"\n--- [{cat}] Cluster {i+1} ({len(jobs)} records, {len(unique_titles)} distinct titles) ---")
    print(f"Explanation: '{reason}'")
    for t in unique_titles[:5]:
        print(f"   * {t}")
    if len(unique_titles) > 5:
        print(f"   ... and {len(unique_titles)-5} more")
