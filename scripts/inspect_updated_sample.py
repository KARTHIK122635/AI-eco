import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
from scripts.test_comprehensive_evidence_fix import extract_substantive_evidence, SPECIFIC_TARGET_EXCERPTS

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

print("=== CHECKING THE 6 MANDATED TARGETS ===")
for jid in [
    'job_d207b42e585bf8e6', # Digital Campaigns, Policy Advocacy
    'job_80a480dfe5f61806', # Public Policy, Strategic Advisory
    'job_03adf198b79570b7', # Research Associate, Biology
    'job_3ab4fad59bd0a42d', # Research Scientist, Life Sciences (Chemistry)
    'job_b30c4117b32b2e1b', # Research Scientist, Life Sciences (Large Molecules, Antibody Design)
    'job_d2ffb1910190a82b', # Data Acquisition Lead, Frontier Environments
]:
    j = [x for x in jobs if x['jobId'] == jid][0]
    new_ev, ch = extract_substantive_evidence(j)
    print(f"ID: {jid}")
    print(f"Title: {j['jobTitle']} ({j['companyName']})")
    print(f"Category: {j['category']}")
    print(f"Reason: {j['classificationReason']}")
    print(f"Old Evidence: {j['responsibilityEvidence']}")
    print(f"New Evidence: {new_ev}")
    print(f"Verbatim in desc: {new_ev in j['jobDescription']}")
    print("-" * 60)

print("\n=== SAMPLE OF 15 OTHER UPDATED RECORDS ===")
sample_count = 0
for j in jobs:
    if j['jobId'] in SPECIFIC_TARGET_EXCERPTS:
        continue
    new_ev, ch = extract_substantive_evidence(j)
    if ch:
        sample_count += 1
        print(f"ID: {j['jobId']} | {j['companyName']} | {j['jobTitle']}")
        print(f"  Reason: {j['classificationReason']}")
        print(f"  Old: {j['responsibilityEvidence'][:100]}...")
        print(f"  New: {new_ev}")
        print(f"  Verbatim: {new_ev in j['jobDescription']}")
        print()
        if sample_count >= 15:
            break
