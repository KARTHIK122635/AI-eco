import csv

with open('reports/project_cleanup/project_classification.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    unknowns = [r for r in reader if r['category'] == 'UNKNOWN_REQUIRES_REVIEW']

print(f'Total UNKNOWN_REQUIRES_REVIEW: {len(unknowns)}')
by_prefix = {}
for r in unknowns:
    top = r['relative_path'].split('/')[0]
    by_prefix[top] = by_prefix.get(top, 0) + 1

print('Unknowns by directory prefix:')
for k, v in sorted(by_prefix.items(), key=lambda x: x[1], reverse=True):
    print(f'  {k:<30}: {v}')

print('\nDetailed listing of all unknowns:')
for r in unknowns:
    print(f"  {r['relative_path']} ({r['filename']})")
