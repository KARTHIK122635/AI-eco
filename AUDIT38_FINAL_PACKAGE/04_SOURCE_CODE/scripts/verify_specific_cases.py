import sys
sys.path.append('scripts')
from generate_audit7_reasons import records, generate_audit7_reason

test_cases = [
    'Autonomous Systems Security Engineer',
    'Hardware Systems Architect',
    'Data Engineer, Product',
    'Specialist Solutions Architect - Data Engineering',
    'Corporate Accounting',
    'Director, Infrastructure Lease Accounting',
    'Staff Backline Engineer – ML/AI'
]

for tc in test_cases:
    matches = [r for r in records if tc.lower() in r['jobTitle'].lower()]
    for m in matches[:1]:
        print(f"Role: {m['companyName']} - {m['jobTitle']} [{m['category']}]")
        print(f"  Reason: {generate_audit7_reason(m)}")
        print()
