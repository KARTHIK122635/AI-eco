import json
import re
from collections import defaultdict

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

backend_records = [r for r in records if r['classificationReason'] == 'Designs, builds, and maintains backend services, distributed systems, and APIs supporting AI platforms.']

print(f"Total backend records: {len(backend_records)}")

# Group by patterns in jobTitle
unmatched = []
categorized = defaultdict(list)

for r in backend_records:
    t = r['jobTitle']
    tl = t.lower()
    resp = r.get('responsibilityEvidence', '')
    
    # Check various patterns
    if 'education' in tl or 'developer education' in tl or 'instructor' in tl or 'training' in tl:
        categorized['Developer Education / Training'].append(r)
    elif 'executive architect' in tl or 'field executive' in tl:
        categorized['Field Executive Architecture'].append(r)
    elif 'front end' in tl or 'frontend' in tl or 'web' in tl or 'ui' in tl:
        categorized['Frontend / Web Development'].append(r)
    elif 'incident response' in tl or 'incident manager' in tl:
        categorized['Incident Response & Engineering Readiness'].append(r)
    elif 'it systems' in tl or 'client platform' in tl or 'chromeos' in tl or 'macos' in tl:
        categorized['IT Systems & Endpoint Engineering'].append(r)
    elif 'network' in tl:
        categorized['Corporate & Datacenter Network Engineering'].append(r)
    elif 'red team' in tl or 'safeguards' in tl and 'engineer' in tl:
        categorized['Red Team & Adversarial Security'].append(r)
    elif 'salesforce' in tl or 'business technology' in tl or 'crm' in tl:
        categorized['Salesforce & Business Systems Development'].append(r)
    elif 'bioinformatics' in tl or 'bio' in tl:
        categorized['Bioinformatics & Computational Biology'].append(r)
    elif 'silicon' in tl or 'rtl' in tl or 'dft' in tl or 'post-silicon' in tl or 'pnr' in tl or 'physical design' in tl or 'hardware' in tl or 'firmware' in tl:
        categorized['Silicon, Hardware & Firmware Engineering'].append(r)
    elif 'privacy' in tl:
        categorized['Privacy Engineering & Governance'].append(r)
    elif 'datacenter server lifecycle' in tl or 'server lifecycle' in tl or 'metaldev' in tl:
        categorized['Datacenter Server Lifecycle & Bare-Metal Engineering'].append(r)
    elif 'perf' in tl or 'benchmarking' in tl or 'performance' in tl:
        categorized['Performance & Benchmarking Engineering'].append(r)
    elif 'distributed data' in tl or 'data systems' in tl or 'data platform' in tl or 'storage' in tl or 'database' in tl:
        categorized['Distributed Data Systems & Storage Engineering'].append(r)
    elif 'observability' in tl or 'monitoring' in tl:
        categorized['Observability & Monitoring Systems'].append(r)
    elif 'inference' in tl:
        categorized['AI Model Inference Systems'].append(r)
    elif 'autonomous systems' in tl or 'robot' in tl or 'physical ai' in tl:
        categorized['Autonomous Systems & Robotics Engineering'].append(r)
    elif 'agent' in tl:
        categorized['AI Agent Platform & Systems Engineering'].append(r)
    elif 'solutions' in tl or 'solution architect' in tl or 'solutions engineer' in tl or 'field engineer' in tl or 'deployment' in tl:
        categorized['Field Solutions & Technical Deployment Engineering'].append(r)
    elif 'security' in tl or 'iam' in tl or 'abuse' in tl or 'auth' in tl or 'sandboxing' in tl:
        categorized['Platform Security, Identity & Access Engineering'].append(r)
    elif 'productivity' in tl or 'tools' in tl or 'research tools' in tl or 'developer' in tl or 'devex' in tl:
        categorized['Developer Tooling & Research Productivity'].append(r)
    elif 'people' in tl or 'hr' in tl:
        categorized['Technical People & Engineering HR'].append(r)
    elif 'manager' in tl or 'director' in tl or 'lead' in tl:
        categorized['Engineering Leadership & Technical Management'].append(r)
    elif 'backend' in tl or 'software engineer' in tl or 'architect' in tl or 'platform' in tl or 'infrastructure' in tl:
        categorized['Core Backend & Distributed Systems Engineering'].append(r)
    else:
        unmatched.append(r)

print("\n--- Summary of Categories in 282 ---")
for cat_name, items in sorted(categorized.items(), key=lambda x: -len(x[1])):
    print(f"{len(items):3d} records: {cat_name}")

print(f"\nUnmatched records: {len(unmatched)}")
for r in unmatched:
    print(f"  {r['jobId']} | {r['jobTitle']} | {r['responsibilityEvidence'][:80]}")
