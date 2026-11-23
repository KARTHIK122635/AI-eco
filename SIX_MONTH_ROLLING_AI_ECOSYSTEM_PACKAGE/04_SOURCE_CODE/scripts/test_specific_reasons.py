import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

def clean_snippet(s, max_len=140):
    if not s:
        return ""
    s = re.sub(r'\s+', ' ', s.replace('\u00a0', ' ').replace('\u202f', ' ')).strip()
    # Remove leading boilerplate phrases if any
    for prefix in [
        r'^as an?\s+[^,]+,\s+you(?:’|\')ll\s+',
        r'^as an?\s+[^,]+,\s+you\s+will\s+',
        r'^we(?:\'|’)?re\s+looking\s+for\s+an?\s+[^,]+(?:\s+to|\s+who)\s+',
        r'^the\s+role\s+involves\s+',
        r'^join\s+our\s+team\s+to\s+'
    ]:
        s = re.sub(prefix, '', s, flags=re.I)
    # lowercase first char
    if s and s[0].isupper() and not s[:3].isupper():
        s = s[0].lower() + s[1:]
    # trim to sentence or word
    if len(s) > max_len:
        cut = s[:max_len].rfind('. ')
        if cut != -1 and cut > 40:
            s = s[:cut+1]
        else:
            cut_sp = s[:max_len].rfind(' ')
            if cut_sp != -1:
                s = s[:cut_sp]
    return s.strip(' .,;')

