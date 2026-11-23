import json
from collections import defaultdict
import sys
sys.path.append('scripts')
from build_audit8_reasons import records, generate_clean_reason

reasons_to_titles = defaultdict(list)
for r in records:
    reason = generate_clean_reason(r)
    reasons_to_titles[reason].append(r['jobTitle'])

print(f"Total distinct reasons: {len(reasons_to_titles)}")
print("\nInspecting explanations with more than 20 roles:")
for reason, titles in sorted(reasons_to_titles.items(), key=lambda x: len(x[1]), reverse=True):
    unique_titles = sorted(list(set(titles)))
    print(f"\n[{len(titles)} records, {len(unique_titles)} distinct titles]: '{reason}'")
    for t in unique_titles[:8]:
        print(f"   - {t}")
    if len(unique_titles) > 8:
        print(f"   ... and {len(unique_titles)-8} more")
