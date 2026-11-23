import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('reports/all_109_targets.json', 'r', encoding='utf-8') as f:
    targets = json.load(f)

BANNED = [
    r'\b(?:product|strategic|company|long-term|our)\s+vision\b|paint the vision|set the vision|shaping the vision|strategic direction, ai vision|towards our vision|from the vision',
    r'\bmission\b',
    r'\bculture\b',
    r'\bour team\b|\bour teams\b',
    r'\bjoin\b',
    r'\babout (?:us|the|our|scale|anthropic|coreweave|openai|databricks|nebius)\b',
    r'\bwe believe\b|\bwe think\b|\bwe view\b|\bwe are building\b|\bis building\b',
    r'\bequal opportunity\b|\baffirmative action\b|\bwe encourage you to apply\b',
    r'\byears experience\b|\byears of experience\b',
    r'\bbachelor\'s degree\b|\bdegree in\b',
    r'\bideal candidate\b',
    r'\bwho you are\b|\bwhat you\'ll need\b',
    r'\bminimum qualifications\b|\bpreferred qualifications\b',
    r'\bwhat we\'re looking for\b|\bwe are looking for\b|\bwe’re looking for\b',
    r'\bexists to ensure\b',
    r'\bsit at the intersection\b',
    r'\bworld-class\b',
    r'\bcollaborative work:\b',
    r'\bplay a key role in\b|\bplays a key role in\b',
    r'^scale’s rapidly growing',
]

def check_clean(text):
    for b in BANNED:
        if re.search(b, text, re.I):
            return False, b
    return True, None

rep = {}

# 1. Priorities
rep['job_0d920108a62c8874'] = "Develop and evaluate complex financial scenarios to test and enhance AI accuracy in valuation, forecasting, and analysis; collaborate in interactive sessions to assess model outputs for market relevance and compliance; provide detailed feedback to improve AI capabilities; and contribute to specialized projects in financial modeling, risk assessment, and equity research."
rep['job_8ad086e5f89d9290'] = "Design complex clinical scenarios, evaluate model decision-making for safety and accuracy, and shape reasoning frameworks through structured, example-driven feedback."
rep['job_9a8d370f471b9403'] = "Design complex clinical scenarios, evaluate model decision-making for safety and accuracy, and shape reasoning frameworks through structured, example-driven feedback."
rep['job_4c10396068078ad5'] = "Build working prototypes quickly, from AI agents and evaluation pipelines to data and knowledge systems, and take the most promising ones to production"
rep['job_ca9fd326e9b5b4a3'] = "Build systems of record that Finance can close the books on and trace back to the signed contract, with reconciliation against the CRM and every downstream billing system designed in from the start."
rep['job_6b50fb83f97464c3'] = "Design and ship billing capabilities end to end — pricing primitives, payment flows, contract and entitlement models, revenue data pipelines"
rep['job_4a03b7baf7f497e7'] = "Invent, design, and implement RL environments and evaluations for agentic RTL generation, design (including formal) verification, physical design optimization."
rep['job_82c44ea0d56968c5'] = "You'll design RL environments and coding tasks, build the reward signals and verifiers that capture what \"good code\" means, run training experiments on frontier models, diagnose why a model does (or doesn't) get better at a class of software-engineering work, and improve the speed and reliability of the pipelines that make all of that iterate fast."
rep['job_67d5b04df41fa9f1'] = "Design widely-used APIs, frameworks, and abstractions that other engineers and researchers build on, with careful attention to interface legibility and principled defaults"
rep['job_63a3680d2fc7006a'] = "You’ll own the development and continuous refinement of Cresta’s positioning and messaging for the Healthcare industry, translating our platform capabilities into clear, differentiated industry narratives that resonate with buyers, operators, and executives at payers, providers, DSOs, and retail health organizations"
rep['job_4fd5890a5e0e7831'] = "You’ll own the development and continuous refinement of Cresta’s positioning and messaging for Travel & Hospitality, Telecommunications, and more, translating our platform capabilities into clear, differentiated industry narratives that resonate with buyers, operators, and executives in each"

