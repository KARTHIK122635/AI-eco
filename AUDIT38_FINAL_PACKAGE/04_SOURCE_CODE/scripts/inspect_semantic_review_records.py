import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import csv

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

# Let's inspect potential REQUIRES_REVIEW records
review_candidates = [
    # The 7 known quality audit review records
    ('job_87e7a826e1904b7b', 'Leadership role spans technical cybersecurity operations and non-technical people management.'),
    ('job_61a941b22ab64bde', 'Specialized national security intelligence and weapons risk analysis on the borderline between non-technical compliance and technical AI safety.'),
    ('job_20072b58f5dc3523', 'Specialized national security intelligence and weapons risk analysis on the borderline between non-technical compliance and technical AI safety.'),
    ('job_91fd8017f05b1d94', 'Software engineering fellowship role evaluating AI models on the borderline between non-technical expert annotation and technical development.'),
    ('job_f3d068e4db415d90', 'Software engineering fellowship role evaluating AI models on the borderline between non-technical expert annotation and technical development.'),
    ('job_953d904c00132369', 'Digital agency role bridging traditional e-commerce web consulting and rapid prototyping of AI solutions.'),
    ('job_0fccf7a2e05aac14', 'Listing represents state-subsidized AZAV vocational education (Bildungsgutschein) rather than standard commercial employment.'),
    # The priority ambiguous roles identified in Audit 14:
    ('job_ca9fd326e9b5b4a3', 'Engineering management title categorized as NON_TECHNICAL due to focus on billing operations, financial ledgers, and revenue systems of record.'),
    ('job_6b50fb83f97464c3', 'Staff software engineer title categorized as NON_TECHNICAL due to focus on pricing models, billing infrastructure, and payment processing reconciliations.'),
    ('job_3f7c9cb190129a33', 'Strategic projects title categorized as CORE_AI_ML spanning operational data labeling delivery, cross-functional program execution, and model evaluation.'),
    ('job_d93736d1ee4a9098', 'Finance systems leadership role positioned on the boundary between financial planning and enterprise ERP software systems implementation.'),
    ('job_7427cacb294b9060', 'General talent pool expression-of-interest listing rather than a single concrete open requisition with fixed operational assignments.'),
    ('job_0d920108a62c8874', 'Independent contractor domain fellowship evaluating AI models on the boundary between professional financial advisory and AI safety benchmarking.'),
    ('job_8ad086e5f89d9290', 'Independent contractor domain fellowship evaluating AI models on the boundary between clinical medical advisory and generative model evaluation.'),
    ('job_9a8d370f471b9403', 'Independent contractor domain fellowship evaluating AI models on the boundary between clinical medical advisory and generative model evaluation.'),
]

review_dict = {jid: rationale for jid, rationale in review_candidates}
print(f"Total defined review records: {len(review_dict)}")

for j in jobs:
    if j['jobId'] in review_dict:
        print(f"{j['jobId']} | {j['companyName']} | {j['jobTitle']} | Cat: {j['category']}")
        print(f"   Rationale: {review_dict[j['jobId']]}")
        print()
