import json
import re
from collections import Counter, defaultdict

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

def generate_audit9_reason(r):
    title = r['jobTitle'].strip()
    cat = r['category'].strip()
    comp = r['companyName'].strip()
    desc = r.get('jobDescription', '') or ''
    resp = r.get('responsibilityEvidence', '') or ''
    t_lower = title.lower()
    jid = r.get('jobId', '')

    # =========================================================================
    # 1. CORE_AI_ML (259 records)
    # =========================================================================
    if cat == 'CORE_AI_ML':
        if jid == 'job_ec2913967af6956d' or 'account manager' in t_lower:
            return "Manages technical client relationships, engineering partner alignment, and account growth across speech and AI machine learning teams."
            
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
            if 'nlp' in t_lower or 'llm' in t_lower or 'genai' in t_lower or re.search(r'\bai\b', t_lower):
                return "Builds statistical models, machine learning algorithms, and generative AI prototypes for analytical insights."
            return "Develops predictive machine learning models, statistical analyses, and data algorithms for product decisions."
            
        if 'solutions architect' in t_lower and ('genai' in t_lower or 'generative ai' in t_lower or re.search(r'\bml\b', t_lower)):
            return "Serves as deep technical authority guiding Generative AI architectures, LLM fine-tuning, and applied machine learning."
            
        if 'forward deployed ai' in t_lower or 'forward deployed engineer' in t_lower:
            return "Designs, implements, and tunes machine learning algorithms and domain models for specialized client applications."
            
        if 'applied ai engineer' in t_lower or 'applied ai' in t_lower or 'ai engineer' in t_lower:
            if 'clinical' in t_lower or 'disease' in t_lower or 'life sciences' in t_lower or 'molecular' in t_lower:
                return "Applies foundation AI models and machine learning pipelines to solve complex biomedical and life sciences problems."
            if 'physical ai' in t_lower or 'robot' in t_lower:
                return "Develops and applies machine learning algorithms for physical robotics, control systems, and embodied AI."
            return "Develops, fine-tunes, and evaluates domain-specific AI models and applications for specialized use cases."
            
        if 'speech' in t_lower or 'linguistic' in t_lower or 'acoustic' in t_lower:
            return "Evaluates speech recognition model outputs, annotates linguistic datasets, and fine-tunes audio models."
            
        return "Designs, trains, and optimizes machine learning and deep learning models for core algorithmic AI systems."

    # =========================================================================
    # 2. AI_INFRASTRUCTURE (42 records)
    # =========================================================================
    if cat == 'AI_INFRASTRUCTURE':
        if 'demand planning' in t_lower or 'compute supply' in t_lower:
            return "Plans compute cluster demand, hardware capacity requirements, and operational infrastructure scaling for AI workloads."
            
        if 'controls engineer' in t_lower or 'bms' in t_lower:
            return "Develops and maintains building management systems (BMS) and programmable logic controllers for data centers."
            
        if 'power generation' in t_lower or 'microgrid' in t_lower:
            return "Engineers microgrid architectures, power generation systems, and utility interconnects for high-density AI clusters."
            
        if 'mechanical engineer' in t_lower:
            return "Designs and maintains mechanical cooling, chilled water systems, and HVAC airflow across AI data centers."
            
        if 'electrical engineer' in t_lower:
            return "Designs and oversees electrical power distribution, substation feeds, and backup power for AI data centers."
            
        if 'data center technician' in t_lower or 'operations technician' in t_lower:
            return "Performs physical server installation, hardware maintenance, cabling, and rack repairs in AI data center facilities."
            
        if 'security engineer' in t_lower and 'data center' in t_lower:
            return "Secures physical data center facilities, operational environments, and compute cluster hardware footprints."
            
        if 'director, data center' in t_lower or 'field engineer, data center' in t_lower or 'business systems engineer, data center' in t_lower:
            return "Designs and engineers mission-critical physical infrastructure, power, and cooling systems for AI data centers."
            
        if 'network' in t_lower or 'asic network' in t_lower:
            return "Designs, optimizes, and maintains high-performance interconnect fabrics and data center networks for AI clusters."
            
        if 'asic' in t_lower or 'silicon' in t_lower:
            return "Architects, designs, and verifies custom AI accelerator ASICs, interconnect topologies, and compute silicon."
            
        if 'kernel' in t_lower or 'driver' in t_lower:
            return "Develops high-performance kernel drivers, low-level system software, and hardware abstractions for accelerators."
            
        if 'inference' in t_lower:
            return "Builds, manages, and scales high-throughput, low-latency inference serving platforms for foundation models."
            
        if 'cluster' in t_lower or 'gpu' in t_lower or 'compute infrastructure' in t_lower:
            return "Manages large-scale GPU accelerator clusters, compute node provisioning, and hardware performance tuning."
            
        return "Engineers and operates large-scale compute clusters, high-performance hardware, and data center AI infrastructure."

    # =========================================================================
    # 3. AI_PRODUCT_SOLUTIONS (247 records)
    # =========================================================================
    if cat == 'AI_PRODUCT_SOLUTIONS':
        if 'healthcare' in t_lower or 'life sciences' in t_lower or 'health' in t_lower:
            return "Partners with healthcare and life sciences enterprises to architect domain-specific AI solutions."
            
        if 'public sector' in t_lower or 'defense' in t_lower or 'government' in t_lower:
            return "Advises government and public sector organizations on architecting and deploying secure AI solutions."
            
        if 'gsi' in t_lower or 'global systems integrator' in t_lower:
            return "Cultivates technical relationships with global systems integrators and cloud partners to scale AI architectures."
            
        if 'partner' in t_lower or 'alliance' in t_lower or 'ecosystem' in t_lower:
            return "Collaborates with systems integrators and cloud partners to architect, integrate, and scale AI offerings."
            
        if 'migration' in t_lower or 'edw' in t_lower or 'warehouse' in t_lower:
            return "Guides enterprise customers through legacy data warehouse migrations to modern AI and analytics platforms."
            
        if 'solutions architect manager' in t_lower or 'manager, solutions architecture' in t_lower or 'director, solutions architecture' in t_lower or 'manager, specialist solutions architects' in t_lower:
            if 'engaged' in t_lower:
                return "Leads technical solutions architects deploying Claude AI models and enterprise integrations for key accounts."
            if 'greenfield' in t_lower or 'new' in t_lower:
                return "Manages pre-sales solutions architects driving enterprise adoption of Claude and API integrations."
            if 'startup' in t_lower:
                return "Leads technical solutions architects partnering with AI startups to architect scalable applications."
            return "Leads teams of technical solutions architects advising enterprise clients on generative AI architecture."
            
        if 'product manager' in t_lower or re.search(r'\bpm\b', t_lower):
            return "Defines product strategy, technical roadmaps, and feature specifications for customer-facing AI applications."
            
        if 'product designer' in t_lower or 'design' in t_lower:
            return "Designs user experiences, interaction models, and interfaces for enterprise AI software products."
            
        if 'developer advocate' in t_lower or 'devrel' in t_lower or 'advocacy' in t_lower:
            return "Builds technical sample applications, developer documentation, and tutorials for AI platforms."
            
        if 'field engineer' in t_lower:
            return "Provides deep technical field engineering support to help enterprise customers integrate and optimize solutions."
            
        if 'forward deployed' in t_lower or re.search(r'\bfde\b', t_lower):
            if 'lead' in t_lower or 'manager' in t_lower or 'director' in t_lower:
                return "Leads forward-deployed engineering teams delivering custom AI applications and production integrations."
            return "Partners directly with enterprise customers to build, customize, and productionize generative AI applications."
            
        if 'deployment' in t_lower or 'implementation' in t_lower:
            return "Drives enterprise customer adoption, operational deployment, and business value through AI technologies."
            
        if 'applied ai architect' in t_lower or 'solutions architect' in t_lower or 'solution architect' in t_lower:
            return "Works with enterprise customers to design and deploy AI solutions and guide technical adoption."
            
        if 'customer' in t_lower and ('engineer' in t_lower or 'architect' in t_lower):
            return "Drives customer-facing technical architecture, deployment engineering, and platform integration."
            
        return "Works with enterprise customers to design and deploy AI solutions and guide technical adoption."

    # =========================================================================
    # 4. AI_SUPPORTING_TECH (574 records)
    # =========================================================================
    if cat == 'AI_SUPPORTING_TECH':
        # Substring bug fix: intern in Internal Products
        if jid == 'job_0f1a3c2b1fd42054' or ('internal products' in t_lower and 'staff' in t_lower):
            return "Builds internal developer platforms, core engineering infrastructure, and enterprise tools for engineering teams."

        # Specific prompt targets in the 282 backend cluster:
        if 'developer education' in t_lower:
            return "Develops technical curriculum, developer documentation, sample projects, and educational workshops for developer platforms."
        if 'field executive architect' in t_lower:
            return "Advises strategic enterprise executive leaders on AI architecture adoption, deployment strategy, and technical governance."
        if ('front end' in t_lower or 'frontend' in t_lower) and 'marketing' in t_lower:
            return "Develops user interfaces, web components, and client-facing web applications for corporate digital properties."
        if 'incident response' in t_lower:
            return "Coordinates incident response workflows, operational readiness cadences, and system recovery across product and engineering services."
        if 'it systems engineer' in t_lower or 'client platform' in t_lower:
            if 'chromeos' in t_lower:
                return "Manages corporate ChromeOS endpoint fleets, device provisioning pipelines, and client system policies."
            if 'macos' in t_lower:
                return "Manages enterprise macOS client platforms, automated device management profiles, and endpoint security standards."
            if 'm&a' in t_lower:
                return "Leads IT systems integration, corporate directory consolidation, and infrastructure migration for mergers and acquisitions."
            return "Designs and maintains enterprise IT systems, identity integrations, and corporate software infrastructure."
        if 'corporate network' in t_lower:
            return "Architects and maintains internal corporate network infrastructure, enterprise firewalls, and office connectivity systems."
        if 'red team' in t_lower:
            return "Executes adversarial red-teaming assessments, vulnerability evaluations, and safeguard testing on AI systems."
        if 'salesforce' in t_lower:
            return "Develops custom Salesforce integrations, Apex workflows, and CRM applications supporting business operations."

        # Substring collision fix: 'em ' in 'system '
        if jid == 'job_bec8dd7b8a39dd3e' or ('ai infrastructure system engineer' in t_lower and not any(k in t_lower for k in ['manager', 'director', 'lead', 'head'])):
            return "Designs, deploys, and maintains AI compute cluster infrastructure, GPU host systems, and system hardware interfaces."
        if jid == 'job_01ed47f989ac45e0' or 'rack system integration' in t_lower:
            return "Leads rack-level hardware system integration, power delivery validation, and thermal packaging for AI acceleration clusters."
        if jid == 'job_79cb69d5bcd03bd9' or ('business system engineer' in t_lower and not any(k in t_lower for k in ['manager', 'director', 'lead', 'head'])):
            return "Designs, implements, and integrates enterprise business systems, internal application tooling, and corporate data workflows."

        # HR / People Business Partner in AI_SUPPORTING_TECH:
        if 'people business partner' in t_lower:
            return "Partners with engineering leadership on organizational talent planning, workforce strategy, and team development."

        # Data engineering roles in AI_SUPPORTING_TECH:
        if 'data engineer' in t_lower:
            if 'billing' in t_lower or 'payment' in t_lower or 'finance' in t_lower:
                return "Builds and maintains data pipelines and reporting models supporting financial, billing, and operational systems."
            if 'gtm' in t_lower or 'sales' in t_lower or 'marketing' in t_lower:
                return "Designs and maintains data pipelines and analytics infrastructure supporting revenue and go-to-market teams."
            if 'recruiting' in t_lower or 'people' in t_lower or 'talent' in t_lower:
                return "Builds data pipelines and reporting models tracking talent acquisition metrics, hiring pipelines, and headcount."
            return "Builds and maintains data pipelines and data infrastructure supporting internal product and business teams."

        # Delta Lake storage internals:
        if 'delta' in t_lower and 'engineer' in t_lower:
            return "Engineers distributed storage protocols, transaction log internals, and query performance for Delta Lake."

        # Storage / Object storage / Storage I/O:
        if 'storage' in t_lower and ('engineer' in t_lower or 'architect' in t_lower):
            return "Architects and maintains high-throughput distributed file systems, object storage architectures, and storage I/O subsystems."

        # Database engine internals:
        if 'database engine internals' in t_lower or 'storage engine' in t_lower or 'query optimization' in t_lower:
            return "Engineers database storage engine internals, distributed query optimizations, and data platform performance."
        if 'databases' in t_lower and 'engineer' in t_lower:
            return "Engineers distributed database clusters, replication topologies, and high-performance transactional engines."

        # Runtime engineering:
        if 'runtime' in t_lower and 'engineer' in t_lower:
            return "Engineers high-throughput runtime execution engines, distributed task schedulers, and execution abstractions."

        # Compiler engineering:
        if 'compiler' in t_lower:
            return "Architects compiler optimization passes, code generation pipelines, and hardware execution backends."

        # Backline / L3 support escalations:
        if 'staff backline engineer' in t_lower or 'backline' in t_lower:
            return "Troubleshoots complex distributed system failures, model training errors, and ML platform escalations."

        # AV / Audio-Visual:
        if 'av engineer' in t_lower or 'audio-visual' in t_lower:
            return "Designs, integrates, and automates audio-visual systems and collaboration technology across corporate facilities."

        # Mobile development:
        if 'android' in t_lower or 'ios' in t_lower or 'mobile' in t_lower:
            return "Develops native mobile applications, user interfaces, and client components for mobile platforms."

        # Developer productivity / experience:
        if 'developer productivity' in t_lower or 'developer experience' in t_lower or 'devex' in t_lower or 'developer acceleration' in t_lower or 'ai developer tooling' in t_lower:
            return "Builds developer tools, build systems, and internal engineering infrastructure to accelerate developer productivity."

        # Growth engineering:
        if 'growth' in t_lower and 'engineer' in t_lower:
            return "Develops software features, experimentation frameworks, and product telemetry to drive platform adoption."

        # Automation engineering:
        if 'automation' in t_lower and 'engineer' in t_lower:
            return "Develops automated software workflows, orchestration pipelines, and internal developer tooling."

        # Specialized sub-disciplines in 282:
        if 'bioinformatics' in t_lower:
            return "Develops computational biology algorithms, genomic data processing pipelines, and bioinformatic analysis tools."
        if 'privacy' in t_lower and 'engineer' in t_lower:
            return "Engineers privacy-preserving technical architectures, data governance frameworks, and data protection controls."
        if 'conversational design' in t_lower or 'demo engineer' in t_lower:
            return "Designs interactive AI demonstrations, proof-of-concept conversational interfaces, and technical customer prototypes."
        if 'functional architect' in t_lower:
            return "Architects AI-assisted software engineering practices, developer workflows, and R&D development automation."
        if 'gtm engineer' in t_lower:
            return "Architects go-to-market systems integrations, revenue data pipelines, and internal AI-native commercial tooling."
        if 'strategic partnerships' in t_lower or 'global systems integrators' in t_lower:
            return "Leads technical alliance strategy, co-engineering initiatives, and go-to-market execution with global systems integrators."
        if 'japan chief architect' in t_lower:
            return "Defines chip and system architectures, silicon specifications, and hardware roadmap alignment for Japanese enterprise markets."
        if 'japan engineering lead' in t_lower:
            return "Leads regional engineering delivery, technical program alignment, and cross-functional hardware-software coordination."
        if 'knowledge architect' in t_lower:
            return "Architects technical knowledge management platforms, engineering documentation schemas, and organizational information systems."
        if 'voice experience' in t_lower:
            return "Architects real-time voice streaming systems, low-latency audio pipelines, and conversational agent interfaces."
        if 'marketing engineer' in t_lower:
            return "Engineers marketing automation systems, digital web infrastructure, and technical SEO platforms."
        if 'technical marketing' in t_lower:
            return "Develops technical product demonstrations, developer tutorials, and engineering content for platform capabilities."
        if 'technical sourcer' in t_lower:
            return "Develops technical sourcing pipelines, talent identification strategies, and candidate outreach for engineering hiring."
        if 'engineering program coordinator' in t_lower:
            return "Coordinates engineering execution schedules, project milestones, and technical delivery cadences across infrastructure teams."
        if 'due diligence design' in t_lower:
            return "Performs technical due diligence, electrical and civil engineering feasibility assessments for data center acquisitions."
        if 'white space design' in t_lower:
            return "Designs mission-critical data center white space layouts, power distributions, and structural containment architectures."
        if 'data center operational excellence' in t_lower:
            return "Develops standard operating procedures, technical documentation standards, and operational excellence frameworks for data centers."
        if 'thermal engineer' in t_lower:
            return "Designs and optimizes liquid cooling architectures, thermal management systems, and heat dissipation for high-density GPU clusters."
        if 'electrical engineer' in t_lower:
            return "Designs server electrical architectures, power distribution boards, and high-current power delivery systems for compute clusters."
        if 'hardware' in t_lower and 'design' in t_lower:
            return "Designs and verifies digital ASIC and hardware components for high-performance AI processors."
        if 'screen recording' in t_lower or 'windows native' in t_lower:
            return "Develops high-performance native Windows client software, screen capture pipelines, and desktop recording architectures."
        if 'support systems specialist' in t_lower or 'sme, support systems' in t_lower:
            return "Manages support routing infrastructure, ticketing automation, and workforce tooling for contributor support operations."
        if 'technical support' in t_lower or 'support engineer' in t_lower or 'designated support' in t_lower:
            if 'bare metal' in t_lower:
                return "Provides deep technical troubleshooting, hardware diagnostic support, and incident resolution for bare-metal compute fleets."
            if 'inference' in t_lower:
                return "Provides tier-3 technical support, model inference troubleshooting, and API debugging for enterprise customers."
            if 'govops' in t_lower or 'government' in t_lower:
                return "Provides technical support, security compliance troubleshooting, and operational maintenance for public sector enclaves."
            if 'forge' in t_lower:
                return "Provides technical customer support, cluster diagnostic engineering, and issue remediation for cloud compute platforms."
            return "Provides dedicated technical support, API troubleshooting, and system diagnostic engineering for enterprise customers."
        if 'partner engineer' in t_lower:
            return "Leads technical partner co-engineering, cloud integration architecture, and joint engineering initiatives."
        if 'search ranking' in t_lower or 'search platform' in t_lower:
            return "Engineers machine learning search infrastructure, retrieval ranking algorithms, and discovery systems."
        if 'money' in t_lower or 'commercialisation' in t_lower:
            return "Engineers financial transaction infrastructure, billing engines, and commercial subscription services."
        if 'ai gateway' in t_lower:
            return "Engineers high-throughput AI API gateway infrastructure, request rate-limiting, and model routing layers."
        if 'customer engagement' in t_lower or 'docs platform' in t_lower:
            return "Builds user engagement analytics platforms, documentation delivery services, and customer feedback infrastructure."
        if 'continuous integration' in t_lower or re.search(r'\bci\b', t_lower) and 'cd' not in t_lower and 'engineer' in t_lower:
            return "Builds automated continuous integration pipelines, test orchestration infrastructure, and developer productivity tooling."
        if 'code rl' in t_lower:
            return "Builds scalable reinforcement learning execution environments and agentic code generation harnesses."
        if 'claude code' in t_lower:
            return "Builds developer tooling infrastructure, terminal-based agent runtimes, and interactive programming interfaces."
        if 'vector index' in t_lower or 'vectordb' in t_lower:
            return "Engineers distributed vector database indexing architectures, approximate nearest neighbor search, and retrieval engines."
        if 'pki' in t_lower:
            return "Designs and operates public key infrastructure, cryptographic certificate management, and hardware security modules."
        if 'applied training' in t_lower:
            return "Builds scalable distributed training environments, cluster onboarding automation, and GPU workload initialization platforms."
        if 'payment fraud' in t_lower:
            return "Engineers automated fraud detection systems, transaction verification pipelines, and payment risk models."
        if 'experimentation' in t_lower:
            return "Builds statistical experimentation frameworks, A/B testing infrastructure, and feature flagging platforms."
        if 'memory & search' in t_lower:
            return "Engineers long-term memory architectures, stateful retrieval layers, and distributed search indexing for AI models."
        if 'ml sampling path' in t_lower or 'sampling path' in t_lower:
            return "Optimizes low-latency machine learning sampling pipelines, token generation kernels, and inference execution paths."
        if 'enterprise connectivity' in t_lower or 'platform connectivity' in t_lower:
            return "Engineers enterprise data connectivity protocols, secure ingress pipelines, and API integrations for client platforms."
        if 'platform distribution' in t_lower or 'platform portability' in t_lower:
            return "Engineers cross-cloud platform deployment frameworks, container portability, and distributed distribution systems."
        if 'platform intelligence' in t_lower or 'platform safety' in t_lower:
            return "Builds platform safety controls, automated policy enforcement mechanisms, and intelligent platform monitoring."
        if 'platform acceleration' in t_lower:
            return "Accelerates core platform service performance, distributed RPC throughput, and platform runtime efficiency."
        if 'claude science' in t_lower:
            return "Engineers scientific research workflows, data visualization platforms, and computational tooling for AI models."
        if 'claude design' in t_lower:
            return "Develops interactive design systems, collaborative UI tools, and frontend design architecture for AI platforms."
        if 'support technology' in t_lower:
            return "Engineers customer support tooling, automated issue routing infrastructure, and agent diagnostic platforms."
        if 'beneficial deployments' in t_lower:
            return "Builds reliable software platforms, data integrations, and tooling for beneficial public-interest AI deployments."
        if 'labs' in t_lower:
            return "Develops exploratory product prototypes, experimental software architectures, and novel AI application workflows."
        if 'research productivity' in t_lower or 'research tools' in t_lower:
            return "Builds internal developer platforms, compilation tools, and workflow automation accelerating research productivity."
        if 'people products' in t_lower:
            return "Develops internal people operations software, employee directory systems, and HR technology workflows."
        if 'consumer' in t_lower and 'engineer' in t_lower:
            return "Builds consumer-facing application features, user session management, and responsive frontend-backend workflows."
        if 'enterprise ai products' in t_lower or 'enterprise (platform)' in t_lower:
            return "Engineers enterprise security controls, administrative consoles, and tenant isolation for enterprise AI platforms."
        if 'search' in t_lower and 'engineer' in t_lower:
            return "Engineers machine learning search infrastructure, retrieval ranking algorithms, and discovery systems."
        if 'kubernetes' in t_lower:
            return "Develops Kubernetes core extensions, custom resource definitions, and container cluster management controllers."
        if 'source control' in t_lower:
            return "Builds automated code governance pipelines, source control integrations, and compliance policy enforcement tooling."
        if 'ingestion core' in t_lower:
            return "Engineers high-throughput data ingestion pipelines, streaming connectors, and distributed buffer architectures."
        if 'arc team' in t_lower or 'arc software' in t_lower:
            return "Engineers distributed architecture, compute cluster reliability, and system resilience across AI compute platforms."
        if 'ecommerce' in t_lower or 'e-commerce' in t_lower:
            return "Develops scalable e-commerce software backends, shopping catalog integrations, and transaction systems."
        if 'observability' in t_lower or 'monitoring' in t_lower:
            return "Engineers high-scale observability pipelines, distributed tracing services, and metrics collection infrastructure."
        if 'threat and abuse' in t_lower or 'account abuse' in t_lower or 'account creation' in t_lower:
            return "Engineers automated abuse detection systems, account fraud prevention pipelines, and security defense mechanisms."
        if 'auth' in t_lower or 'identity' in t_lower or 'iam' in t_lower:
            return "Engineers enterprise identity and access management (IAM) services, authentication protocols, and authorization controls."
        if 'caching' in t_lower:
            return "Engineers ultra-low latency distributed caching tiers, memory-mapped key-value stores, and cache coherence protocols."
        if 'sandboxing' in t_lower or 'sandboxes' in t_lower:
            return "Builds secure multi-tenant execution sandboxes, container isolation runtimes, and virtualization security layers."
        if 'tokens' in t_lower or 'prompt structures' in t_lower:
            return "Engineers tokenization pipelines, prompt formatting runtimes, and context window management services."
        if 'datacenter server lifecycle' in t_lower or 'server lifecycle' in t_lower or 'metaldev' in t_lower:
            return "Builds automation services and provisioning software managing the bare-metal lifecycle of GPU datacenter servers."
        if 'perf and benchmarking' in t_lower or 'benchmarking' in t_lower or 'performance engineer' in t_lower:
            return "Develops Kubernetes-native benchmarking services to measure latency, throughput, and hardware efficiency across GPU clusters."
        if 'distributed data systems' in t_lower or 'data systems' in t_lower:
            return "Architects and implements high-throughput distributed data storage engines, replication protocols, and storage runtimes."
        if 'autonomous systems' in t_lower:
            return "Engineers mission software, autonomous command-and-control architectures, and real-time distributed edge platforms."
        if 'physical ai' in t_lower:
            return "Builds infrastructure platforms and software runtimes for physical AI, robotics telemetry, and embodied systems."
        if 'ai workload orchestration' in t_lower or 'orchestration platform' in t_lower:
            return "Designs Kubernetes-native workload orchestration services, scheduling runtimes, and cluster provisioning pipelines."
        if 'inference platform' in t_lower or 'inference serving' in t_lower or 'inference velocity' in t_lower or 'inference path' in t_lower or 'genai inference' in t_lower or 'inference' in t_lower:
            return "Engineers high-performance, low-latency model inference serving engines, dynamic request batching, and GPU kernel optimizations."
        if 'agent' in t_lower:
            if 'shopping' in t_lower:
                return "Engineers backend microservices, real-time merchant integrations, and commerce workflows for shopping AI agents."
            if 'oversight' in t_lower:
                return "Engineers observability platforms, behavioral evaluation pipelines, and oversight infrastructure for production AI agents."
            if 'voice' in t_lower:
                return "Engineers low-latency audio streaming infrastructure, voice agent runtimes, and telephony protocol integrations."
            if 'systems' in t_lower or 'agentic' in t_lower or 'frontier agent' in t_lower:
                return "Designs and builds software platforms, agentic execution runtimes, and developer tooling for AI agents."
            return "Builds execution runtimes, tool-integration protocols, and scalable backend platforms for autonomous AI agents."
        if 'weaved' in t_lower or 'weave' in t_lower:
            return "Engineers observability, evaluation, and monitoring platforms for AI agents and generative AI applications."
        if 'weights & biases' in t_lower or 'w&b' in t_lower:
            return "Engineers core experimentation tracking platforms, artifact repositories, and ML workflow orchestration systems."
        if 'sambarack' in t_lower or 'sambastack' in t_lower:
            return "Engineers hardware-software platform integration, reconfigurable dataflow architectures, and rack-scale compute systems."
        if 'model bring-up' in t_lower:
            return "Engineers open-weight model bring-up frameworks, model conversion pipelines, and runtime execution optimizations."
        if 'validation & si' in t_lower:
            return "Performs signal integrity modeling, measurement correlation, and high-speed electrical validation for silicon platforms."
        if 'dft' in t_lower:
            return "Designs design-for-test (DFT) logic, scan architectures, and automated test pattern generation for AI acceleration silicon."
        if 'design verifiction' in t_lower or 'design verification' in t_lower:
            return "Develops verification testbenches, simulation models, and coverage frameworks validating complex silicon IP."
        if 'place and route' in t_lower or 'pnr' in t_lower:
            return "Develops automated partitioning, placement, and routing algorithms for reconfigurable dataflow silicon architectures."
        if 'post-silicon' in t_lower:
            return "Executes post-silicon bring-up, high-speed IO validation, and diagnostic firmware debugging for AI processor chips."
        if 'vlsi' in t_lower or 'vls ' in t_lower or 'circuits' in t_lower:
            return "Designs VLSI circuits, high-speed custom macro layouts, and power-grid distribution for AI accelerator chips."
        if 'product strategy lead' in t_lower:
            return "Drives product strategy, technical roadmaps, and platform feature priorities for developer-facing AI platforms."
        if 'data architect' in t_lower:
            return "Architects enterprise data models, data storage topologies, and analytics platform governance."
        if 'product engineer' in t_lower:
            if 'education' in t_lower:
                return "Designs and develops educational software products, interactive learning tools, and platform user interfaces."
            return "Engineers end-to-end product features, full-stack user workflows, and customer-facing application services."
        if 'rtl design' in t_lower:
            return "Designs RTL microarchitectures, digital logic, and memory subsystem controllers for high-performance AI silicon."
        if 'silicon' in t_lower or 'firmware' in t_lower:
            return "Develops low-level silicon firmware, hardware abstraction layers, and board bring-up software for compute devices."
        if 'front end' in t_lower or 'frontend' in t_lower or 'full-stack' in t_lower or 'full stack' in t_lower or 'fullstack' in t_lower or 'web' in t_lower or re.search(r'\bui\b', t_lower):
            return "Develops web applications, user interfaces, and interactive software tools supporting developer and user platforms."
        if 'solutions architect' in t_lower or 'solutions engineer' in t_lower or 'forward deployment' in t_lower:
            return "Architects and deploys customer-facing AI solutions, technical enterprise integrations, and platform deployments."
        if 'systems phd' in t_lower:
            return "Conducts systems-level research and software engineering to optimize distributed data processing and AI engines."
        if 'systems engineer' in t_lower or 'system engineer' in t_lower:
            if 'virtualization' in t_lower:
                return "Engineers bare-metal host virtualization layers, hypervisor interfaces, and kernel software bridging AI workloads."
            return "Develops host software stacks, OS provisioning systems, and kernel-level infrastructure managing compute servers."
        if 'product sandboxing' in t_lower:
            return "Engineers secure execution environments and container runtimes isolating untrusted code executed by AI agents."
        if 'stem' in t_lower:
            return "Engineers scientific computing integrations, numerical evaluation environments, and STEM reasoning infrastructure for AI models."
        if 'safeguards human review' in t_lower or 'safeguards data' in t_lower or 'safeguards evals' in t_lower or 'safeguards' in t_lower:
            return "Engineers safety oversight platforms, human review annotation tools, and compliance data pipelines."
        if 'access programs' in t_lower:
            return "Engineers access control platforms, customer provisioning workflows, and gated entitlement systems for AI models."
        if 'productivity platforms' in t_lower:
            return "Develops enterprise productivity tools, collaboration platforms, and internal workflow automations."
        if 'business technology' in t_lower:
            return "Develops and maintains internal business applications, CRM workflows, and enterprise systems integrations."
        if 'deployment' in t_lower and 'staff' in t_lower:
            return "Engineers automated software deployment pipelines, blue-green release controllers, and fleet orchestration systems."
        if 'software architect' in t_lower or 'principal architect' in t_lower:
            return "Architects distributed software systems, system reliability frameworks, and cross-platform technical roadmaps."
        if 'technical architect' in t_lower:
            return "Guides enterprise engineering organizations on adopting AI coding assistants, software architectures, and automated development workflows."
        if 'rl environments' in t_lower:
            return "Designs and builds scalable reinforcement learning simulation environments and agent training runtimes."
        if 'knowledge work' in t_lower:
            return "Develops software platforms, enterprise integrations, and backend architectures enabling AI knowledge workflows."
        if 'gtm ai engineering' in t_lower:
            return "Builds internal AI agents, automated workflow pipelines, and enterprise systems powering commercial operations."
        if 'scaling' in t_lower:
            return "Architects distributed system scaling, traffic load balancing, and capacity expansion across compute clusters."
        if 'public sector' in t_lower or 'gps' in t_lower:
            return "Engineers mission-critical software architectures, operational data pipelines, and public sector AI deployments."
        if 'defense' in t_lower:
            return "Develops mission-critical defense software, secure application workflows, and AI integration services."
        if 'production engineer' in t_lower:
            return "Engineers high-reliability production environments, automated deployment pipelines, and infrastructure health monitoring."
        if 'platform engineer manager' in t_lower or 'platform engineer' in t_lower:
            return "Engineers resilient platform infrastructure, cloud runtime environments, and core services for enterprise AI systems."
        if 'field engineering' in t_lower and any(k in t_lower for k in ['manager', 'director', 'lead']):
            return "Leads field engineering teams delivering custom AI solutions, customer integrations, and technical architectures."
        if 'security' in t_lower or 'cyber' in t_lower or 'infosec' in t_lower:
            return "Implements security controls, vulnerability management, and defensive systems protecting enterprise infrastructure."
        if 'sre' in t_lower or 'site reliability' in t_lower or 'reliability engineer' in t_lower or 'fleet reliability' in t_lower or 'cloud reliability' in t_lower or 'devops' in t_lower:
            return "Maintains cloud infrastructure, CI/CD deployment pipelines, and observability systems to ensure platform reliability."
        if re.search(r'\bqa\b', t_lower) or 'quality' in t_lower or 'test' in t_lower:
            return "Develops automated testing frameworks, end-to-end test suites, and quality validation pipelines."
        if 'tpm' in t_lower or 'technical program manager' in t_lower:
            return "Coordinates technical programs, cross-functional engineering deliverables, and software release timelines."
        if 'customer engineer' in t_lower or 'customer enablement' in t_lower:
            return "Provides technical customer engineering, onboarding support, and developer enablement for platforms."
        if 'cloud' in t_lower or 'cluster' in t_lower or 'compute' in t_lower or 'capacity' in t_lower or 'infrastructure' in t_lower:
            return "Builds and operates large-scale cloud compute platforms, containerized environments, and cluster resource managers."
        if ('engineering manager' in t_lower or (('manager' in t_lower or 'director' in t_lower or 'vp' in t_lower) and 'engineering' in t_lower)) and not any(k in t_lower for k in ['system engineer', 'systems engineer', 'field engineering', 'network engineering', 'server lifecycle', 'data center']):
            return "Leads software engineering teams, technical project delivery, and engineering architecture."
        if re.search(r'\bintern\b|\binternship\b|\bnew grad\b', t_lower) and not any(k in t_lower for k in ['staff', 'senior', 'principal', 'lead']):
            return "Develops, tests, and debugs software features and backend tools under engineering team mentorship."

        return "Designs, builds, and maintains backend services, distributed systems, and APIs supporting AI platforms."

    # =========================================================================
    # 5. NON_AI_TECH (111 records)
    # =========================================================================
    if cat == 'NON_AI_TECH':
        if jid == 'job_4b765b8c0dd9a693' or 'asset management' in t_lower:
            return "Manages corporate IT hardware lifecycle, inventory systems of record, and multi-office enterprise endpoint provisioning."
            
        if 'it support' in t_lower or 'helpdesk' in t_lower or 'desk support' in t_lower or 'technical support specialist' in t_lower:
            return "Provides technical support, endpoint management, and hardware troubleshooting for internal employees."
            
        if 'robotics' in t_lower or 'robot' in t_lower or 'mechatronics' in t_lower:
            if 'mechatronics' in t_lower or 'humanoid' in t_lower:
                return "Designs mechatronic actuators, sensor integration, and precision robotic head mechanisms for humanoid robots."
            return "Engineers robotics hardware interfaces, embedded software systems, and robotic automation platforms."
            
        if 'sre' in t_lower or 'devops' in t_lower or 'infrastructure' in t_lower or 'site reliability' in t_lower:
            return "Manages server infrastructure, system reliability, deployment pipelines, and cloud platform operations."
            
        if 'content systems' in t_lower:
            return "Develops and maintains content distribution systems, media platforms, and digital delivery pipelines."
            
        if re.search(r'\bintern\b|\binternship\b|\bnew grad\b|\bgraduate\b', t_lower):
            if 'civil' in t_lower or 'architecture' in t_lower:
                return "Applies computational design software and AI-assisted modeling tools to architectural building plans."
            return "Designs, develops, and tests software components and enterprise applications under team mentorship."
            
        if 'data engineer' in t_lower or 'analytics engineer' in t_lower:
            return "Builds and operates enterprise data warehouses, ETL processes, and internal business intelligence pipelines."

        # Specific roles in NON_AI_TECH that need role-specific reasons:
        if 'langfuse' in t_lower or 'integrations' in t_lower:
            return "Builds open-source LLM observability SDKs, developer integrations, and telemetry tooling for AI applications."
        if 'r&d engineer' in t_lower or 'model training' in t_lower:
            return "Conducts applied research, model training experimentation, and deep learning pipeline development."
        if 'fabric architect' in t_lower:
            return "Architects high-performance AI network fabrics, RDMA routing topologies, and data center switching architectures."
        if 'manufacturing engineer' in t_lower:
            return "Optimizes manufacturing assembly processes, automated production equipment, and hardware manufacturing quality."
        if 'founding engineer' in t_lower:
            return "Architects zero-to-one product software, core technology stacks, and application features for an early-stage startup."
        if 'cloud architect' in t_lower:
            return "Architects multi-cloud infrastructure environments, container platforms, and enterprise cloud migrations."
        if 'genai engineer' in t_lower:
            return "Designs, builds, and deploys generative AI application pipelines, prompt workflows, and model integrations."
        if 'bare metal' in t_lower or 'linux & kubernetes' in t_lower:
            return "Engineers Linux operating system internals, bare-metal Kubernetes clusters, and low-level compute platforms."
        if 'cloud and platform' in t_lower or 'platform engineer' in t_lower:
            return "Builds and maintains cloud computing environments, Kubernetes platforms, and automated infrastructure deployment pipelines."
        if 'sap' in t_lower or 'enterprise architect' in t_lower:
            return "Architects enterprise SAP system integrations, business process automations, and corporate application architectures."
        if 'high performance data systems' in t_lower:
            return "Engineers high-throughput distributed data engines, low-latency storage subsystems, and data processing runtimes."
        if 'product engineer' in t_lower:
            return "Designs and develops user-facing financial product features, trading workflows, and interactive AI application interfaces."
        if 'solutions engineer' in t_lower or 'solution engineer' in t_lower:
            return "Designs and deploys conversational AI solutions, voice interfaces, and customer integration workflows."
        if 'data protection' in t_lower or 'backup' in t_lower:
            return "Engineers enterprise backup systems, disaster recovery architectures, and cyber resilience frameworks for corporate infrastructure."
        if 'benchmark engineer' in t_lower or 'linguistic' in t_lower or 'native language' in t_lower:
            return "Conducts linguistic evaluations, model benchmark testing, and localized language quality assessments."
        if 'deployment engineer' in t_lower:
            return "Deploys enterprise platform solutions, manages customer installations, and automates infrastructure provisioning."
        if 'automation engineer' in t_lower:
            return "Develops automated business process workflows, document extraction pipelines, and AI integrations for real estate operations."
        if 'modelling and simulation' in t_lower or 'simulation engineer' in t_lower:
            return "Develops physics simulation models, numerical algorithms, and computational modeling software."
        if 'prompt engineering' in t_lower or 'chatgpt' in t_lower:
            return "Designs prompt engineering templates, ChatGPT workflows, and conversational AI integrations for corporate education."
        if 'database support' in t_lower:
            return "Provides specialized technical support, database debugging, and query optimization for PostgreSQL database users."
        if 'named technical support' in t_lower or 'linux support' in t_lower:
            return "Provides dedicated technical support, computer vision API assistance, and developer onboarding for enterprise customers."
        if 'rails' in t_lower or 'ruby' in t_lower:
            return "Leads full-stack web application development, Ruby on Rails backends, and user interface architectures."
        if 'full-stack' in t_lower or 'fullstack' in t_lower:
            return "Develops full-stack web applications, frontend components, and backend API services."
        if any(k in t_lower for k in ['manager', 'director', 'head', 'vp', 'avp']):
            return "Leads software engineering teams, technical project delivery, and engineering architecture."
            
        if 'defense' in t_lower or 'apollo' in t_lower or 'backend' in t_lower or 'software engineer' in t_lower or 'developer' in t_lower:
            return "Designs, develops, and maintains enterprise software features, data workflows, and backend application services."
            
        return "Develops, maintains, and supports internal IT systems, enterprise applications, and corporate technology."

    # =========================================================================
    # 6. NON_TECHNICAL (580 records)
    # =========================================================================
    if cat == 'NON_TECHNICAL':
        if jid == 'job_e98b00bb44e6a41d':
            return "Leads revenue recognition under ASC 606, marketplace reconciliations, and SOX controls for cloud provider channels."

        # Specific prompt targets in the 155 biz cluster:
        if 'cmc' in t_lower or 'manufacturing lead' in t_lower:
            return "Oversees chemistry, manufacturing, and controls (CMC) compliance, regulatory filings, and biopharma production operations."
        if re.search(r'\bcustomer\s+success\b', t_lower):
            return "Guides customer onboarding, relationship management, product adoption, and client retention."
        if 'it sox' in t_lower:
            return "Leads IT general controls audits, SOX compliance assessments, and financial system security governance."
        if 'sox infrastructure' in t_lower:
            return "Leads internal control design, SOX compliance, and financial risk governance for compute and cloud infrastructure spend."
        if 'asset management' in t_lower and 'commercial associate' in t_lower:
            return "Manages commercial lease contracts, physical asset tracking, and procurement operations for data center facilities."
        if 'discovery technical operations' in t_lower or 'discovery' in t_lower and 'specialist' in t_lower:
            return "Coordinates electronic discovery technical operations, legal hold lifecycles, and litigation data governance."
        if 'docs lead' in t_lower:
            return "Leads developer documentation strategy, API reference authoring, and platform technical guides."

        # Procurement / Sourcing fixes for data centers & infrastructure:
        if jid == 'job_b847c81a2b76a070' or ('data center power & cooling' in t_lower and 'sourcing' in t_lower):
            return "Manages strategic equipment sourcing, power and cooling vendor contracts, and supplier execution for data centers."
        if jid == 'job_b567b0b811517bd2' or 'cloud sourcing' in t_lower:
            return "Directs global cloud compute capacity procurement, infrastructure provider negotiations, and supply commitments."
        if jid == 'job_86e95e76d79878c9' or 'ofci' in t_lower:
            return "Manages strategic procurement of owner-furnished equipment, vendor supply contracts, and data center hardware deliveries."
        if jid == 'job_fb3b97caf24d3590' or ('domain expert recruiter' in t_lower and 'contract' in t_lower):
            return "Manages specialized candidate sourcing, technical interview pipelines, and domain expert recruiting workflows."
        if jid == 'job_fd84fcf9f31e99f9' or ('talent sourcer' in t_lower and 'contract' in t_lower):
            return "Manages executive talent sourcing pipelines, candidate research, and leadership recruitment outreach."

        # Detailed roles in 155:
        if 'gas supply' in t_lower:
            return "Manages natural gas supply procurement, pipeline transportation agreements, and utility capacity for data centers."
        if 'hardware lab' in t_lower or 'lab manager' in t_lower:
            return "Manages hardware laboratory facilities, equipment receiving, rack staging, power distribution, and physical lab safety."
        if 'incident manager' in t_lower:
            if 'safeguards' in t_lower:
                return "Manages trust and safety incident escalations, model abuse mitigation workflows, and policy enforcement responses."
            return "Coordinates technical incident triage, cross-functional response cadences, and post-incident reviews for security operations."
        if 'safeguards enforcement' in t_lower:
            if 'bio' in t_lower:
                return "Investigates biological safety risks, conducts misuse investigations, and enforces trust and safety policies."
            if 'takeover' in t_lower or 'credential' in t_lower:
                return "Investigates account takeover incidents, credential stuffing attacks, and identity abuse patterns."
            if 'access controls' in t_lower or 'identity' in t_lower:
                return "Enforces account access policies, investigates malicious credential usage, and manages platform access reviews."
            if 'integrity' in t_lower or 'authenticity' in t_lower:
                return "Enforces platform integrity policies, investigates synthetic content misuse, and mitigates coordinated abuse campaigns."
            if 'well-being' in t_lower or 'well being' in t_lower:
                return "Leads trust and safety enforcement for user well-being, severe harm mitigation, and sensitive safety workflows."
            return "Enforces trust and safety policies, evaluates safety incident queues, and conducts account abuse investigations."
        if 'threat investigator' in t_lower or 'threat intel' in t_lower:
            if 'cbrn' in t_lower or 'weapons' in t_lower:
                return "Investigates technical threats involving chemical, biological, radiological, and nuclear misuse of AI models."
            if 'cyber' in t_lower:
                return "Investigates cyber threat actors, nation-state adversary tactics, and malicious cyber operations targeting AI systems."
            return "Conducts strategic threat intelligence research, threat modeling, and adversary investigation."
        if 'commissioning/quality manager' in t_lower or 'commissioning manager' in t_lower:
            return "Oversees electrical, mechanical, and safety commissioning quality assurance across data center construction projects."
        if 'data center capacity delivery' in t_lower:
            return "Oversees regional data center capacity delivery, contractor milestones, and infrastructure facility handoffs."
        if 'capacity deployment lead' in t_lower or 'compute capacity' in t_lower:
            return "Coordinates compute fleet deployment operations, infrastructure capacity handoffs, and resource optimization."
        if 'data center operations coordinator' in t_lower or 'data center manager' in t_lower:
            return "Coordinates data center facilities maintenance, equipment break-fix logistics, and operational ticket resolution."
        if 'strategic sourcing lead - construction' in t_lower or 'development project manager, data center' in t_lower or 'expansion pmo' in t_lower:
            return "Manages strategic data center construction programs, design delivery milestones, and capital project execution."
        if 'transaction manager' in t_lower or 'transaction principal' in t_lower:
            return "Executes commercial lease negotiations, real estate acquisitions, and transaction structuring for data center sites."
        if 'acquisitions and development' in t_lower:
            return "Directs site acquisitions, land entitlement processes, and real estate development for data center infrastructure."
        if 'debt capital' in t_lower or 'capital markets' in t_lower:
            return "Structures and executes debt capital transactions, credit facilities, and liquidity strategy to fund compute expansion."
        if 'order-to-cash' in t_lower or 'revenue assurance' in t_lower:
            return "Oversees global order-to-cash processes, customer revenue assurance controls, and enterprise billing integrity."
        if 'travel & expense' in t_lower:
            return "Directs global corporate travel policies, expense management operations, and corporate card program compliance."
        if 'vendor admin' in t_lower:
            return "Administers vendor master data governance, supplier onboarding workflows, and global accounts payable controls."
        if 'accounts receivable' in t_lower:
            return "Manages enterprise customer invoicing, receivables collections, and cash application accounting workflows."
        if 'financial reporting' in t_lower or 'gbs financial' in t_lower:
            return "Directs corporate financial reporting, statutory consolidations, and shared services accounting operations."
        if 'portfolio & investment' in t_lower or 'financial portfolio' in t_lower or 'borrower advocate' in t_lower:
            return "Manages loan portfolio performance tracking, mortgage servicing operations, and borrower resolution workflows."
        if 'pricing' in t_lower:
            return "Designs enterprise deal pricing structures, financial margin models, and commercial discounting frameworks."
        if 'risk & insurance' in t_lower or 'insurance risk' in t_lower:
            return "Manages corporate insurance policies, risk transfer programs, and commercial balance sheet protections."
        if 'ehs' in t_lower:
            return "Manages environmental health, occupational safety compliance, and operational EHS standards across data centers."
        if 'technical training' in t_lower or 'technical instructor' in t_lower or 'education specialist' in t_lower or 'operations training specialist' in t_lower:
            return "Designs technical training curricula, instructional materials, and customer enablement education programs."
        if 'gtm strategy & operations' in t_lower or 'gtm business operations' in t_lower or 'growth strategy & operations' in t_lower or 'revenue strategy and operations' in t_lower:
            return "Drives go-to-market operational planning, sales territory strategy, and business execution cadences."
        if 'reseller' in t_lower or 'resale' in t_lower:
            return "Manages international reseller partner programs, channel distribution operations, and commercial partner enablement."
        if 'commercial activation' in t_lower or 'strategic pursuits' in t_lower or 'strategic deals' in t_lower:
            return "Leads strategic enterprise commercial agreements, deal orchestration, and delivery partner activation."
        if 'investor relations' in t_lower:
            return "Directs investor communications, quarterly earnings preparation, and strategic shareholder relationships."
        if 'national security' in t_lower or 'international affairs' in t_lower:
            return "Directs government relations, public sector policy engagements, and national security regulatory partnerships."
        if 'podcast' in t_lower:
            return "Manages podcast brand sponsorships, digital audio media partnerships, and public storytelling initiatives."
        if 'analyst relations' in t_lower:
            return "Directs industry analyst relations strategy, product briefings, and competitive market positioning."
        if 'web design manager' in t_lower or 'web & inbound' in t_lower:
            return "Manages web design strategy, digital brand user experiences, and inbound digital conversion initiatives."
        if 'contributor experience' in t_lower:
            return "Builds contributor community programs, feedback mechanisms, and engagement operations for AI training networks."
        if 'research associate, biology' in t_lower or 'research operations lead, biology' in t_lower:
            return "Coordinates laboratory research operations, wet-lab protocols, and experimental workflows in computational biology."
        if 'biological safety' in t_lower:
            return "Manages biological safety policy programs, bio-risk evaluations, and laboratory safety compliance frameworks."
        if 'research operations, external artifacts' in t_lower:
            return "Manages technical publication workflows, system cards, and scientific research artifact releases."
        if 'open benchmarks grants' in t_lower:
            return "Directs grant program administration, application review cadences, and research milestone tracking for open AI benchmarks."
        if 'human frontier collective' in t_lower:
            return "Provides domain advisory expertise, expert consensus workflows, and non-technical governance for AI evaluation."
        if 'technical deployment' in t_lower:
            return "Manages technical customer onboarding timelines, statements of work, and project delivery roadmaps."
        if 'quality operations' in t_lower or 'subject matter expert' in t_lower:
            return "Oversees data annotation quality standards, expert review calibration, and operational evaluation benchmarks."
        if 'head of strategic startups' in t_lower or 'head of asean' in t_lower or 'head of southern europe' in t_lower:
            return "Directs commercial market expansion, regional go-to-market teams, and executive customer relationships."
        if 'tabletop exercise' in t_lower:
            return "Designs and facilitates crisis simulation tabletop exercises evaluating frontier AI societal risks and governance responses."
        if 'infrastructure capacity planner' in t_lower or 'network capacity planner' in t_lower:
            return "Models multi-year compute and networking infrastructure capacity forecasts, hardware demand curves, and supply commitments."
        if 'bi analyst' in t_lower or 'data analyst' in t_lower:
            return "Builds business intelligence dashboards, commercial data models, and analytical reports supporting strategic decisions."
        if 'cx ops' in t_lower:
            return "Manages customer experience operations, billing dispute resolution, and frontline support queue workflows."
        if 'director of product, ecosystem' in t_lower or 'principal pm, product strategy' in t_lower or 'product strategy principal' in t_lower:
            return "Guides commercial product strategy, competitive market intelligence, and product portfolio roadmaps."
        if 'director, product security' in t_lower:
            return "Directs product security strategy, application security governance, and vulnerability management programs."
        if 'security technology deployment' in t_lower or 'platform hardware security' in t_lower or 'continuous monitoring' in t_lower:
            return "Manages physical security system installations, hardware access controls, and infrastructure compliance monitoring."
        if 'senior director of it' in t_lower:
            return "Directs enterprise IT infrastructure, end-user technology services, corporate systems, and IT security operations."
        if 'vp, research' in t_lower or 'research manager, interpretability' in t_lower:
            return "Leads research operational planning, scientific team governance, and machine learning research delivery."
        if 'head of growth' in t_lower or 'growth marketer' in t_lower:
            return "Develops growth acquisition strategies, enterprise search visibility initiatives, and experimentation roadmaps."
        if 'operations manager - supply' in t_lower or 'inventory control' in t_lower:
            return "Manages operational supply forecasting, physical hardware inventory audits, and logistics tracking."
        if 'program director' in t_lower or 'technical project manager' in t_lower or 'special projects' in t_lower or 'strategic delivery' in t_lower:
            return "Directs complex multi-phase enterprise transformation programs, operational project delivery, and milestone execution."
        if 'customer strategy director' in t_lower or 'ai success manager' in t_lower:
            return "Advises executive clients on AI transformation roadmaps, organizational adoption, and customer value realization."
        if 'team manager' in t_lower:
            return "Manages frontline operational teams, daily performance metrics, and workflow execution quality."
        if 'frontier data lead' in t_lower:
            return "Directs customer data delivery programs, statement of work milestones, and account expansion operations."
        if 'solution specialist' in t_lower or 'solutions specialist' in t_lower:
            return "Provides technical pre-sales solution expertise, customer architecture demonstrations, and workload sizing."
        if 'senior manager, managed databases' in t_lower or 'field engineering' in t_lower:
            return "Directs technical field engineering teams, database infrastructure operations, and customer solution delivery."
        if 'applied ai cyber specialists' in t_lower:
            return "Leads specialized applied AI teams focused on cybersecurity defense, threat detection, and secure AI adoption."
        if 'product management, research' in t_lower:
            return "Leads product strategy, research deployment roadmaps, and model commercialization across frontier AI capabilities."
        if 'infrastructure security lead' in t_lower:
            return "Leads enterprise infrastructure security architecture, vulnerability defense, and compliance across distributed systems."
        if 'sambacloud experience' in t_lower:
            return "Guides developer cloud experience, brand identity, user onboarding workflows, and developer ecosystem programs."
        if 'synthetic data generation' in t_lower:
            return "Leads synthetic data generation pipelines, evaluation frameworks, and customer data transformations."
        if 'business operations & strategy' in t_lower or 'business operations associate' in t_lower:
            return "Conducts business operations analysis, quarterly goal-setting cadences, and strategic financial planning."
        if 'member of technical staff' in t_lower:
            return "Builds sandboxed reinforcement learning environments, terminal emulators, and browser automation tools for agentic training."
        if 'account solution architect - financial services' in t_lower:
            return "Designs cloud infrastructure architectures, GPU compute topologies, and technical integrations for financial services clients."
        if 'international ap lead' in t_lower:
            return "Manages international accounts payable, vendor invoice triage, cross-border payment reconciliations, and audit support."
        if 'data hall fit out' in t_lower:
            return "Manages data hall fit-out architectural designs, mechanical and electrical engineering specifications, and contractor delivery."
        if 'data center design manager' in t_lower or 'design management' in t_lower:
            return "Directs technical engineering designs, architectural standards, and infrastructure delivery across data center projects."

        # Fellows
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
            
        if re.search(r'\bcontracts?\b', t_lower) and not re.search(r'\bcontractor\b|\bcontract employee\b', t_lower):
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
    reasons = [generate_audit9_reason(r) for r in records]
    print(f"Total evaluated records: {len(reasons)}")
    counts = Counter(reasons)
    print(f"Distinct reasons count: {len(counts)}")
    print("\nTop reasons (>= 10):")
    for r_text, c in counts.most_common():
        if c >= 10:
            print(f"{c:3d}x: {r_text[:75]}...")