# CoreWeave Data Center Technicians
rep['job_4f4361d44526f5d7'] = "Maintain data center operations to ensure service availability and reliability Conduct hardware and network diagnostics and repairs"
rep['job_a2b5203844474445'] = "Maintain data center operations to ensure service availability and reliability. Conduct hardware and network diagnostics and repairs."
rep['job_de27bd5296f47999'] = "Maintain data center operations to ensure service availability and reliability. Conduct hardware and network diagnostics and repairs."
rep['job_e6c5f4d8890b7630'] = "Maintain data center operations to ensure service availability and reliability.Conduct hardware and network diagnostics and repairs."
rep['job_509b55147b60eecb'] = "Maintain data center operations to ensure availability and reliability of service levels Conduct hardware and network diagnostics and repairs"
rep['job_7427cacb294b9060'] = "Performing hardware and network diagnostics, troubleshooting, and physical repairs"
rep['job_f9a9b26d75b45013'] = "Assemble, rack, stack, and maintain data center server, storage, and networking hardware. Maintain hot/cold aisle containment, conduct inventory audits, and perform routine physical maintenance."
rep['job_7d02a7727c51c1d9'] = "Maintain data center operations to ensure service availability and reliability.Conduct hardware and network diagnostics and repairs."

# Anthropic AI Outcomes Manager / CSM
for jid in ['job_45c1882c91f1b5d5', 'job_bc685344022df5e7', 'job_0023846c82f691f5']:
    rep[jid] = "Build trusting, strategic relationships with key customer decision makers in complex, matrixed organizations; understand their business and objectives and identify opportunities for optimization and expansion"

# Anthropic Product Designer, Safeguards
rep['job_8341f8a6faee8aef'] = "Understand the technical architecture of our products and define primitives for new capabilities. Define feature areas with exceptional attention to detail and polish, identifying opportunities to improve quality and consistency of broader flows"

# Anthropic Research Engineer, Visual Knowledge Work
rep['job_1e8b2d8ee5e34329'] = "Manage technical relationships with external data vendors, including writing task specifications, evaluating visual data and annotation quality, and iterating on reward design"

# Scale AI Director & AGC
rep['job_aa001c816ac245da'] = "Advise the public sector business development teams on proposals and federal procurement law. Negotiate contracts for new business and manage follow-on contracts with the federal government and prime contractors."

# Scale AI Strategic Projects Lead
rep['job_3f7c9cb190129a33'] = "Lead cross-functional projects with diverse stakeholders (Engineering + Ops + Go-to-Market) Partner with product and engineering teams to enhance products to fulfill needs of strategic customers and initiatives Own the execution of our data labeling operations for strategic projects"

# Together AI Director of Brand
rep['job_4657d6865ca86588'] = "Build brand campaign with messaging, design and channel execution that cuts through the noise Drive consistency of brand messaging and look & feel across marketing assets and channels"

# Cresta Customer Strategy Director
rep['job_f37a0db650e24ab4'] = "Lead business value discovery, stakeholder alignment, and use-case scoping across complex, multi-stakeholder enterprise accounts"

# Snorkel AI VP FDE
rep['job_9f31230ef373c53b'] = "Set engineering standards for how the FDE organization works, including pipeline design, data evaluation and verification, delivery sign-off, and root cause analysis, so every team operates to one standard."

# CoreWeave Account Solutions Architect
rep['job_961d3a659e5894c4'] = "You’ll help AI teams solve real-world problems by designing custom demos, leading proofs of concept (PoCs) end-to-end, and acting as a trusted advisor on best practices from the first technical conversation through production and expansion."

# CoreWeave Principal Engineer IaaS
rep['job_381568cdf3c8852a'] = "Infrastructure Architecture - Design and implement highly scalable, multi-tenant control and data planes spanning compute, networking, and storage."

# CoreWeave Principal Engineer Perf & Benchmarking
rep['job_d4a04d0d1fa3c68e'] = "Perf Ownership - Lead end-to-end MLPerf Inference and Training submissions: workload selection, cluster planning, runbooks, audits, and result publication."

# CoreWeave Senior Technology Design Manager
rep['job_a13a84ccd21c0d5d'] = "overseeing the design of our Data Center Fit Outs (White Space) and ensuring that designs meet and incorporate CoreWeave project requirements."

