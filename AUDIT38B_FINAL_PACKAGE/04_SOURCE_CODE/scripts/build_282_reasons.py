import json
import re
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

backend_records = [r for r in records if r['classificationReason'] == 'Designs, builds, and maintains backend services, distributed systems, and APIs supporting AI platforms.']

print(f"Backend records: {len(backend_records)}")

def get_282_reason(r):
    jid = r['jobId']
    t = r['jobTitle'].strip()
    tl = t.lower()
    comp = r['companyName'].strip()
    resp = r.get('responsibilityEvidence', '') or ''
    rl = resp.lower()

    # Explicit examples from prompt:
    # - Developer Education Lead, Claude Platform
    if 'developer education' in tl or 'developer education lead' in tl:
        return "Develops technical curriculum, developer documentation, sample projects, and educational workshops for developer platforms."
    # - Field Executive Architect
    if 'field executive architect' in tl:
        return "Advises strategic enterprise executive leaders on AI architecture adoption, deployment strategy, and technical governance."
    # - Front End Engineer, Marketing
    if 'front end engineer' in tl and 'marketing' in tl:
        return "Develops user interfaces, web components, and client-facing web applications for corporate digital properties."
    # - Incident Response Manager – Product & Engineering
    if 'incident response' in tl:
        return "Coordinates incident response workflows, operational readiness cadences, and system recovery across product and engineering services."
    # - IT Systems Engineer, Client Platform (ChromeOS / macOS / M&A)
    if 'it systems engineer' in tl or 'client platform' in tl:
        if 'chromeos' in tl:
            return "Manages corporate ChromeOS endpoint fleets, device provisioning pipelines, and client system policies."
        if 'macos' in tl:
            return "Manages enterprise macOS client platforms, automated device management profiles, and endpoint security standards."
        if 'm&a' in tl:
            return "Leads IT systems integration, corporate directory consolidation, and infrastructure migration for mergers and acquisitions."
        return "Designs and maintains enterprise IT systems, identity integrations, and corporate software infrastructure."
    # - Manager, Corporate Network Engineering
    if 'corporate network' in tl or 'network engineering' in tl:
        return "Architects and maintains internal corporate network infrastructure, enterprise firewalls, and office connectivity systems."
    # - Red Team Engineer, Safeguards
    if 'red team' in tl:
        return "Executes adversarial red-teaming assessments, vulnerability evaluations, and safeguard testing on AI systems."
    # - Salesforce Developer
    if 'salesforce' in tl:
        return "Develops custom Salesforce integrations, Apex workflows, and CRM applications supporting business operations."

    # Other specific roles in 282:
    if 'bioinformatics' in tl:
        return "Develops computational biology algorithms, genomic data processing pipelines, and bioinformatic analysis tools."
    if 'privacy' in tl and 'engineer' in tl:
        return "Engineers privacy-preserving technical architectures, data governance frameworks, and data protection controls."
    if 'conversational design' in tl or 'demo engineer' in tl:
        return "Designs interactive AI demonstrations, proof-of-concept conversational interfaces, and technical customer prototypes."
    if 'functional architect' in tl:
        return "Architects AI-assisted software engineering practices, developer workflows, and R&D development automation."
    if 'gtm engineer' in tl:
        return "Architects go-to-market systems integrations, revenue data pipelines, and internal AI-native commercial tooling."
    if 'strategic partnerships' in tl or 'global systems integrators' in tl:
        return "Leads technical alliance strategy, co-engineering initiatives, and go-to-market execution with global systems integrators."
    if 'japan chief architect' in tl:
        return "Defines chip and system architectures, silicon specifications, and hardware roadmap alignment for Japanese enterprise markets."
    if 'japan engineering lead' in tl:
        return "Leads regional engineering delivery, technical program alignment, and cross-functional hardware-software coordination."
    if 'knowledge architect' in tl:
        return "Architects technical knowledge management platforms, engineering documentation schemas, and organizational information systems."
    if 'voice experience' in tl:
        return "Architects real-time voice streaming systems, low-latency audio pipelines, and conversational agent interfaces."
    if 'marketing engineer' in tl:
        return "Engineers marketing automation systems, digital web infrastructure, and technical SEO platforms."
    if 'technical marketing' in tl:
        return "Develops technical product demonstrations, developer tutorials, and engineering content for platform capabilities."
    if 'technical sourcer' in tl:
        return "Develops technical sourcing pipelines, talent identification strategies, and candidate outreach for engineering hiring."
    if 'engineering program coordinator' in tl:
        return "Coordinates engineering execution schedules, project milestones, and technical delivery cadences across infrastructure teams."
    if 'due diligence design' in tl:
        return "Performs technical due diligence, electrical and civil engineering feasibility assessments for data center acquisitions."
    if 'white space design' in tl:
        return "Designs mission-critical data center white space layouts, power distributions, and structural containment architectures."
    if 'data center operational excellence' in tl or 'procedure' in tl:
        return "Develops standard operating procedures, technical documentation standards, and operational excellence frameworks for data centers."
    if 'thermal engineer' in tl:
        return "Designs and optimizes liquid cooling architectures, thermal management systems, and heat dissipation for high-density GPU clusters."
    if 'electrical engineer' in tl:
        return "Designs server electrical architectures, power distribution boards, and high-current power delivery systems for compute clusters."
    if 'screen recording' in tl or 'windows native' in tl:
        return "Develops high-performance native Windows client software, screen capture pipelines, and desktop recording architectures."
    if 'sme, support systems' in tl:
        return "Manages support routing infrastructure, ticketing automation, and workforce tooling for contributor support operations."
    if 'support engineer' in tl or 'technical support' in tl or 'designated support' in tl:
        if 'bare metal' in tl:
            return "Provides deep technical troubleshooting, hardware diagnostic support, and incident resolution for bare-metal compute fleets."
        if 'inference' in tl:
            return "Provides tier-3 technical support, model inference troubleshooting, and API debugging for enterprise customers."
        if 'govops' in tl or 'government' in tl:
            return "Provides technical support, security compliance troubleshooting, and operational maintenance for public sector enclaves."
        if 'forge' in tl:
            return "Provides technical customer support, cluster diagnostic engineering, and issue remediation for cloud compute platforms."
        return "Provides dedicated technical support, API troubleshooting, and system diagnostic engineering for enterprise customers."
    if 'partner engineer' in tl:
        return "Leads technical partner co-engineering, cloud integration architecture, and joint engineering initiatives."
    if 'search ranking' in tl or 'search platform' in tl:
        return "Engineers machine learning search infrastructure, retrieval ranking algorithms, and discovery systems."
    if 'money' in tl or 'billing' in tl or 'commercialisation' in tl:
        return "Engineers financial transaction infrastructure, billing engines, and commercial subscription services."
    if 'ai gateway' in tl:
        return "Engineers high-throughput AI API gateway infrastructure, request rate-limiting, and model routing layers."
    if 'customer engagement' in tl or 'docs platform' in tl:
        return "Builds user engagement analytics platforms, documentation delivery services, and customer feedback infrastructure."
    if 'continuous integration' in tl or 'ci ' in tl:
        return "Builds automated continuous integration pipelines, test orchestration infrastructure, and developer productivity tooling."
    if 'code rl' in tl:
        return "Builds scalable reinforcement learning execution environments and agentic code generation harnesses."
    if 'claude code' in tl:
        return "Builds developer tooling infrastructure, terminal-based agent runtimes, and interactive programming interfaces."
    if 'vector index' in tl or 'vectordb' in tl:
        return "Engineers distributed vector database indexing architectures, approximate nearest neighbor search, and retrieval engines."
    if 'pki' in tl:
        return "Designs and operates public key infrastructure, cryptographic certificate management, and hardware security modules."
    if 'applied training' in tl:
        return "Builds scalable distributed training environments, cluster onboarding automation, and GPU workload initialization platforms."
    if 'observability' in tl or 'monitoring' in tl:
        return "Engineers high-scale observability pipelines, distributed tracing services, and metrics collection infrastructure."
    if 'threat and abuse' in tl or 'account abuse' in tl or 'account creation' in tl:
        return "Engineers automated abuse detection systems, account fraud prevention pipelines, and security defense mechanisms."
    if 'auth' in tl or 'identity' in tl or 'iam' in tl:
        return "Engineers enterprise identity and access management (IAM) services, authentication protocols, and authorization controls."
    if 'caching' in tl:
        return "Engineers ultra-low latency distributed caching tiers, memory-mapped key-value stores, and cache coherence protocols."
    if 'sandboxing' in tl or 'sandboxes' in tl:
        return "Builds secure multi-tenant execution sandboxes, container isolation runtimes, and virtualization security layers."
    if 'tokens' in tl or 'prompt structures' in tl:
        return "Engineers tokenization pipelines, prompt formatting runtimes, and context window management services."
    if 'datacenter server lifecycle' in tl or 'server lifecycle' in tl or 'metaldev' in tl:
        return "Builds automation services and provisioning software managing the bare-metal lifecycle of GPU datacenter servers."
    if 'perf and benchmarking' in tl or 'benchmarking' in tl:
        return "Develops Kubernetes-native benchmarking services to measure latency, throughput, and hardware efficiency across GPU clusters."
    if 'distributed data systems' in tl or 'data systems' in tl:
        return "Architects and implements high-throughput distributed data storage engines, replication protocols, and storage runtimes."
    if 'autonomous systems' in tl:
        return "Engineers mission software, autonomous command-and-control architectures, and real-time distributed edge platforms."
    if 'physical ai' in tl or 'robot' in tl:
        return "Builds infrastructure platforms and software runtimes for physical AI, robotics telemetry, and embodied systems."
    if 'ai workload orchestration' in tl or 'orchestration platform' in tl:
        return "Designs Kubernetes-native workload orchestration services, scheduling runtimes, and cluster provisioning pipelines."
    if 'inference platform' in tl or 'inference serving' in tl or 'inference' in tl:
        return "Engineers high-performance, low-latency model inference serving engines, dynamic request batching, and GPU kernel optimizations."
    if 'agent' in tl:
        if 'shopping' in tl:
            return "Engineers backend microservices, real-time merchant integrations, and commerce workflows for shopping AI agents."
        if 'oversight' in tl:
            return "Engineers observability platforms, behavioral evaluation pipelines, and oversight infrastructure for production AI agents."
        if 'voice' in tl:
            return "Engineers low-latency audio streaming infrastructure, voice agent runtimes, and telephony protocol integrations."
        return "Builds execution runtimes, tool-integration protocols, and scalable backend platforms for autonomous AI agents."
    if 'weaved' in tl or 'weave' in tl:
        return "Engineers observability, evaluation, and monitoring platforms for AI agents and generative AI applications."
    if 'weights & biases' in tl or 'w&b' in tl:
        return "Engineers core experimentation tracking platforms, artifact repositories, and ML workflow orchestration systems."
    if 'sambarack' in tl or 'sambastack' in tl:
        return "Engineers hardware-software platform integration, reconfigurable dataflow architectures, and rack-scale compute systems."
    if 'model bring-up' in tl:
        return "Engineers open-weight model bring-up frameworks, model conversion pipelines, and runtime execution optimizations."
    if 'validation & si' in tl:
        return "Performs signal integrity modeling, measurement correlation, and high-speed electrical validation for silicon platforms."
    if 'dft' in tl:
        return "Designs design-for-test (DFT) logic, scan architectures, and automated test pattern generation for AI acceleration silicon."
    if 'design verifiction' in tl or 'design verification' in tl:
        return "Develops verification testbenches, simulation models, and coverage frameworks validating complex silicon IP."
    if 'place and route' in tl or 'pnr' in tl:
        return "Develops automated partitioning, placement, and routing algorithms for reconfigurable dataflow silicon architectures."
    if 'post-silicon' in tl:
        return "Executes post-silicon bring-up, high-speed IO validation, and diagnostic firmware debugging for AI processor chips."
    if 'product engineer' in tl:
        if 'education' in tl:
            return "Designs and develops educational software products, interactive learning tools, and platform user interfaces."
        return "Engineers end-to-end product features, full-stack user workflows, and customer-facing application services."
    if 'rtl design' in tl:
        return "Designs RTL microarchitectures, digital logic, and memory subsystem controllers for high-performance AI silicon."
    if 'silicon' in tl or 'firmware' in tl:
        return "Develops low-level silicon firmware, hardware abstraction layers, and board bring-up software for compute devices."
    if 'front end' in tl or 'frontend' in tl or 'full-stack' in tl or 'full stack' in tl:
        return "Develops full-stack web applications, interactive user interfaces, and client components supporting platform services."
    if 'solutions architect' in tl or 'solutions engineer' in tl or 'field engineer' in tl or 'forward deployment' in tl:
        return "Architects and deploys customer-facing AI solutions, technical enterprise integrations, and platform deployments."
    if 'systems phd' in tl:
        return "Conducts systems-level research and software engineering to optimize distributed data processing and AI engines."
    if 'systems engineer' in tl or 'system engineer' in tl:
        if 'virtualization' in tl:
            return "Engineers bare-metal host virtualization layers, hypervisor interfaces, and kernel software bridging AI workloads."
        return "Develops host software stacks, OS provisioning systems, and kernel-level infrastructure managing compute servers."
    if 'manager' in tl or 'director' in tl or 'lead' in tl:
        return "Leads engineering teams in designing, building, and operating scalable infrastructure and software platforms."
    if 'product sandboxing' in tl:
        return "Engineers secure execution environments and container runtimes isolating untrusted code executed by AI agents."
    if 'stem' in tl:
        return "Engineers scientific computing integrations, numerical evaluation environments, and STEM reasoning infrastructure for AI models."
    if 'safeguards human review' in tl or 'safeguards data' in tl:
        return "Engineers safety oversight platforms, human review annotation tools, and compliance data pipelines."
    if 'access programs' in tl:
        return "Engineers access control platforms, customer provisioning workflows, and gated entitlement systems for AI models."

    # General backend / platform roles:
    return "Designs, builds, and scales core backend services, distributed systems, and API infrastructure supporting AI platforms."

test_reasons = [get_282_reason(r) for r in backend_records]
counts = Counter(test_reasons)
print(f"\nDistinct reasons generated for 282: {len(counts)}")
print("Distribution:")
for r_text, c in counts.most_common():
    print(f"{c:2d}x: {r_text}")