def generate_specific_reason(r):
    title = r['jobTitle'].strip()
    comp = r['companyName'].strip()
    cat = r['category']
    old_reason = r['classificationReason']
    resp = r.get('responsibilityEvidence') or ""
    desc = r.get('jobDescription') or ""
    
    # Check if old reason is already customized/specific (e.g., from Audit 4, 5, 6 specific fixes)
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

    # Extract a representative action phrase from responsibility evidence
    resp_phrase = clean_snippet(resp, max_len=130)
    
    # Specific targeted patterns based on title and category
    t_lower = title.lower()
    
    # 1. CORE_AI_ML
    if cat == 'CORE_AI_ML':
        if 'research scientist' in t_lower or 'research engineer' in t_lower:
            if resp_phrase:
                return f"AI scientific research and model development role focused on {resp_phrase} at {comp}."
            return f"Frontier AI scientific research and machine learning engineering role developing foundational model capabilities at {comp}."
        elif 'post-training' in t_lower or 'fine-tuning' in t_lower or 'alignment' in t_lower or 'rlhf' in t_lower:
            if resp_phrase:
                return f"Model post-training, alignment, and evaluation engineering role focused on {resp_phrase} at {comp}."
            return f"Core AI alignment and post-training role refining model behavior, reinforcement learning, and safety evaluations at {comp}."
        elif 'pretraining' in t_lower or 'pre-training' in t_lower:
            if resp_phrase:
                return f"Foundation model pretraining role responsible for {resp_phrase} at {comp}."
            return f"Foundation model pretraining engineering role scaling large-scale distributed training runs and datasets at {comp}."
        elif 'eval' in t_lower:
            if resp_phrase:
                return f"AI evaluation and model capability benchmarking role responsible for {resp_phrase} at {comp}."
            return f"Model evaluation engineering role developing automated benchmarks and capability assessments at {comp}."
        else:
            if resp_phrase:
                return f"Machine learning engineering role responsible for {resp_phrase} at {comp}."
            return f"Direct machine learning and deep learning engineering role building models and algorithmic systems at {comp}."

    # 2. AI_INFRASTRUCTURE
    elif cat == 'AI_INFRASTRUCTURE':
        if 'hardware' in t_lower or 'silicon' in t_lower or 'asic' in t_lower:
            if resp_phrase:
                return f"AI hardware engineering and compute systems role focused on {resp_phrase} at {comp}."
            return f"AI hardware systems architecture role evaluating accelerator topologies, memory hierarchies, and silicon performance at {comp}."
        elif 'data center' in t_lower or 'facility' in t_lower or 'power' in t_lower or 'cooling' in t_lower:
            if resp_phrase:
                return f"Data center infrastructure and physical compute operations role responsible for {resp_phrase} at {comp}."
            return f"Data center engineering role managing physical power, cooling, space, and deployment operations for AI compute clusters at {comp}."
        elif 'network' in t_lower or 'interconnect' in t_lower or 'infiniband' in t_lower or 'roce' in t_lower:
            if resp_phrase:
                return f"High-performance AI networking and fabric engineering role focused on {resp_phrase} at {comp}."
            return f"High-speed interconnect and network infrastructure role optimizing fabric bandwidth and collective communications for AI clusters at {comp}."
        elif 'cluster' in t_lower or 'gpu' in t_lower or 'fleet' in t_lower or 'capacity' in t_lower or 'orchestration' in t_lower:
            if resp_phrase:
                return f"AI compute cluster infrastructure role responsible for {resp_phrase} at {comp}."
            return f"Large-scale AI cluster engineering role managing GPU fleet bring-up, workload orchestration, and accelerator health at {comp}."
        else:
            if resp_phrase:
                return f"AI compute infrastructure role focused on {resp_phrase} at {comp}."
            return f"Core infrastructure engineering role supporting high-performance compute clusters and distributed systems at {comp}."

    # 3. AI_PRODUCT_SOLUTIONS
    elif cat == 'AI_PRODUCT_SOLUTIONS':
        if 'solutions architect' in t_lower or 'applied ai architect' in t_lower:
            if resp_phrase:
                return f"AI solutions architecture role partnering with customers and technical teams on {resp_phrase} at {comp}."
            return f"Customer-facing AI solutions architecture role designing model deployment topologies and technical workflows on {comp}."
        elif 'forward deployed' in t_lower or 'fde' in t_lower:
            if resp_phrase:
                return f"Forward-deployed engineering role working hands-on with enterprise customers to {resp_phrase} at {comp}."
            return f"Forward-deployed AI engineering role deploying custom models, pipelines, and integrations for enterprise clients at {comp}."
        elif 'developer relations' in t_lower or 'advocate' in t_lower or 'devrel' in t_lower:
            if resp_phrase:
                return f"Developer relations and technical enablement role focused on {resp_phrase} at {comp}."
            return f"Developer advocacy and technical enablement role building community tools, sample apps, and documentation for {comp}."
        elif 'product manager' in t_lower or 'product lead' in t_lower or 'tpm' in t_lower:
            if resp_phrase:
                return f"Technical AI product management role driving product roadmaps and customer solutions for {resp_phrase} at {comp}."
            return f"Technical AI product management role defining features, deployment workflows, and capabilities for {comp}."
        elif 'customer success' in t_lower or 'csm' in t_lower or 'outcomes' in t_lower:
            if resp_phrase:
                return f"Customer success and technical adoption role partnering with enterprise accounts on {resp_phrase} at {comp}."
            return f"Customer success and technical enablement role accelerating client onboarding and model integration at {comp}."
        else:
            if resp_phrase:
                return f"AI solutions and customer engineering role focused on {resp_phrase} at {comp}."
            return f"Technical solutions engineering role driving customer deployment, integration, and adoption of AI technologies at {comp}."

    # 4. AI_SUPPORTING_TECH
    elif cat == 'AI_SUPPORTING_TECH':
        if 'data engineer' in t_lower:
            if resp_phrase:
                return f"Data engineering role designing and operating data pipelines and platform infrastructure for {resp_phrase} at {comp}."
            return f"Data platform engineering role building scalable ETL pipelines, data models, and storage infrastructure at {comp}."
        elif 'security' in t_lower or 'cyber' in t_lower or 'infosec' in t_lower:
            if resp_phrase:
                return f"Security engineering role focused on {resp_phrase} at {comp}."
            return f"Information security and application defense role safeguarding systems, models, and infrastructure against vulnerabilities at {comp}."
        elif 'backend' in t_lower or 'platform engineer' in t_lower or 'systems engineer' in t_lower:
            if resp_phrase:
                return f"Core backend and platform engineering role responsible for {resp_phrase} at {comp}."
            return f"Backend software engineering role designing distributed services, microservices, and reliable APIs at {comp}."
        elif 'frontend' in t_lower or 'full stack' in t_lower or 'fullstack' in t_lower or 'ui' in t_lower:
            if resp_phrase:
                return f"Fullstack and frontend engineering role building user-facing applications and interfaces for {resp_phrase} at {comp}."
            return f"Web application engineering role developing user interfaces, client components, and interactive experiences at {comp}."
        elif 'devops' in t_lower or 'sre' in t_lower or 'reliability' in t_lower or 'infrastructure' in t_lower:
            if resp_phrase:
                return f"Site reliability and platform operations role responsible for {resp_phrase} at {comp}."
            return f"DevOps and site reliability engineering role managing cloud infrastructure, CI/CD pipelines, and observability at {comp}."
        elif 'compiler' in t_lower or 'kernel' in t_lower:
            if resp_phrase:
                return f"Systems and compiler engineering role focused on {resp_phrase} at {comp}."
            return f"Low-level systems software role developing compilers, runtimes, and optimized execution passes at {comp}."
        else:
            if resp_phrase:
                return f"Software engineering role responsible for {resp_phrase} at {comp}."
            return f"Technical engineering role building software tools, backend platforms, and systems supporting AI products at {comp}."

    # 5. NON_AI_TECH
    elif cat == 'NON_AI_TECH':
        if 'it ' in t_lower or 'it operations' in t_lower or 'helpdesk' in t_lower or 'desktop' in t_lower or 'client platform' in t_lower:
            if resp_phrase:
                return f"Corporate IT systems engineering role focused on {resp_phrase} at {comp}."
            return f"Corporate IT operations role managing employee hardware fleets, identity provisioning, and enterprise desktop tools at {comp}."
        elif 'av ' in t_lower or 'audio' in t_lower or 'video' in t_lower:
            if resp_phrase:
                return f"Audio-visual systems engineering role responsible for {resp_phrase} at {comp}."
            return f"Corporate AV engineering role maintaining conferencing systems, conference room hardware, and event production at {comp}."
        elif 'network' in t_lower or 'sysadmin' in t_lower:
            if resp_phrase:
                return f"Enterprise network administration role responsible for {resp_phrase} at {comp}."
            return f"Internal corporate network engineering role maintaining office connectivity, VPNs, switches, and edge infrastructure at {comp}."
        else:
            if resp_phrase:
                return f"Enterprise IT and technical operations role responsible for {resp_phrase} at {comp}."
            return f"Traditional enterprise IT, business applications, and infrastructure engineering role at {comp}."

    # 6. NON_TECHNICAL
    elif cat == 'NON_TECHNICAL':
        if 'accounting' in t_lower or 'accountant' in t_lower or 'tax' in t_lower or 'audit' in t_lower or 'revenue' in t_lower:
            if resp_phrase:
                return f"Corporate accounting and financial compliance role responsible for {resp_phrase} at {comp}."
            return f"Accounting and tax compliance role managing corporate financial ledgers, month-end closing, and fiscal reporting at {comp}."
        elif 'finance' in t_lower or 'fp&a' in t_lower or 'financial analyst' in t_lower or 'treasury' in t_lower:
            if resp_phrase:
                return f"Corporate financial planning and analysis role responsible for {resp_phrase} at {comp}."
            return f"Strategic finance role building financial forecast models, operational budgets, and capital allocation analysis at {comp}."
        elif 'legal' in t_lower or 'counsel' in t_lower or 'attorney' in t_lower or 'compliance' in t_lower:
            if resp_phrase:
                return f"Legal counsel and corporate governance role focused on {resp_phrase} at {comp}."
            return f"Corporate legal role advising on commercial contracts, intellectual property, regulatory compliance, and risk mitigation at {comp}."
        elif 'recruiter' in t_lower or 'recruiting' in t_lower or 'talent' in t_lower or 'hr' in t_lower or 'people' in t_lower:
            if resp_phrase:
                return f"Talent acquisition and human resources role focused on {resp_phrase} at {comp}."
            return f"Human resources and talent operations role managing candidate sourcing, interview pipelines, and employee onboarding at {comp}."
        elif 'sales' in t_lower or 'account executive' in t_lower or 'business development' in t_lower or 'bdr' in t_lower or 'sdr' in t_lower:
            if resp_phrase:
                return f"Commercial sales and revenue generation role responsible for {resp_phrase} at {comp}."
            return f"Enterprise sales and commercial account management role driving revenue growth, pipeline generation, and customer acquisition at {comp}."
        elif 'marketing' in t_lower or 'communications' in t_lower or 'brand' in t_lower or 'pr ' in t_lower or 'content' in t_lower:
            if resp_phrase:
                return f"Marketing and external communications role focused on {resp_phrase} at {comp}."
            return f"Marketing strategy and brand management role executing corporate campaigns, messaging, and community outreach at {comp}."
        elif 'policy' in t_lower or 'government' in t_lower or 'regulatory' in t_lower:
            if resp_phrase:
                return f"Public policy and regulatory affairs role focused on {resp_phrase} at {comp}."
            return f"Government affairs and public policy role analyzing AI regulatory frameworks, legislative developments, and external relations at {comp}."
        elif 'operations' in t_lower or 'program manager' in t_lower or 'coordinator' in t_lower or 'logistics' in t_lower:
            if resp_phrase:
                return f"Business operations and program management role responsible for {resp_phrase} at {comp}."
            return f"Corporate operations and administrative management role driving cross-functional project execution and organizational cadences at {comp}."
        else:
            if resp_phrase:
                return f"Corporate operational role focused on {resp_phrase} at {comp}."
            return f"Business operational, administrative, or non-technical functional support role at {comp}."

    # 7. UNCERTAIN
    else:
        if resp_phrase:
            return f"Role with ambiguous technical scope involving {resp_phrase} at {comp}; categorized as uncertain pending further domain evidence."
        return f"Job title and description lack sufficient evidence to definitively confirm technical depth or specialized category at {comp}."

# Let's test this on our repeated records!
generated_reasons = []
for r in records:
    new_r = generate_specific_reason(r)
    generated_reasons.append(new_r)

new_counts = Counter(generated_reasons)
print(f"Old distinct reasons: {len(Counter(r['classificationReason'] for r in records))}")
print(f"New distinct reasons: {len(new_counts)}")
print(f"Max repeated count now: {new_counts.most_common(1)[0]}")