# CoreWeave Staff Product Manager AI Inference
rep['job_4ede00298715cd84'] = "Solve novel problems related to scaling AI model inference on specialized hardware."

# CoreWeave Staff Security Engineer
rep['job_cd6a9fa698193ee7'] = "Design and build resilient, automated Detection-as-Code pipelines, maintaining high-fidelity detection logic, CI/CD testing frameworks, and continuous coverage validation."

# Databricks Sr PM Data Engineering
rep['job_e58baeb7a86d3815'] = "partner closely with various Databricks product teams to enable Data Engineering for the overall Databrick product portfolio including data science, data warehousing, business intelligence, and machine learning products"

# Databricks Staff SWE Databricks AI
rep['job_3a10b52751a1502a'] = "Solve hard problems in ingesting and querying traces, metrics, and artifacts at scale, and in evaluating AI agents in production."

# Databricks Staff SWE Search Quality
rep['job_720ab8670e44abea'] = "You’ll design and build the systems, models, and evaluation frameworks that ensure our Search stack delivers accurate, high-quality results across diverse multimodal datasets and query patterns."

# Harmattan Ai ML Engineer Intern
rep['job_0eb8a39b77bea5dc'] = "Run literature reviews and state-of-the-art analyses on computer vision and machine learning topics framed by the team. Scope projects, define tasks, and decide which approaches to benchmark, from baselines to the most prominent algorithms."

# Sunflower Labs CV & ML Engineer
rep['job_71f5c7b45f026e5a'] = "Design and develop a wide variety of computer vision and machine learning features for unmanned aerial vehicle (UAV) applications Train, fine-tune and evaluate deep learning models for tasks such as object detection, instance segmentation, image retrieval/reidentification"

# Voodoo Senior Security Engineer
rep['job_c4489b6d5491b5ca'] = "Architect, construct, and maintain automated security guardrails and paved paths to foster secure-by-default development environments."

# Smartlyio Senior EM
rep['job_dec08a00c3ca6fe1'] = "Drive the development of AdTech-specific ML models foundational AI capabilities (e.g. predictive and simulation techniques) and explore novel approaches that can be applied across Smartly’s products. Optimize existing models for performance, efficiency, and scalability."

# Doctrine Senior AI PM
rep['job_eb55db7bacee02ee'] = "Define, track, and analyze key metrics to measure product success and guide decisions. Collect and leverage user feedback, usability insights, and market research into clear product requirements that elevate user satisfaction."

# Skydio PhD Autonomy Intern
rep['job_16bc52df1159b77c'] = "Research, prototype, and generally assess the feasibility of new approaches Imagine and then implement new features that unlock magic for our users Characterize and quantify the performance of core components of the software and hardware stack"

# Robot Heart CTO
rep['job_d98ec925aa02009f'] = "Your work centers on advancing the AI-native, hardware-agnostic fleet operating system and scaling the infrastructure that supports autonomous mobile robots, drones, and humanoids."

# CDDS AG Senior Vision & Perception Engineer
rep['job_42a1da156e346751'] = "Implement and optimize vision pipelines in C++ for low-latency object detection and tracking Develop high-speed detection and tracking algorithms on Jetson platforms"

# Sightwise GmbH
rep['job_566f348bd3bf0e18'] = "Erstellen und Kuratieren von Trainingsdaten: reale Aufnahmen und synthetisch generierte Daten aus unserer Plattform Trainieren, Evaluieren und Verbessern von Klassifikations- und Detektionsmodellen Mitarbeit beim Aufbau und der Inbetriebnahme unserer Versuchsaufbauten"

# Roboflow Named TSE
rep['job_cf172bf7557a0ff6'] = "Diagnose complex issues spanning edge devices, networking, cloud pipelines, and inference performance. Partner closely with Product, Field Engineering, and Account Executives to relay customer insights."

# Anthropic AV Engineers
for jid in ['job_8d17c9b890a373ab', 'job_fd37980b24dac13a']:
    rep[jid] = "Lead AV design, procurement, and programming for new office builds, expansions, and retrofits across our global portfolio Create and maintain AV system designs including schematic drawings, line diagrams, and elevation plans"

