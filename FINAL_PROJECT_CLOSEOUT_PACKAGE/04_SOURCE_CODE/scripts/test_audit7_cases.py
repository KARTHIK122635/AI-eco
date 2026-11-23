import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

def clean_snippet(s, max_len=140):
    if not s:
        return ""
    s = re.sub(r'\s+', ' ', s.replace('\u00a0', ' ').replace('\u202f', ' ')).strip()
    for prefix in [
        r'^as an?\s+[^,]+,\s+you(?:’|\')ll\s+',
        r'^as an?\s+[^,]+,\s+you\s+will\s+',
        r'^we(?:\'|’)?re\s+looking\s+for\s+an?\s+[^,]+(?:\s+to|\s+who)\s+',
        r'^we(?:\'|’)?re\s+hiring\s+an?\s+[^,]+(?:\s+to|\s+who)\s+',
        r'^the\s+role\s+involves\s+',
        r'^join\s+our\s+team\s+to\s+'
    ]:
        s = re.sub(prefix, '', s, flags=re.I)
    if s and s[0].isupper() and not s[:3].isupper():
        s = s[0].lower() + s[1:]
    if len(s) > max_len:
        cut = s[:max_len].rfind('. ')
        if cut != -1 and cut > 40:
            s = s[:cut+1]
        else:
            cut_sp = s[:max_len].rfind(' ')
            if cut_sp != -1:
                s = s[:cut_sp]
    return s.strip(' .,;')

