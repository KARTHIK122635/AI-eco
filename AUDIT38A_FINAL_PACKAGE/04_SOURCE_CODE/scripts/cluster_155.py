import json
from collections import defaultdict

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

biz_records = [r for r in records if r['classificationReason'] == 'Coordinates cross-functional business operations, program delivery, and operational planning cadences.']

categorized = defaultdict(list)
unmatched = []

for r in biz_records:
    t = r['jobTitle']
    tl = t.lower()
    resp = r.get('responsibilityEvidence', '')
    
    if 'cmc' in tl or 'manufacturing' in tl or 'biology' in tl or 'biological' in tl:
        categorized['Life Sciences, Bio Harms & Lab Operations'].append(r)
    elif 'customer  success' in tl or 'customer success' in tl:
        categorized['Customer Success Management'].append(r)
    elif 'sox' in tl or 'assurance' in tl or 'internal audit' in tl or 'order-to-cash' in tl:
        categorized['SOX Compliance & Internal Controls Assurance'].append(r)
    elif 'asset management' in tl or 'commercial associate' in tl:
        categorized['Data Center Asset Management & Commercial Leases'].append(r)
    elif 'discovery' in tl or 'technical operations specialist' in tl:
        categorized['Discovery & Scientific Operations'].append(r)
    elif 'docs' in tl or 'documentation' in tl:
        categorized['Technical Documentation & Platform Guides'].append(r)
    elif 'hardware lab' in tl or 'lab manager' in tl:
        categorized['Hardware Laboratory Management'].append(r)
    elif 'incident manager' in tl:
        categorized['Incident Management & Threat Response'].append(r)
    elif 'safeguards' in tl or 'user well-being' in tl or 'threat' in tl or 'cbrn' in tl or 'investigator' in tl:
        categorized['Trust & Safety, Threat Intelligence & Safeguards'].append(r)
    elif 'gas supply' in tl or 'energy' in tl or 'power supply' in tl:
        categorized['Energy & Utility Infrastructure Procurement'].append(r)
    elif 'data center capacity' in tl or 'capacity delivery' in tl or 'capacity planning' in tl or 'capacity deployment' in tl or 'network capacity' in tl:
        categorized['Data Center Capacity Delivery & Planning'].append(r)
    elif 'data center' in tl or 'design manager' in tl or 'fit out' in tl or 'commissioning' in tl:
        categorized['Data Center Design, Commissioning & Operations'].append(r)
    elif 'transaction' in tl or 'acquisitions' in tl or 'debt capital' in tl or 'capital markets' in tl or 'portfolio' in tl:
        categorized['Real Estate Transactions & Capital Markets'].append(r)
    elif 'investor relations' in tl:
        categorized['Investor Relations & Financial Communications'].append(r)
    elif 'national security' in tl or 'public sector' in tl or 'international affairs' in tl:
        categorized['National Security, Public Policy & Government Engagement'].append(r)
    elif 'podcast' in tl or 'media' in tl or 'creative' in tl or 'brand' in tl:
        categorized['Media Production & Brand Storytelling'].append(r)
    elif 'pricing' in tl:
        categorized['Enterprise Pricing & Commercial Strategy'].append(r)
    elif 'insurance' in tl or 'risk' in tl or 'ehs' in tl:
        categorized['Enterprise Risk, Insurance & EHS Compliance'].append(r)
    elif 'training' in tl or 'instructor' in tl or 'education specialist' in tl:
        categorized['Technical Training & Customer Education'].append(r)
    elif 'gtm' in tl or 'business operations' in tl or 'strategy & operations' in tl:
        categorized['GTM Strategy & Business Operations'].append(r)
    elif 'reseller' in tl or 'resale' in tl or 'partner' in tl or 'alliances' in tl:
        categorized['Partner, Reseller & Channel Operations'].append(r)
    elif 'technical deployment' in tl or 'deployment lead' in tl:
        categorized['Technical Customer Deployment Management'].append(r)
    elif 'financial reporting' in tl or 'accounts receivable' in tl or 'ap lead' in tl or 'gbs' in tl:
        categorized['Corporate Accounting & Financial Operations'].append(r)
    elif 'data analyst' in tl or 'bi analyst' in tl:
        categorized['Business Intelligence & Data Analysis'].append(r)
    elif 'security' in tl or 'cyber' in tl:
        categorized['Security Operations & Cyber Defense'].append(r)
    elif 'solution specialist' in tl or 'solutions specialist' in tl or 'runtime' in tl:
        categorized['Technical Solution Specialists'].append(r)
    elif 'research' in tl or 'grants' in tl or 'benchmarks' in tl:
        categorized['Research Operations & Academic Grants'].append(r)
    elif 'community' in tl or 'contributor' in tl:
        categorized['Community Engagement & Developer Relations'].append(r)
    else:
        unmatched.append(r)

print("\n--- Summary of Categories in 155 ---")
for cat_name, items in sorted(categorized.items(), key=lambda x: -len(x[1])):
    print(f"{len(items):3d} records: {cat_name}")

print(f"\nUnmatched records: {len(unmatched)}")
for r in unmatched:
    print(f"  {r['jobId']} | {r['jobTitle']} | {r['responsibilityEvidence'][:80]}")