# Anthropic Finance Systems Lead
rep['job_d93736d1ee4a9098'] = "Lead the international finance systems agenda for the Dublin finance hub and other international teams (including EMEA and APAC), finding the problems worth solving without waiting to be asked and partnering closely with the product owners for each finance area"

# Anthropic Security Engineer
rep['job_d3b042fdf4d449c3'] = "Lead cybersecurity Incident Response efforts covering diverse domains from external attacks to insider threats involving all layers of Anthropic’s technology stack"

# Scale AI GPS SWEs
rep['job_0887970c910f71b5'] = "Develop and maintain full-stack components that integrate with AI models, focusing on building responsive UIs and reliable backend APIs."
for jid in ['job_9da6bbbe6ce9c2c6', 'job_03efa7167566fada', 'job_4c2a3234c5f58949']:
    rep[jid] = "Architect production-grade applications that integrate AI models with full-stack frameworks, managing everything from interactive UIs to backend APIs and systems."
rep['job_8836aeb7b2444909'] = "Architect the fundamental frameworks for production-grade AI applications, setting the gold standard for how interactive UIs, backend systems, and AI models are integrated at scale to deliver reliable outcomes"

# Scale AI PM AI Applications
rep['job_088711206e853a98'] = "You will own large AI projects end to end, working directly with customers and leading a cross-functional team of engineers, MLEs, and operators to deliver solutions that drive meaningful impact for our customers"

# Scale AI Staff SWE Full Stack Gen AI
rep['job_af0d701a2b68fde4'] = "You will act as an organizational architect and tech lead, dynamically embedding yourself into the highest-priority projects across the org to guarantee execution"

# Cresta Partner Enablement Manager
rep['job_6b706fa6b3fac5a0'] = "Own the AI Receptionist partner enablement strategy, roadmap, and success metrics Own, configure, and continuously optimize our learning platform to scale enablement across partner types"

# Labelbox Recruiter
rep['job_fb3b97caf24d3590'] = "Run targeted outbound sourcing campaigns to identify and engage hard-to-reach subject matter experts. Recruit specialists across priority domains including scientific computing, cybersecurity, quantitative finance, engineering, mathematics, healthcare, legal, and other highly technical fields."

# CoreWeave Senior Production Engineer
rep['job_02a67152c4e32baf'] = "Assist in incident response efforts by helping identify and resolve service disruptions quickly, working under the guidance of more senior engineers."

# CoreWeave Senior SWE IAM
rep['job_e7b91d4cbd86b68f'] = "You will leverage your experience in distributed systems to design, extend, and harden a platform that secures our high-performance cloud infrastructure."

# CoreWeave Senior TPM Compute Firmware
rep['job_beb466c57c7e3e6e'] = "Lead and drive the end-to-end NPI process for next-generation DC-SCM hardware and firmware, from initial concept and architecture definition through design, validation, manufacturing, and production ramp."

# Databricks Life Sciences SA
rep['job_df0e763acd964f03'] = "Drive the technical and consumption strategy for the organisation's most complex customer engagements, directly influencing platform adoption and revenue growth."

# Databricks Staff Backend SWE AI Platform
rep['job_e86f546d333b6cd8'] = "You will design and build systems that enable high-throughput, low-latency inference across CPU and GPU workloads, influence architectural direction, and collaborate closely across platform, product, infrastructure, and research teams"

# Neuphonic Marketing Generalist
rep['job_350a930679a271b8'] = "Creating and publishing content across LinkedIn, X, our website and other relevant channels Helping plan and execute product launches, open-source releases and company announcements Turning technical work from our engineering and research teams into clear, engaging content"

# Nabla Senior MLE
rep['job_2cb4170746e06d9c'] = "Propose and guide experiments, model architectures, and data-labeling strategies to improve our speech-to-text, note generation, and normalization systems. Implement, train, and deploy models in production, ensuring scalability and robustness in a live healthcare setting."

# Artifact AI Engineer / Consultant
rep['job_2131aa478b54ee53'] = "Design, implement, and deploy pragmatic AI solutions using state-of-the-art technologies, tailored to client needs and habits, to solve pressing business problems"