def test_generate_reason(r):
    title = r['jobTitle'].strip()
    comp = r['companyName'].strip()
    cat = r['category']
    old_reason = r['classificationReason']
    resp = r.get('responsibilityEvidence') or ""
    t_lower = title.lower()

    # Preserve audited specific reasons
    already_specific_keywords = [
        "Senior accounting management role leading revenue recognition (ASC 606)",
        "Technical infrastructure capacity planning and cluster bring-up",
        "AI solutions architecture and customer engineering leading Claude model adoption",
        "AI solutions architecture and technical partnership leadership guiding global and public health",
        "AI solutions architecture and domain engineering enabling life sciences",
        "AI solutions architecture and technical advisory leadership guiding non-profit",
        "Customer- and partner-facing pre-sales solutions architecture role cultivating technical relationships with GSIs",
        "Pre-sales solutions architecture management leading a team of technical architects deploying Claude AI models",
        "Customer-facing AI architecture leadership managing pre-sales solutions architects",
        "Internal IT operations engineering role managing corporate IT fleet systems",
        "Customer success and AI adoption leadership partnering with FSI enterprise clients",
        "Commercial lease administration, contract risk management",
        "Public policy analysis, empirical economics research, and societal governance"
    ]
    for kw in already_specific_keywords:
        if kw.lower() in old_reason.lower():
            return old_reason

    resp_snippet = clean_snippet(resp, max_len=130)

    # 1. Autonomous Systems Security Engineer
    if 'autonomous systems security' in t_lower:
        return f"Autonomous and sensing systems security engineering role securing data center hardware footprint, physical sites, and firmware integrity at {comp}."

    # 2. Hardware Systems Architect / Hardware roles
    if 'hardware systems architect' in t_lower:
        return f"AI hardware systems architecture role focused on accelerator topologies, interconnect, power, and thermal scaling for large-scale compute systems at {comp}."
    if 'hardware' in t_lower and ('security' in t_lower or 'platform' in t_lower):
        return f"Hardware platform and firmware security engineering role designing secure boot chains, root of trust, and bare-metal defense at {comp}."

    # 3. Data Engineer roles
    if 'data engineer' in t_lower:
        if 'billing' in t_lower or 'payment' in t_lower:
            return f"Data engineering role designing financial data pipelines, billing models, and transaction analytics supporting fiscal systems at {comp}."
        if 'recruiting' in t_lower or 'talent' in t_lower:
            return f"Data engineering and analytics role building talent acquisition reporting pipelines, headcount models, and operational dashboards at {comp}."
        if 'solutions architect' in t_lower or 'specialist solutions' in t_lower:
            return f"Specialist solutions architecture role guiding customer data engineering, lakehouse pipelines, and distributed data platform deployments at {comp}."
        if 'product manager' in t_lower:
            return f"Technical product management role defining roadmap, developer workflows, and system capabilities for data engineering platforms at {comp}."
        if resp_snippet:
            return f"Data engineering role designing scalable ETL data pipelines, storage infrastructure, and analytics platforms for {resp_snippet} at {comp}."
        return f"Data engineering role building scalable ETL pipelines, distributed data infrastructure, and analytics platforms at {comp}."

    # 4. Corporate Finance / Accounting roles
    if any(k in t_lower for k in ['corporate accounting', 'corporate finance', 'revenue accounting', 'infrastructure accounting', 'infrastructure lease accounting', 'compute accounting', 'capex accounting', 'deal strategy', 'deal velocity', 'finance & strategy', 'finance systems', 'tax ']):
        if 'lease' in t_lower:
            return f"Corporate infrastructure lease accounting role managing lease contracts, ASC 842 compliance, and datacenter capital commitments at {comp}."
        if 'revenue' in t_lower:
            return f"Corporate revenue accounting role managing ASC 606 revenue recognition, month-end financial close, and billing reconciliation at {comp}."
        if 'deal' in t_lower:
            return f"Corporate finance and deal strategy role structuring commercial contract pricing, margin analysis, and deal velocity controls at {comp}."
        if 'tax' in t_lower:
            return f"Corporate tax accounting and compliance role managing international tax filings, transfer pricing, and statutory reporting at {comp}."
        if 'systems' in t_lower:
            return f"Finance systems role configuring ERP workflows, financial automation pipelines, and ledger integrations at {comp}."
        if resp_snippet:
            return f"Corporate financial planning, accounting, and internal controls role responsible for {resp_snippet} at {comp}."
        return f"Corporate finance and accounting role managing financial planning, general ledgers, financial close, and internal controls at {comp}."

    # Category-based tailored synthesis for remaining
    if cat == 'CORE_AI_ML':
        if 'research scientist' in t_lower or 'research engineer' in t_lower:
            if resp_snippet:
                return f"AI scientific research and model development role focused on {resp_snippet} at {comp}."
            return f"Frontier AI scientific research and machine learning engineering role developing foundational model capabilities at {comp}."
        elif 'post-training' in t_lower or 'alignment' in t_lower or 'rlhf' in t_lower or 'fine-tuning' in t_lower:
            if resp_snippet:
                return f"Model post-training, alignment, and evaluation engineering role focused on {resp_snippet} at {comp}."
            return f"Core AI alignment and post-training role refining model behavior, reinforcement learning, and safety evaluations at {comp}."
        elif 'pretraining' in t_lower or 'pre-training' in t_lower:
            if resp_snippet:
                return f"Foundation model pretraining role responsible for {resp_snippet} at {comp}."
            return f"Foundation model pretraining engineering role scaling large-scale distributed training runs and datasets at {comp}."
        elif 'eval' in t_lower:
            if resp_snippet:
                return f"AI evaluation and model capability benchmarking role responsible for {resp_snippet} at {comp}."
            return f"Model evaluation engineering role developing automated benchmarks and capability assessments at {comp}."
        else:
            if resp_snippet:
                return f"Machine learning engineering role responsible for {resp_snippet} at {comp}."
            return f"Direct machine learning and deep learning engineering role building models and algorithmic systems at {comp}."

    elif cat == 'AI_INFRASTRUCTURE':
        if 'hardware' in t_lower or 'silicon' in t_lower or 'asic' in t_lower:
            if resp_snippet:
                return f"AI hardware engineering and compute systems role focused on {resp_snippet} at {comp}."
            return f"AI hardware systems architecture role evaluating accelerator topologies, memory hierarchies, and silicon performance at {comp}."
        elif 'data center' in t_lower or 'facility' in t_lower or 'power' in t_lower or 'cooling' in t_lower:
            if resp_snippet:
                return f"Data center infrastructure and physical compute operations role responsible for {resp_snippet} at {comp}."
            return f"Data center engineering role managing physical power, cooling, space, and deployment operations for AI compute clusters at {comp}."
        elif 'network' in t_lower or 'interconnect' in t_lower or 'infiniband' in t_lower:
            if resp_snippet:
                return f"High-performance AI networking and fabric engineering role focused on {resp_snippet} at {comp}."
            return f"High-speed interconnect and network infrastructure role optimizing fabric bandwidth and collective communications for AI clusters at {comp}."
        elif 'cluster' in t_lower or 'gpu' in t_lower or 'fleet' in t_lower or 'orchestration' in t_lower:
            if resp_snippet:
                return f"AI compute cluster infrastructure role responsible for {resp_snippet} at {comp}."
            return f"Large-scale AI cluster engineering role managing GPU fleet bring-up, workload orchestration, and accelerator health at {comp}."
        else:
            if resp_snippet:
                return f"AI compute infrastructure role focused on {resp_snippet} at {comp}."
            return f"Core infrastructure engineering role supporting high-performance compute clusters and distributed systems at {comp}."

    elif cat == 'AI_PRODUCT_SOLUTIONS':
        if 'solutions architect' in t_lower or 'applied ai architect' in t_lower:
            if resp_snippet:
                return f"AI solutions architecture role partnering with customers on {resp_snippet} at {comp}."
            return f"Customer-facing AI solutions architecture role designing model deployment topologies and technical workflows at {comp}."
        elif 'forward deployed' in t_lower or 'fde' in t_lower:
            if resp_snippet:
                return f"Forward-deployed AI engineering role working with customers to {resp_snippet} at {comp}."
            return f"Forward-deployed AI engineering role deploying custom models, pipelines, and integrations for enterprise clients at {comp}."
        elif 'developer relations' in t_lower or 'advocate' in t_lower or 'devrel' in t_lower:
            if resp_snippet:
                return f"Developer relations and technical enablement role focused on {resp_snippet} at {comp}."
            return f"Developer advocacy and technical enablement role building community tools, sample apps, and documentation for {comp}."
        elif 'product manager' in t_lower or 'product lead' in t_lower or 'tpm' in t_lower:
            if resp_snippet:
                return f"Technical AI product management role driving product roadmaps and customer solutions for {resp_snippet} at {comp}."
            return f"Technical AI product management role defining features, deployment workflows, and capabilities for {comp}."
        elif 'customer success' in t_lower or 'csm' in t_lower:
            if resp_snippet:
                return f"Customer success and technical adoption role partnering with enterprise accounts on {resp_snippet} at {comp}."
            return f"Customer success and technical enablement role accelerating client onboarding and model integration at {comp}."
        else:
            if resp_snippet:
                return f"AI solutions and customer engineering role focused on {resp_snippet} at {comp}."
            return f"Technical solutions engineering role driving customer deployment, integration, and adoption of AI technologies at {comp}."

    elif cat == 'AI_SUPPORTING_TECH':
        if 'security' in t_lower or 'cyber' in t_lower or 'infosec' in t_lower:
            if resp_snippet:
                return f"Security engineering role focused on {resp_snippet} at {comp}."
            return f"Information security and application defense role safeguarding systems, models, and infrastructure against vulnerabilities at {comp}."
        elif 'backend' in t_lower or 'platform engineer' in t_lower or 'systems engineer' in t_lower:
            if resp_snippet:
                return f"Core backend and platform engineering role responsible for {resp_snippet} at {comp}."
            return f"Backend software engineering role designing distributed services, microservices, and reliable APIs at {comp}."
        elif 'frontend' in t_lower or 'full stack' in t_lower or 'fullstack' in t_lower or 'ui' in t_lower:
            if resp_snippet:
                return f"Fullstack and frontend engineering role building user-facing applications and interfaces for {resp_snippet} at {comp}."
            return f"Web application engineering role developing user interfaces, client components, and interactive experiences at {comp}."
        elif 'devops' in t_lower or 'sre' in t_lower or 'reliability' in t_lower or 'infrastructure' in t_lower:
            if resp_snippet:
                return f"Site reliability and platform operations role responsible for {resp_snippet} at {comp}."
            return f"DevOps and site reliability engineering role managing cloud infrastructure, CI/CD pipelines, and observability at {comp}."
        elif 'compiler' in t_lower or 'kernel' in t_lower:
            if resp_snippet:
                return f"Systems and compiler engineering role focused on {resp_snippet} at {comp}."
            return f"Low-level systems software role developing compilers, runtimes, and optimized execution passes at {comp}."
        else:
            if resp_snippet:
                return f"Software engineering role responsible for {resp_snippet} at {comp}."
            return f"Technical engineering role building software tools, backend platforms, and systems supporting AI products at {comp}."

    elif cat == 'NON_AI_TECH':
        if 'it ' in t_lower or 'it operations' in t_lower or 'helpdesk' in t_lower or 'desktop' in t_lower:
            if resp_snippet:
                return f"Corporate IT systems engineering role focused on {resp_snippet} at {comp}."
            return f"Corporate IT operations role managing employee hardware fleets, identity provisioning, and enterprise desktop tools at {comp}."
        elif 'av ' in t_lower or 'audio' in t_lower or 'video' in t_lower:
            if resp_snippet:
                return f"Audio-visual systems engineering role responsible for {resp_snippet} at {comp}."
            return f"Corporate AV engineering role maintaining conferencing systems, conference room hardware, and event production at {comp}."
        elif 'network' in t_lower or 'sysadmin' in t_lower:
            if resp_snippet:
                return f"Enterprise network administration role responsible for {resp_snippet} at {comp}."
            return f"Internal corporate network engineering role maintaining office connectivity, VPNs, switches, and edge infrastructure at {comp}."
        else:
            if resp_snippet:
                return f"Enterprise IT and technical operations role responsible for {resp_snippet} at {comp}."
            return f"Traditional enterprise IT, business applications, and infrastructure engineering role at {comp}."

    elif cat == 'NON_TECHNICAL':
        if 'recruiter' in t_lower or 'recruiting' in t_lower or 'talent' in t_lower or 'hr' in t_lower or 'people' in t_lower:
            if resp_snippet:
                return f"Talent acquisition and human resources role focused on {resp_snippet} at {comp}."
            return f"Human resources and talent operations role managing candidate sourcing, interview pipelines, and employee onboarding at {comp}."
        elif 'sales' in t_lower or 'account executive' in t_lower or 'business development' in t_lower or 'bdr' in t_lower or 'sdr' in t_lower:
            if resp_snippet:
                return f"Commercial sales and revenue generation role responsible for {resp_snippet} at {comp}."
            return f"Enterprise sales and commercial account management role driving revenue growth, pipeline generation, and customer acquisition at {comp}."
        elif 'marketing' in t_lower or 'communications' in t_lower or 'brand' in t_lower or 'pr ' in t_lower or 'content' in t_lower:
            if resp_snippet:
                return f"Marketing and external communications role focused on {resp_snippet} at {comp}."
            return f"Marketing strategy and brand management role executing corporate campaigns, messaging, and community outreach at {comp}."
        elif 'policy' in t_lower or 'government' in t_lower or 'regulatory' in t_lower:
            if resp_snippet:
                return f"Public policy and regulatory affairs role focused on {resp_snippet} at {comp}."
            return f"Government affairs and public policy role analyzing AI regulatory frameworks, legislative developments, and external relations at {comp}."
        elif 'operations' in t_lower or 'program manager' in t_lower or 'coordinator' in t_lower or 'logistics' in t_lower:
            if resp_snippet:
                return f"Business operations and program management role responsible for {resp_snippet} at {comp}."
            return f"Corporate operations and administrative management role driving cross-functional project execution and organizational cadences at {comp}."
        else:
            if resp_snippet:
                return f"Corporate operational role focused on {resp_snippet} at {comp}."
            return f"Business operational, administrative, or non-technical functional support role at {comp}."

    else: # UNCERTAIN
        if resp_snippet:
            return f"Role with ambiguous technical scope involving {resp_snippet} at {comp}; categorized as uncertain pending further domain evidence."
        return f"Job title and description lack sufficient evidence to definitively confirm technical depth or specialized category at {comp}."

# Let's inspect test cases
test_jobs = [
    ('Autonomous Systems Security Engineer', 'job_5757352c69c94652'),
    ('Hardware Systems Architect', 'job_46ab92d6b3d90f5e'),
    ('Data Engineer, Product', 'job_8f652cc76da624e7'),
    ('Data Engineer, Billing & Payments', 'job_055dac98677af801'),
    ('Corporate Accounting', 'job_82529721fad25dda'),
    ('Director, Infrastructure Lease Accounting', 'job_d586c26604249dae'),
    ('3P Revenue Accounting & Reporting', 'job_e98b00bb44e6a41d'),
    ('AI Outcomes Manager, Financial Services', 'job_eb45b729c76db3d4'),
    ('AI Forward Deployed Engineer', 'job_5008700b1cf661ac')
]

for title, jid in test_jobs:
    rec = next(r for r in records if r['jobId'] == jid)
    print(f"[{rec['category']}] {rec['companyName']} - {rec['jobTitle']}")
    print(f"  Old: {rec['classificationReason']}")
    print(f"  New: {test_generate_reason(rec)}")
    print()
