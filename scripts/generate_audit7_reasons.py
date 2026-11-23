import json
import re
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

BOILERPLATE_PATTERNS = [
    r'while candidates in the listed locations',
    r'remote candidates in other',
    r'shape the trajectory of one of the most',
    r'we develop reliable ai systems',
    r'anthropic is dedicated to developing',
    r'anthropic is building ai systems',
    r'scale ai is at the forefront',
    r'at scale, we develop',
    r'mission is to create reliable',
    r'committed researchers, engineers',
    r'werde teil der digitalen zukunft',
    r'more than \d+[\d,]*\s+organizations',
    r'req\s*id:',
    r'location:\s*',
    r'hybrid policy',
    r'visa sponsorship'
]

def is_boilerplate(text):
    if not text:
        return True
    t = text.lower()
    return any(re.search(p, t) for p in BOILERPLATE_PATTERNS)

def clean_snippet(s, max_len=120):
    if not s:
        return ""
    s = re.sub(r'\s+', ' ', s.replace('\u00a0', ' ').replace('\u202f', ' ')).strip()
    
    # Strip common header boilerplate
    s = re.sub(r'^(?:AI\s+Engineer\s+-\s+FDE\s+\([^)]+\)\s+-\s+All\s+Levels\s+)?(?:CSQ\w+\s+)?Req\s+ID:[^:]+(?:Location:[^:]+)?Mission\s+', '', s, flags=re.I)
    s = re.sub(r'^(?:CSQ\w+\s+)?Mission\s+', '', s, flags=re.I)
    s = re.sub(r'^About(?:\s+the\s+role)?:?\s*', '', s, flags=re.I)
    s = re.sub(r'^[A-Z][A-Za-z0-9\s&,]+\s+is\s+seeking\s+an?\s+[^,]+(?:\s+to|\s+who)\s+', '', s, flags=re.I)
    s = re.sub(r'^[A-Z][A-Za-z0-9\s&,]+\s+is\s+looking\s+for\s+an?\s+[^,]+(?:\s+to|\s+who)\s+', '', s, flags=re.I)
    
    for prefix in [
        r'^as an?\s+[^,]+,\s+you(?:’|\')ll\s+',
        r'^as an?\s+[^,]+,\s+you\s+will\s+',
        r'^as an?\s+[^,]+,\s+you\s+are\s+',
        r'^we(?:\'|’)?re\s+looking\s+for\s+an?\s+[^,]+(?:\s+to|\s+who)\s+',
        r'^we(?:\'|’)?re\s+hiring\s+an?\s+[^,]+(?:\s+to|\s+who)\s+',
        r'^the\s+role\s+involves\s+',
        r'^join\s+our\s+team\s+to\s+',
        r'^join\s+[A-Z][A-Za-z0-9\s&,\']+\s+team(?:\s+as\s+an?\s+[^,]+)?\s+in\s+a\s+[^,]+(?:\s+role\s+driving|\s+to)\s+'
    ]:
        s = re.sub(prefix, '', s, flags=re.I)
        
    s = re.sub(r'^(?:and|or|with|to|for|in|on|at|by|from|as)\s+', '', s, flags=re.I).strip()
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
                
    # Strip punctuation and trailing conjunctions/prepositions
    s = re.sub(r'[\s.,;:\-]+$', '', s)
    s = re.sub(r'\b(and|or|in|to|for|with|of|the|a|an|on|at|by|from|as)$', '', s, flags=re.I).strip()
    s = re.sub(r'[\s.,;:\-]+$', '', s)
    return s

def extract_real_responsibility(desc, fallback_snippet=""):
    if fallback_snippet and not is_boilerplate(fallback_snippet):
        cleaned = clean_snippet(fallback_snippet, max_len=125)
        if cleaned and not is_boilerplate(cleaned):
            return cleaned
        
    if not desc:
        return ""
        
    sentences = re.split(r'(?<=[.!?])\s+', desc)
    action_keywords = [
        'deliver professional services', 'help our customers build', 'partner with our customers to',
        'design and build', 'architect, build', 'scaling distributed', 'lead the design',
        'responsible for', 'helping large enterprises', 'develop and optimize', 'build and scale'
    ]
    for sent in sentences:
        s = sent.strip()
        if len(s) < 30 or len(s) > 250:
            continue
        if is_boilerplate(s):
            continue
        s_lower = s.lower()
        if any(ak in s_lower for ak in action_keywords):
            cleaned = clean_snippet(s, max_len=125)
            if cleaned and not is_boilerplate(cleaned):
                return cleaned
            
    return ""