# Common patterns for remainder
arch_common_1 = "Working closely with our Sales, Product, and Engineering teams, you'll guide customers from initial technical discovery through successful deployment."
arch_common_2 = "Partner with account executives to deeply understand customer requirements and translate them into technical solutions, ensuring alignment between business objectives and technical implementation"
arch_common_3 = "Partner with account executives across Japan to deeply understand customer requirements and translate them into technical solutions, ensuring alignment between business objectives and technical implementation"
arch_common_4 = "Partner with account executives across South Korea to deeply understand customer requirements and translate them into technical solutions, ensuring alignment between business objectives and technical implementation"
gps_common = "Take on the hardest technical problems across our programs, stepping in where projects are stuck or the path forward is unclear"
db_engine_common = "design and implement these next gen systems that leapfrog state-of-the-art: Query compilation and optimization Distributed query execution and scheduling Vectorized execution engine"
db_ai_swe = "Design and implement core services and APIs for the platform, ensuring scalability, reliability, and operational excellence."
mirakl_ai = "Design, build and scale the core capabilities of the Mirakl Assistant, including RAG, LLM orchestration, tool use, memory and context engineering, from rapid prototype to robust production feature"
mirakl_mlops = "Design and implement a performant, robust, and scalable ML Platform architecture — covering training, evaluation, and inference — while keeping costs under control"
mirakl_devex = "Build agents and assistants as products - across the full software development lifecycle (code review, tech design, maintenance, incident response), from first prototype to tools teams genuinely rely on every day."
cresta_backend = "Design, implement, and maintain backend services and APIs to support applications. Build and optimize data storage solutions using Postgres , ClickHouse and Elasticsearch to ensure high performance and scalability."
capco_infra = "Lead and coordinate a large-scale AI Ops implementation project, ensuring effective planning, execution, and alignment with business and technical objectives. Manage and coordinate cross-functional IT teams responsible for setting up, integrating, and managing complex infrastructure environments"
artefact_strat = "vous cadrez, analysez, prototypez et recommandez, vous coachez les consultants juniors, et vous voyez vos recommandations prendre vie avec nos équipes Engineering"

for t in targets:
    jid = t['jobId']
    desc = t['description']
    if jid in rep:
        continue
    
    # Try common patterns
    if arch_common_1 in desc:
        rep[jid] = arch_common_1
    elif arch_common_2 in desc:
        rep[jid] = arch_common_2
    elif arch_common_3 in desc:
        rep[jid] = arch_common_3
    elif arch_common_4 in desc:
        rep[jid] = arch_common_4
    elif gps_common in desc:
        rep[jid] = gps_common
    elif db_engine_common in desc:
        rep[jid] = db_engine_common
    elif db_ai_swe in desc:
        rep[jid] = db_ai_swe
    elif mirakl_ai in desc:
        rep[jid] = mirakl_ai
    elif mirakl_mlops in desc:
        rep[jid] = mirakl_mlops
    elif mirakl_devex in desc:
        rep[jid] = mirakl_devex
    elif cresta_backend in desc:
        rep[jid] = cresta_backend
    elif capco_infra in desc:
        rep[jid] = capco_infra
    elif artefact_strat in desc:
        rep[jid] = artefact_strat

print(f"Total mapped: {len(rep)} / {len(targets)}")

missing = [t for t in targets if t['jobId'] not in rep]
if missing:
    print(f"Missing {len(missing)}:")
    for m in missing:
        print(f"  {m['jobId']} | {m['company']} | {m['title']}")
else:
    print("ALL 109 TARGETS ARE MAPPED!")

# Verify verbatim and clean for ALL 109!
all_valid = True
for jid, text in rep.items():
    t = next(t for t in targets if t['jobId'] == jid)
    if text not in t['description']:
        print(f"ERROR: NOT VERBATIM in {jid}: {text[:60]}...")
        all_valid = False
    clean, banned_pat = check_clean(text)
    if not clean:
        print(f"ERROR: BANNED {banned_pat} in {jid}: {text[:60]}...")
        all_valid = False

if all_valid:
    print("\n>>> ALL 109 REPLACEMENTS ARE 100% VERBATIM AND 100% CLEAN OF ALL BANNED WORDS! <<<")
    with open('reports/audit14_all_109_replacements.json', 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=2)
    print("Saved reports/audit14_all_109_replacements.json")
