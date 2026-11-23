import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

anthropic_jobs = [j for j in jobs if j['companyName'] == 'Anthropic']
print(f"Total Anthropic jobs: {len(anthropic_jobs)}")

# Let's inspect all Anthropic jobs that have a salary
sal_jobs = [j for j in anthropic_jobs if j.get('salaryMin') is not None]
print(f"Anthropic jobs with salary: {len(sal_jobs)}")

# Check each one for sales role
sales_roles = []
non_sales_roles = []

for j in sal_jobs:
    t = j['jobTitle'].lower()
    # Explicit sales titles
    if any(s in t for s in ['account executive', 'enterprise sales', 'sales lead', 'sales leader', 'sales excellence', 'business development representative', 'partner account manager', 'partner sales manager', 'strategic pursuits']):
        sales_roles.append(j)
    else:
        non_sales_roles.append(j)

print(f"Definitive sales roles: {len(sales_roles)}")
for j in sales_roles:
    print(f"  Sales: {j['jobTitle']}")

# Check if any non_sales_roles had OTE in our previous output
for j in non_sales_roles:
    if j.get('compensationType') == 'ANNUAL_OTE':
        print(f"  Misclassified as OTE: {j['jobTitle']}")