# Precise list of hand-audited specific reasons from previous audits to preserve verbatim
PRESERVED_REASONS = {
    "Senior accounting management role leading revenue recognition (ASC 606), month-end close, balance sheet reconciliations, and SOX controls for cloud service provider marketplace channels (AWS Bedrock, Google Cloud Vertex, Azure Marketplace).",
    "Customer success and enterprise AI adoption leadership partnering with clients on model deployment and Claude integration at Anthropic",
    "Customer- and partner-facing pre-sales solutions architecture role cultivating technical relationships with GSIs, hyperscalers, and enterprise clients for Claude model deployment at Anthropic.",
    "Pre-sales solutions architecture management leading a team of technical architects deploying Claude AI models and enterprise AI integrations at Anthropic.",
    "Customer-facing AI architecture leadership managing pre-sales solutions architects delivering enterprise AI integrations and Claude model deployments at Anthropic.",
    "AI solutions architecture and technical partnership leadership guiding global and public health organizations in deploying Claude AI models for mission-critical outcomes at Anthropic.",
    "AI solutions architecture and domain engineering enabling life sciences, biotechnology, and healthcare organizations to build on Claude AI models at Anthropic.",
    "AI solutions architecture and technical advisory leadership guiding non-profit, philanthropic, and social impact organizations in deploying Claude AI models at Anthropic.",
    "Internal IT operations engineering role managing corporate IT fleet systems, hardware lifecycle, identity provisioning, and asset management at Anthropic",
    "Customer success and AI adoption leadership partnering with FSI enterprise clients to operationalize Claude and generative AI solutions at Anthropic",
    "Commercial lease administration, contract risk management, and physical infrastructure asset governance for high-performance AI data center footprint at Anthropic",
    "Public policy analysis, empirical economics research, and societal governance examining frontier AI labor market impacts and economic implications at Anthropic",
    "Technical infrastructure capacity planning and cluster bring-up leadership driving high-performance AI compute fleet readiness and data center operations at Anthropic",
    "Corporate community relations, regional stakeholder engagement, and public affairs supporting data center facility construction at Anthropic"
}

