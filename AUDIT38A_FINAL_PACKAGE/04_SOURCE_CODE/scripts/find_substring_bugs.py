with open('scripts/build_audit8_reasons.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re

patterns = re.findall(r"['\"][a-zA-Z0-9\s_-]+['\"]\s+in\s+t_lower", code)
print(f"Total 'in t_lower' checks: {len(patterns)}")
short_checks = []
for p in patterns:
    val = p.split(' in ')[0].strip('\'"')
    if len(val) <= 3:
        short_checks.append(p)

print("\nShort substring checks (length <= 3):")
for p in short_checks:
    print("  ", p)
