import json
import re
from collections import defaultdict, Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

def generate_audit8_reason(r):
    title = r['jobTitle'].strip()
    cat = r['category'].strip()
    comp = r['companyName'].strip()
    desc = r.get('jobDescription', '') or ''
    t_lower = title.lower()
    jid = r.get('jobId', '')

    # =========================================================================
    # 1. CORE_AI_ML (259 records)
    # =========================================================================
    if cat == 'CORE_AI_ML':
        if 'resident' in t_lower or 'fellow' in t_lower:
            if 'safety' in t_lower or 'security' in t_lower:
                return "Conducts foundational research on model alignment, safety benchmarks, and empirical AI risk mitigation."
            if 'rl' in t_lower or 'reinforcement' in t_lower or 'systems' in t_lower:
                return "Conducts machine learning research on reinforcement learning algorithms and high-throughput training systems."
            return "Conducts foundational machine learning research and experimental modeling under researcher mentorship."
        
        if 'research scientist' in t_lower or 'applied scientist' in t_lower or 'ai scientist' in t_lower:
            if 'inference' in t_lower or 'optimization' in t_lower:
                return "Researches and develops algorithmic optimizations for efficient LLM inference and distributed model execution."
            if 'speech' in t_lower or 'audio' in t_lower:
                return "Conducts applied scientific research on speech recognition, acoustic modeling, and audio foundation models."
            if 'vision' in t_lower or 'multimodal' in t_lower:
                return "Researches and develops multimodal computer vision architectures and visual representation models."
            return "Conducts scientific research and algorithmic development to advance foundational AI model capabilities."
            
        if 'pretraining' in t_lower or 'pre-training' in t_lower:
            return "Scales distributed foundation model pre-training runs, data curation pipelines, and model architectures."
            
        if 'post-training' in t_lower or 'alignment' in t_lower or 'rlhf' in t_lower or 'fine-tuning' in t_lower:
            return "Implements model post-training, reinforcement learning from human feedback (RLHF), and behavioral alignment."
            
        if 'eval' in t_lower or 'evaluation' in t_lower or 'benchmarking' in t_lower:
            return "Develops automated evaluation frameworks, safety benchmarks, and capability assessment suites for AI models."
            
        if 'data scientist' in t_lower or 'data science' in t_lower:
            if 'nlp' in t_lower or 'llm' in t_lower or 'genai' in t_lower or 'ai' in t_lower:
                return "Builds statistical models, machine learning algorithms, and generative AI prototypes for analytical insights."
            return "Develops predictive machine learning models, statistical analyses, and data algorithms for product decisions."
            
        if 'solutions architect' in t_lower and ('genai' in t_lower or 'generative ai' in t_lower or 'ml' in t_lower):
            return "Serves as deep technical authority guiding Generative AI architectures, LLM fine-tuning, and applied machine learning."
            
        if 'forward deployed ai' in t_lower or 'forward deployed engineer' in t_lower:
            return "Designs, implements, and tunes machine learning algorithms and domain models for specialized client applications."
            
        if 'applied ai engineer' in t_lower or 'applied ai' in t_lower or 'ai engineer' in t_lower:
            if 'clinical' in t_lower or 'disease' in t_lower or 'life sciences' in t_lower or 'molecular' in t_lower:
                return "Applies foundation AI models and machine learning pipelines to solve complex biomedical and life sciences problems."
            if 'physical ai' in t_lower or 'robot' in t_lower:
                return "Develops and applies machine learning algorithms for physical robotics, control systems, and embodied AI."
            return "Develops, fine-tunes, and evaluates domain-specific AI models and applications for specialized use cases."
            
        if 'speech tester' in t_lower or 'data annotat' in t_lower or 'model test' in t_lower:
            return "Evaluates speech recognition model outputs, annotates linguistic datasets, and benchmarks acoustic accuracy."
            
        return "Designs, trains, and optimizes machine learning and deep learning models for core algorithmic AI systems."

    # =========================================================================
    # 2. AI_INFRASTRUCTURE (42 records)
    # =========================================================================
    if cat == 'AI_INFRASTRUCTURE':
        if 'demand planning' in t_lower or 'capacity' in t_lower or 'compute supply' in t_lower:
            return "Plans compute cluster demand, hardware capacity requirements, and operational infrastructure scaling for AI workloads."
            
        if 'data center' in t_lower or 'facility' in t_lower:
            if 'security' in t_lower:
                return "Secures physical data center facilities, operational environments, and compute cluster hardware footprints."
            if 'electrical' in t_lower:
                return "Designs and oversees electrical power distribution, substation feeds, and backup power for AI data centers."
            if 'mechanical' in t_lower:
                return "Designs and maintains mechanical cooling, chilled water systems, and HVAC airflow across AI data centers."
            if 'controls' in t_lower or 'automation' in t_lower:
                return "Develops and maintains building management systems (BMS) and programmable logic controllers for data centers."
            if 'power' in t_lower or 'microgrid' in t_lower:
                return "Engineers microgrid architectures, power generation systems, and utility interconnects for high-density AI clusters."
            if 'technician' in t_lower or 'operations' in t_lower:
                return "Performs physical server installation, hardware maintenance, cabling, and rack repairs in AI data center facilities."
            return "Designs and engineers mission-critical physical infrastructure, power, and cooling systems for AI data centers."
            
        if 'network' in t_lower or 'fabric' in t_lower or 'infiniband' in t_lower:
            return "Designs, optimizes, and maintains high-performance interconnect fabrics and data center networks for AI clusters."
            
        if 'inference' in t_lower or 'serving' in t_lower:
            return "Builds, manages, and scales high-throughput, low-latency inference serving platforms for foundation models."
            
        if 'cluster' in t_lower or 'gpu' in t_lower or 'compute infrastructure' in t_lower:
            return "Manages large-scale GPU accelerator clusters, compute node provisioning, and hardware performance tuning."
            
        if 'asic' in t_lower or 'silicon' in t_lower:
            return "Architects, designs, and verifies custom AI accelerator ASICs, interconnect topologies, and compute silicon."
            
        if 'kernel' in t_lower or 'driver' in t_lower:
            return "Develops high-performance kernel drivers, low-level system software, and hardware abstractions for accelerators."
            
        return "Engineers and operates large-scale compute clusters, high-performance hardware, and data center AI infrastructure."

    # =========================================================================
    # 3. AI_PRODUCT_SOLUTIONS (247 records)
    # =========================================================================
    if cat == 'AI_PRODUCT_SOLUTIONS':
        if jid in ['job_455248a218364d2e', 'job_8dc55042eeb084c9']:
            return "Cultivates technical relationships with global systems integrators and cloud providers to design and deploy enterprise Claude AI solutions."
        if jid == 'job_c9050c0a3328518c':
            return "Leads technical solutions architects deploying Claude AI models and enterprise integrations for healthcare and life sciences clients."
        if jid == 'job_a9ec78f057cc185f':
            return "Manages pre-sales solutions architects driving enterprise adoption of Claude API and developer tools across commercial accounts."
        if jid == 'job_dd881a420fc9e6b6':
            return "Leads technical solutions architects partnering with AI startups to architect, build, and deploy production applications on Claude."
            
        if 'solutions architect' in t_lower or 'applied ai architect' in t_lower or 'account solution' in t_lower:
            if 'manager' in t_lower or 'lead' in t_lower or 'director' in t_lower:
                return "Leads teams of technical solutions architects advising enterprise clients on generative AI architectures and deployments."
            if 'partner' in t_lower or 'gsi' in t_lower:
                return "Collaborates with systems integrators and cloud partners to architect, integrate, and deploy enterprise AI solutions."
            if 'health' in t_lower or 'life science' in t_lower:
                return "Partners with healthcare and life sciences enterprises to architect domain-specific AI solutions and compliant workflows."
            if 'public sector' in t_lower or 'government' in t_lower:
                return "Advises government and public sector organizations on architecting and deploying secure, compliant AI solutions."
            if 'data warehouse' in t_lower or 'edw' in t_lower or 'migration' in t_lower:
                return "Guides enterprise customers through legacy data warehouse migrations to modern lakehouse and AI platforms."
            return "Works with enterprise customers to design and deploy AI solutions and guide technical adoption."
            
        if 'forward deployed' in t_lower or 'fde' in t_lower:
            if 'intern' in t_lower:
                return "Collaborates with engineering teams to deploy, integrate, and test customer-facing AI agent solutions."
            if 'manager' in t_lower or 'director' in t_lower or 'lead' in t_lower:
                return "Leads forward-deployed engineering teams delivering custom AI applications and production integrations for clients."
            return "Partners directly with enterprise customers to build, customize, and productionize generative AI applications."
            
        if 'outcomes manager' in t_lower or 'customer success' in t_lower:
            return "Drives enterprise customer adoption, operational deployment, and business value realization for generative AI platforms."
            
        if 'product manager' in t_lower or 'product lead' in t_lower:
            return "Defines product strategy, technical roadmaps, and feature specifications for customer-facing AI applications."
            
        if 'developer' in t_lower and ('relations' in t_lower or 'advocate' in t_lower or 'devrel' in t_lower or 'community' in t_lower):
            return "Builds technical sample applications, developer documentation, and tutorials to drive adoption of AI platforms."
            
        if 'product designer' in t_lower or 'design' in t_lower:
            return "Designs user experiences, interaction models, and interfaces for enterprise AI software products."
            
        if 'field engineer' in t_lower:
            return "Provides deep technical field engineering support to help enterprise customers integrate and optimize AI workloads."
            
        return "Drives customer-facing technical architecture, deployment engineering, and client adoption of AI products."

    # =========================================================================
    # 4. AI_SUPPORTING_TECH (574 records)
    # =========================================================================
    if cat == 'AI_SUPPORTING_TECH':
        if 'data engineer' in t_lower:
            if 'billing' in t_lower or 'payment' in t_lower or 'finance' in t_lower:
                return "Builds and maintains data pipelines and reporting models supporting financial, billing, and operational systems."
            if 'gtm' in t_lower or 'sales' in t_lower or 'marketing' in t_lower:
                return "Designs and maintains data pipelines and analytics infrastructure supporting revenue and go-to-market teams."
            if 'recruiting' in t_lower or 'people' in t_lower or 'talent' in t_lower:
                return "Builds data pipelines and reporting models tracking talent acquisition metrics, hiring pipelines, and headcount."
            return "Builds and maintains data pipelines and data infrastructure supporting internal product and business teams."
            
        if 'hardware systems architect' in t_lower:
            return "Designs accelerator and compute hardware systems, including interconnects, memory architecture and performance."
            
        if 'autonomous systems security' in t_lower:
            return "Develops security controls for autonomous systems, including hardware, firmware and operational environments."
            
        if 'hardware' in t_lower and ('security' in t_lower or 'platform' in t_lower):
            return "Develops security controls, secure boot chains, and firmware hardening for compute hardware platforms."
            
        if 'hardware' in t_lower and 'design' in t_lower:
            return "Designs and verifies digital ASIC and hardware components for high-performance AI processors."
            
        if 'hardware' in t_lower and 'tpm' in t_lower:
            return "Manages hardware technical programs, vendor delivery, and deployment schedules for storage systems."
            
        if 'staff backline engineer' in t_lower or 'backline' in t_lower:
            return "Troubleshoots complex distributed system failures, model training errors, and ML platform escalations."
            
        if 'security' in t_lower or 'cyber' in t_lower or 'infosec' in t_lower or 'detection' in t_lower:
            return "Implements security controls, vulnerability management, and defensive systems protecting enterprise infrastructure."
            
        if 'devops' in t_lower or 'sre' in t_lower or 'reliability' in t_lower or 'fleet reliability' in t_lower:
            return "Maintains cloud infrastructure, CI/CD deployment pipelines, and observability systems to ensure platform reliability."
            
        if 'database' in t_lower or 'storage' in t_lower or 'delta' in t_lower or 'internals' in t_lower:
            return "Engineers database storage engine internals, distributed query optimizations, and data platform performance."
            
        if 'compiler' in t_lower or 'llvm' in t_lower or 'kernel' in t_lower or 'runtime' in t_lower:
            return "Develops compiler optimizations, system runtimes, and intermediate representations for accelerated compute."
            
        if 'performance' in t_lower or 'profil' in t_lower:
            return "Profiles, benchmarks, and optimizes execution throughput and latency across distributed computing systems."
            
        if 'agent evaluation' in t_lower or 'evals' in t_lower:
            return "Designs and runs benchmark evaluations assessing autonomous agent capabilities, tool use, and reliability."
            
        if 'agent' in t_lower and ('frontier agent' in t_lower or 'agent systems' in t_lower or 'agentic' in t_lower):
            return "Designs and builds software platforms, agentic execution runtimes, and developer tooling for AI agents."
            
        if 'automation' in t_lower:
            return "Develops automated software workflows, orchestration pipelines, and internal developer tooling."
            
        if 'growth' in t_lower:
            return "Develops software features, experimentation frameworks, and product telemetry to drive platform adoption."
            
        if 'data architect' in t_lower:
            return "Architects enterprise data models, data storage topologies, and analytics platform governance."
            
        if 'data foundation' in t_lower:
            return "Builds and maintains data foundation pipelines, data models, and go-to-market systems integrations."
            
        if 'design verification' in t_lower:
            return "Develops simulation testbenches, verification suites, and coverage models validating silicon designs."
            
        if 'android' in t_lower or 'ios' in t_lower or 'mobile' in t_lower:
            return "Develops native mobile applications, user interfaces, and client components for mobile platforms."
            
        if 'developer productivity' in t_lower or 'developer experience' in t_lower or 'devex' in t_lower:
            return "Builds developer tools, build systems, and internal engineering infrastructure to accelerate developer productivity."
            
        if 'knowledge work' in t_lower:
            return "Develops software platforms, enterprise integrations, and backend architectures enabling AI knowledge workflows."
            
        if 'intern' in t_lower or 'internship' in t_lower or 'new grad' in t_lower:
            return "Develops, tests, and debugs software features and backend tools under engineering team mentorship."
            
        if 'engineering manager' in t_lower or 'em ' in t_lower:
            return "Leads software engineering teams, technical project delivery, and engineering architecture."
            
        if 'business system' in t_lower:
            return "Develops and maintains internal business applications, CRM workflows, and enterprise systems integrations."
            
        if 'av engineer' in t_lower:
            return "Designs, integrates, and automates audio-visual systems and collaboration technology across corporate facilities."
            
        if 'frontend' in t_lower or 'full stack' in t_lower or 'fullstack' in t_lower or 'web' in t_lower or re.search(r'\bui\b', t_lower):
            return "Develops web applications, user interfaces, and interactive software tools supporting developer and user platforms."
            
        if re.search(r'\bqa\b', t_lower) or 'quality' in t_lower or 'test' in t_lower:
            return "Develops automated testing frameworks, end-to-end test suites, and quality validation pipelines."
            
        if 'tpm' in t_lower or 'technical program manager' in t_lower:
            return "Coordinates technical programs, cross-functional engineering deliverables, and software release timelines."
            
        if 'customer engineer' in t_lower or 'customer enablement' in t_lower:
            return "Provides technical customer engineering, onboarding support, and developer enablement for platforms."
            
        if 'cloud' in t_lower or 'cluster' in t_lower or 'compute' in t_lower or 'capacity' in t_lower or 'infrastructure' in t_lower:
            return "Builds and operates large-scale cloud compute platforms, containerized environments, and cluster resource managers."
            
        return "Designs, builds, and maintains backend services, distributed systems, and APIs supporting AI platforms."

    # =========================================================================
    # 5. NON_AI_TECH (111 records)
    # =========================================================================
    if cat == 'NON_AI_TECH':
        if jid == 'job_4b765b8c0dd9a693' or 'asset management' in t_lower:
            return "Manages corporate IT hardware lifecycle, inventory systems of record, and multi-office enterprise endpoint provisioning."
            
        if 'it support' in t_lower or 'helpdesk' in t_lower or 'desktop' in t_lower or 'it specialist' in t_lower:
            return "Provides technical support, endpoint management, and hardware troubleshooting for internal employees."
            
        if 'network' in t_lower or 'sysadmin' in t_lower or 'system administrator' in t_lower:
            return "Administers internal office networks, VPNs, directory services, and corporate technical infrastructure."
            
        if re.search(r'\bav\b', t_lower) or 'audio' in t_lower:
            return "Maintains corporate audiovisual systems and supports conference room technology and live events."
            
        if 'robotics' in t_lower or 'robot' in t_lower:
            return "Engineers robotics hardware interfaces, embedded software systems, and robotic automation platforms."
            
        if 'site reliability' in t_lower or 'sre' in t_lower:
            return "Maintains server infrastructure, system reliability, deployment pipelines, and cloud platform operations."
            
        if 'content systems' in t_lower:
            return "Develops and maintains content distribution systems, media platforms, and digital delivery pipelines."
            
        if 'internship' in t_lower or 'intern' in t_lower or 'new grad' in t_lower:
            return "Designs, develops, and tests software components and enterprise applications under team mentorship."
            
        if 'data engineer' in t_lower or 'analytics engineer' in t_lower:
            return "Builds and operates enterprise data warehouses, ETL processes, and internal business intelligence pipelines."
            
        if 'defense' in t_lower or 'apollo' in t_lower or 'backend' in t_lower or 'software engineer' in t_lower or 'developer' in t_lower:
            return "Designs, develops, and maintains enterprise software features, data workflows, and backend application services."
            
        return "Develops, maintains, and supports internal IT systems, enterprise applications, and corporate technology."

    # =========================================================================
    # 6. NON_TECHNICAL (580 records)
    # =========================================================================
    if cat == 'NON_TECHNICAL':
        if jid == 'job_e98b00bb44e6a41d':
            return "Leads revenue recognition under ASC 606, marketplace reconciliations, and SOX controls for cloud provider channels."
            
        if 'fellow' in t_lower or 'fellowship' in t_lower:
            if 'policy' in t_lower or 'economic' in t_lower:
                return "Conducts empirical economic research and policy analysis on frontier AI impacts and societal governance."
            if 'medical' in t_lower or 'medicine' in t_lower:
                return "Conducts clinical evaluation, biomedical research analysis, and domain assessments for AI applications."
            if 'finance' in t_lower:
                return "Conducts financial domain analysis, econometric modeling, and market evaluations for AI models."
            return "Conducts specialized non-technical domain research and policy analysis under fellowship mentorship."
            
        if 'accounting' in t_lower or 'accountant' in t_lower or 'close' in t_lower:
            if 'lease' in t_lower:
                return "Manages data center lease accounting, ASC 842 compliance, and capital infrastructure commitments."
            if 'revenue' in t_lower:
                return "Manages revenue recognition under ASC 606, customer billing reconciliations, and month-end close."
            return "Manages revenue recognition, financial reporting, accounting controls and audit readiness."
            
        if 'tax' in t_lower:
            return "Manages corporate tax compliance, statutory filings, indirect tax reporting, and tax audit readiness."
            
        if 'loan' in t_lower or 'credit' in t_lower or 'underwrit' in t_lower:
            return "Evaluates credit risk profiles, underwriting decisions, and borrower account compliance."
            
        if 'revenue operations' in t_lower or 'revops' in t_lower or 'order management' in t_lower:
            return "Manages revenue operations pipelines, sales analytics, and business intelligence reporting for commercial teams."
            
        if 'contract' in t_lower:
            return "Reviews, negotiates, and manages commercial vendor contracts, legal terms, and corporate agreements."
            
        if 'construction' in t_lower or 'energy' in t_lower or 'scheduler' in t_lower:
            return "Manages data center construction projects, project scheduling, utility interconnects, and vendor execution."
            
        if 'corporate development' in t_lower or 'm&a' in t_lower:
            return "Evaluates strategic mergers, acquisitions, venture investments, and corporate partnership opportunities."
            
        if 'data acquisition' in t_lower:
            return "Manages data licensing partnerships, dataset procurement, and data vendor acquisition agreements."
            
        if 'chief of staff' in t_lower:
            return "Drives strategic executive initiatives, financial leadership alignment, and operational execution."
            
        if 'benefits' in t_lower or 'compensation' in t_lower:
            return "Designs and administers employee compensation programs, total rewards, and health benefits packages."
            
        if 'finance' in t_lower or 'fp&a' in t_lower or 'treasury' in t_lower:
            if 'deal' in t_lower or 'pricing' in t_lower or 'velocity' in t_lower:
                return "Structures commercial contract pricing, margin models, and financial risk controls for enterprise transactions."
            return "Builds financial forecasts, operating budgets, and capital allocation models to guide business planning."
            
        if 'billing' in t_lower or 'payment' in t_lower:
            if 'data engineer' in t_lower:
                return "Builds and maintains financial data pipelines, billing models, and transaction reporting supporting corporate fiscal operations."
            return "Oversees customer billing operations, invoice generation, payment processing, and ledger reconciliations."
            
        if 'recruiter' in t_lower or 'recruiting' in t_lower or 'talent' in t_lower or 'sourcer' in t_lower or 'sourcing' in t_lower:
            if 'coordinator' in t_lower or 'operations' in t_lower:
                return "Coordinates candidate interview schedules, recruiting logistics, and applicant tracking workflows."
            return "Manages full-cycle recruiting, candidate sourcing pipelines, and hiring workflows across business functions."
            
        if re.search(r'\bhr\b', t_lower) or 'people' in t_lower or 'human resources' in t_lower or 'rewards' in t_lower or 'payroll' in t_lower:
            return "Administers employee relations, compensation programs, performance management, and people operations policies."
            
        if 'account manager' in t_lower:
            return "Manages existing commercial client relationships, account renewals, and customer growth."
            
        if 'sales' in t_lower or 'account executive' in t_lower or 'business development' in t_lower or 'bdr' in t_lower or 'sdr' in t_lower or 'renewals' in t_lower:
            if 'bdr' in t_lower or 'sdr' in t_lower or 'development rep' in t_lower:
                return "Generates qualified sales leads, conducts outbound prospecting, and initiates enterprise sales pipelines."
            if 'operations' in t_lower or 'enablement' in t_lower:
                return "Coordinates sales operations, commercial deal desks, customer renewal motions, and CRM data management."
            return "Manages enterprise sales cycles, client negotiations, and commercial contract execution."
            
        if 'partner' in t_lower or 'alliance' in t_lower:
            return "Manages strategic cloud partner relationships, co-selling motions, and enterprise go-to-market alliances."
            
        if 'deployment manager' in t_lower or 'activation manager' in t_lower or 'engagement manager' in t_lower:
            return "Coordinates enterprise customer onboarding, solution rollout timelines, and deployment workflows."
            
        if 'customer success' in t_lower or 'customer support' in t_lower or 'client success' in t_lower or 'support specialist' in t_lower or 'outcomes' in t_lower:
            return "Guides customer onboarding, relationship management, product adoption, and client retention."
            
        if 'marketing' in t_lower or 'communications' in t_lower or 'brand' in t_lower or re.search(r'\bpr\b', t_lower) or 'content' in t_lower or 'events' in t_lower:
            return "Develops marketing campaigns, brand messaging, content initiatives, and corporate communications."
            
        if 'legal' in t_lower or 'counsel' in t_lower or 'attorney' in t_lower or 'paralegal' in t_lower:
            return "Drafts and negotiates commercial contracts, advises on legal risk, and ensures corporate compliance."
            
        if 'grc' in t_lower or 'compliance' in t_lower or 'audit' in t_lower:
            return "Monitors regulatory compliance, conducts risk assessments, and maintains internal audit control frameworks."
            
        if 'external affairs' in t_lower or 'public affairs' in t_lower:
            return "Coordinates regional government relations, public policy engagement, and international stakeholder affairs."
            
        if 'protective intelligence' in t_lower or 'physical security' in t_lower:
            return "Analyzes physical security threats, geopolitical risks, and intelligence assessments to safeguard personnel and facilities."
            
        if 'director - u.s. midwest' in t_lower or 'facility operations' in t_lower:
            return "Directs regional data center facility operations, vendor management, physical site reliability, and infrastructure delivery."
            
        if 'system administrator' in t_lower or 'sysadmin' in t_lower:
            return "Administers internal corporate systems, user access permissions, and enterprise software infrastructure."
            
        if 'web strategy' in t_lower or 'web lead' in t_lower:
            return "Develops website architecture, digital marketing strategy, and online user engagement initiatives."
            
        if 'economist' in t_lower or 'economics' in t_lower or 'policy' in t_lower or 'government' in t_lower:
            return "Analyzes public policy developments, economic trends, and legislative frameworks for AI governance."
            
        if 'executive assistant' in t_lower or 'administrative' in t_lower:
            return "Provides executive administrative assistance, calendar coordination, and operational support to leadership."
            
        if 'executive briefing' in t_lower:
            return "Coordinates executive customer briefings, strategic technology demonstrations, and leadership meetings."
            
        if 'workplace' in t_lower or 'facilities' in t_lower or 'office' in t_lower:
            return "Oversees workplace facilities, office operations, space planning, and vendor services."
            
        if 'procurement' in t_lower or 'sourcing manager' in t_lower or 'purchasing' in t_lower or 'supply chain' in t_lower:
            return "Manages vendor contracts, hardware purchasing, procurement negotiation, and supply chain operations."
            
        if 'community engagement' in t_lower or 'stakeholder' in t_lower:
            return "Coordinates regional community relations, local government engagement, and public affairs for data center construction."
            
        if 'strategist' in t_lower or 'transformation' in t_lower:
            return "Advises executive stakeholders on enterprise AI strategy, organizational transformation, and roadmap planning."
            
        if 'quality assurance' in t_lower:
            return "Performs operational testing, workflow quality assurance, and data verification for business processes."
            
        if 'program manager' in t_lower or 'program management' in t_lower or 'enablement' in t_lower:
            return "Manages cross-functional program delivery, organizational planning cadences, and operational execution."
            
        if 'product design' in t_lower or 'creative' in t_lower or 'designer' in t_lower:
            return "Designs user interfaces, visual design systems, and product experience workflows."
            
        if 'av production' in t_lower or re.search(r'\bav\b', t_lower):
            return "Coordinates live event broadcasting, audio-visual technical production, and hybrid meeting operations."
            
        return "Coordinates cross-functional business operations, program delivery, and operational planning cadences."

    # =========================================================================
    # 7. UNCERTAIN (117 records)
    # =========================================================================
    return "Job title and description do not provide sufficient technical detail or domain specificity to classify into a definitive category."

if __name__ == '__main__':
    reasons = [generate_audit8_reason(r) for r in records]
    print(f"Total evaluated records: {len(reasons)}")
    print(f"Distinct reasons count: {len(set(reasons))}")