def generate_audit7_reason(r):
    old_reason = r['classificationReason'].strip()
    
    # Check if already specifically preserved
    for pres in PRESERVED_REASONS:
        if pres.lower() in old_reason.lower():
            return old_reason

    title = r['jobTitle'].strip()
    comp = r['companyName'].strip()
    cat = r['category']
    resp = r.get('responsibilityEvidence') or ""
    desc = r.get('jobDescription') or ""
    t_lower = title.lower()
    
    resp_snippet = extract_real_responsibility(desc, resp)

    # Specific Examples called out by the user:
    # 1. Autonomous Systems Security Engineer (security/firmware/hardening)
    if 'autonomous systems security' in t_lower:
        return f"Autonomous systems security engineering role securing data center hardware footprint, physical sites, firmware integrity, and operational hardening at {comp}."

    # 2. Hardware Systems Architect (hardware topologies/scaling)
    if 'hardware systems architect' in t_lower:
        return f"AI hardware systems architecture role focused on accelerator topologies, interconnect scaling, memory hierarchies, and compute system performance at {comp}."
    if 'hardware platform security' in t_lower or 'platform hardware security' in t_lower:
        return f"Hardware platform and firmware security engineering role designing secure boot chains, root of trust, and bare-metal defense at {comp}."

    # 3. Data Engineer (pipelines/data infrastructure)
    if 'data engineer' in t_lower:
        if 'billing' in t_lower or 'payment' in t_lower:
            return f"Data engineering role designing financial data pipelines, billing models, and transaction analytics supporting fiscal systems at {comp}."
        if 'recruiting' in t_lower or 'talent' in t_lower:
            return f"Data engineering and analytics role building talent acquisition reporting pipelines, headcount models, and operational dashboards at {comp}."
        if 'gtm' in t_lower:
            return f"Data engineering role building go-to-market data pipelines, revenue operations infrastructure, and sales analytics at {comp}."
        if 'specialist solutions' in t_lower or 'solutions architect' in t_lower:
            return f"Specialist solutions architecture role guiding enterprise data engineering, lakehouse pipelines, and distributed data platform deployments at {comp}."
        if 'product manager' in t_lower:
            return f"Technical product management role defining roadmap, developer workflows, and system capabilities for data engineering platforms at {comp}."
        if resp_snippet:
            return f"Data engineering role designing scalable ETL data pipelines and distributed data infrastructure for {resp_snippet} at {comp}."
        return f"Data engineering role building scalable ETL pipelines, distributed data infrastructure, and analytics platforms at {comp}."

    # 4. Corporate Finance (actual accounting/planning/controls)
    if any(k in t_lower for k in [
        'corporate accounting', 'corporate finance', 'revenue accounting', 'infrastructure accounting',
        'infrastructure lease accounting', 'compute accounting', 'capex accounting', 'deal strategy',
        'deal velocity', 'finance & strategy', 'finance systems', 'tax ', 'taxation', 'accountant',
        'accounting manager', 'accounting director', 'treasury'
    ]):
        if 'lease' in t_lower:
            return f"Corporate infrastructure lease accounting role managing lease contracts, ASC 842 compliance, and datacenter capital commitments at {comp}."
        if 'revenue' in t_lower:
            return f"Corporate revenue accounting role managing ASC 606 revenue recognition, month-end financial close, and billing reconciliation at {comp}."
        if 'deal' in t_lower:
            return f"Corporate finance and deal strategy role structuring commercial contract pricing, margin analysis, and deal velocity controls at {comp}."
        if 'tax' in t_lower:
            return f"Corporate tax accounting and compliance role managing tax filings, transfer pricing, and statutory reporting at {comp}."
        if 'compute' in t_lower or 'capex' in t_lower:
            return f"Corporate infrastructure finance role managing compute capex accounting, asset depreciation, and datacenter cost allocations at {comp}."
        if 'systems' in t_lower or 'engineer' in t_lower:
            return f"Finance systems engineering role building automated financial workflows, ERP data integrations, and billing ledgers at {comp}."
        if resp_snippet:
            return f"Corporate financial planning, accounting, and internal controls role responsible for {resp_snippet} at {comp}."
        return f"Corporate financial planning, accounting, internal financial controls, and fiscal administration at {comp}."

    # Broader role-specific grounds based on title and category:
    if cat == 'CORE_AI_ML':
        if 'research scientist' in t_lower or 'research engineer' in t_lower or 'scientist' in t_lower:
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
        elif 'network' in t_lower or 'interconnect' in t_lower or 'infiniband' in t_lower or 'roce' in t_lower:
            if resp_snippet:
                return f"High-performance AI networking and fabric engineering role focused on {resp_snippet} at {comp}."
            return f"High-speed interconnect and network infrastructure role optimizing fabric bandwidth and collective communications for AI clusters at {comp}."
        elif 'cluster' in t_lower or 'gpu' in t_lower or 'fleet' in t_lower or 'orchestration' in t_lower or 'capacity' in t_lower:
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
        elif 'customer success' in t_lower or 'csm' in t_lower or 'outcomes' in t_lower:
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
        elif 'business system' in t_lower:
            if resp_snippet:
                return f"Business systems engineering role supporting internal enterprise platforms for {resp_snippet} at {comp}."
            return f"Business systems engineering role building integrations and tools for enterprise business operations at {comp}."
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
        elif 'legal' in t_lower or 'counsel' in t_lower or 'compliance' in t_lower:
            if resp_snippet:
                return f"Legal counsel and compliance role focused on {resp_snippet} at {comp}."
            return f"Corporate legal role advising on contracts, intellectual property, and regulatory compliance at {comp}."
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

if __name__ == '__main__':
    new_reasons = [generate_audit7_reason(r) for r in records]
    counts = Counter(new_reasons)
    print(f"Total: {len(new_reasons)}, Distinct: {len(counts)}")
    print("\nTop 10 most common reasons:")
    for r, c in counts.most_common(10):
        print(f"  {c:2d} | {r}")
