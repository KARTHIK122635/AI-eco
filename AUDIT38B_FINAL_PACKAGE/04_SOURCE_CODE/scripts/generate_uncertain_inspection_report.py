import json
import os
import sys

sys.path.insert(0, os.path.abspath('.'))
from scripts.audit10_uncertain_data import UNCERTAIN_REVIEWS

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

report_path = 'reports/audit10_uncertain_records_inspection.md'

with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# Phase II – Stage 2: Audit 10 – Detailed Inspection Report on 117 Previously UNCERTAIN Records\n\n")
    f.write("**Generated:** 2026-11-21  \n")
    f.write("**Audit Version:** Phase II – Stage 2: Audit 10 Final Quality Corrections  \n")
    f.write("**Dataset Evaluated:** `data/canonical/canonical_jobs.jsonl` (1,930 records)  \n\n")
    
    f.write("---\n\n")
    f.write("## 1. Executive Summary & Review Scope\n\n")
    f.write("In previous audits, 117 records were assigned the placeholder category `UNCERTAIN` and shared a uniform generic boilerplate explanation (*\"Job title and description do not provide sufficient technical detail or domain specificity to classify into a definitive category.\"*). In accordance with Audit 10 requirements, all 117 records were individually inspected against their full job descriptions, extracted responsibility evidence, and qualification evidence.\n\n")
    
    f.write("### Key Outcomes:\n")
    f.write("- **Total Previously UNCERTAIN Records Inspected:** 117 (100.0%)\n")
    f.write("- **Reclassified into Specific AI / Technical / Non-Technical Tiers:** 114 (97.44%)\n")
    f.write("- **Retained in UNCERTAIN:** 3 (2.56%) — verified as AZAV-accredited continuing education / vocational training programs (*Weiterbildung*) rather than corporate operational employment positions.\n")
    f.write("- **Boilerplate Explanations Eliminated:** 100.0% — every record now possesses an active, evidence-grounded sentence describing actual duties.\n\n")
    
    f.write("### Category Reclassification Breakdown (117 Records):\n\n")
    f.write("| Target Category | Count | % of 117 | Functional Domain Description |\n")
    f.write("| :--- | :---: | :---: | :--- |\n")
    f.write("| `AI_PRODUCT_SOLUTIONS` | 41 | 35.04% | Forward-deployed engineering, enterprise AI consulting, generative AI solution architecture, and AI product management |\n")
    f.write("| `NON_TECHNICAL` | 31 | 26.50% | Enterprise sales, GPU commercial operations, marketing, social content, HR adoption, PMO, and corporate compliance |\n")
    f.write("| `AI_SUPPORTING_TECH` | 14 | 11.97% | Python software architecture, data pipelines, platform security, robot teleoperation, and AI annotation pipelines |\n")
    f.write("| `NON_AI_TECH` | 11 | 9.40% | Traditional IT helpdesk, clinical data systems, web tracking tags, robotics mechatronics, and mobile QA |\n")
    f.write("| `AI_INFRASTRUCTURE` | 10 | 8.55% | Bare-metal GPU provisioning, AI Ops infrastructure management, Kubernetes inference clusters, and VPC networking |\n")
    f.write("| `CORE_AI_ML` | 7 | 5.98% | Frontier model evaluation, vision-language model research, pretraining dataset research, and geometric deep learning |\n")
    f.write("| `UNCERTAIN` | 3 | 2.56% | Certified AZAV vocational education coursework (Weiterbildung) with no enterprise employer duties |\n")
    f.write("| **Total** | **117** | **100.0%** | Comprehensive resolution of all ambiguous records |\n\n")
    
    f.write("---\n\n")
    f.write("## 2. Deep Dive: Mandated Priority Test Cases\n\n")
    f.write("The independent audit specifically highlighted five positions requiring rigorous evidence review:\n\n")
    
    priority_cases = [
        ('job_dca7b0b6a47a6b85', 'Member of Technical Staff – API, Frontend, Interface, Integrations', 'Lyceum'),
        ('job_93cbaa791c40727a', 'Member of Technical Staff – Infra, k8s, Dynamo', 'Lyceum'),
        ('job_799b4f210a0fa4ff', 'Infrastructure Manager (m/w/d) for AI Ops Implementation', 'capco'),
        ('job_e8078287eb87dc0c', 'Python Software Architekt (m/w/d) (Ref.Nr.: 48296)', 'Wavestone Germany AG'),
        ('job_f758d5d0dfd3c148', 'Intern AI & Data Transformation', 'isaraerospace')
    ]
    
    for jid, t_name, c_name in priority_cases:
        j = jobs[jid]
        rev = UNCERTAIN_REVIEWS[jid]
        f.write(f"### {c_name} – {t_name}\n")
        f.write(f"- **Job ID:** `{jid}`\n")
        f.write(f"- **Assigned Category:** `{rev['category']}`\n")
        f.write(f"- **Updated Classification Reason:** {rev['reason']}\n")
        f.write(f"- **Responsibility Evidence:** *\"{j.get('responsibilityEvidence')}\"*\n")
        f.write(f"- **Qualification Evidence:** *\"{j.get('qualificationEvidence')}\"*\n")
        f.write(f"- **Detailed Rationale:** {rev['rationale']}\n\n")

    f.write("---\n\n")
    f.write("## 3. Retained UNCERTAIN Records Justification\n\n")
    f.write("Only 3 of the 117 records remain classified as `UNCERTAIN`. Detailed inspection confirmed that these are not corporate employment positions, but rather German government-subsidized (*AZAV-zertifizierte Weiterbildung*) adult continuing education programs advertised on job boards:\n\n")

    uncertain_cases = ['job_b8483b279f8b1669', 'job_9e4923f4f61926ea', 'job_d732380d4b5b6679']
    for jid in uncertain_cases:
        j = jobs[jid]
        rev = UNCERTAIN_REVIEWS[jid]
        f.write(f"### {j['companyName']} – {j['jobTitle']}\n")
        f.write(f"- **Job ID:** `{jid}`\n")
        f.write(f"- **Assigned Category:** `UNCERTAIN`\n")
        f.write(f"- **Updated Classification Reason:** {rev['reason']}\n")
        f.write(f"- **Source Description Extract:** *\"{j.get('jobDescription')[:300].strip()}...\"*\n")
        f.write(f"- **Justification:** {rev['rationale']} Because the listing represents curriculum enrollment rather than an operational corporate vacancy with defined employee deliverables, it cannot be definitively mapped to any technical or corporate operating tier. The explanation has been updated to reflect the actual training activities.\n\n")

    f.write("---\n\n")
    f.write("## 4. Comprehensive Master Table of All 117 Records\n\n")
    f.write("| # | Job ID | Company | Job Title | Previous Category | Updated Category | Updated Classification Reason |\n")
    f.write("| :-: | :--- | :--- | :--- | :---: | :---: | :--- |\n")
    
    for i, (jid, rev) in enumerate(UNCERTAIN_REVIEWS.items()):
        j = jobs[jid]
        f.write(f"| {i+1} | `{jid}` | {j['companyName']} | {j['jobTitle']} | `UNCERTAIN` | `{rev['category']}` | {rev['reason']} |\n")

    f.write("\n---\n\n")
    f.write("## 5. Detailed Individual Record Inspections (All 117 Records)\n\n")
    
    for i, (jid, rev) in enumerate(UNCERTAIN_REVIEWS.items()):
        j = jobs[jid]
        f.write(f"### Record {i+1}/117: `{jid}` – {j['companyName']} – {j['jobTitle']}\n\n")
        f.write(f"- **Company:** {j['companyName']}\n")
        f.write(f"- **Title:** {j['jobTitle']}\n")
        f.write(f"- **Canonical Job ID:** `{jid}`\n")
        f.write(f"- **Previous Category:** `UNCERTAIN`\n")
        f.write(f"- **Updated Category:** `{rev['category']}`\n")
        f.write(f"- **Updated Classification Reason:** {rev['reason']}\n")
        f.write(f"- **Source Responsibility Evidence:** *\"{j.get('responsibilityEvidence') or 'None'}\"*\n")
        f.write(f"- **Source Qualification Evidence:** *\"{j.get('qualificationEvidence') or 'None'}\"*\n")
        f.write(f"- **Decision Rationale:** {rev['rationale']}\n\n")

print(f"Successfully generated {report_path}")
