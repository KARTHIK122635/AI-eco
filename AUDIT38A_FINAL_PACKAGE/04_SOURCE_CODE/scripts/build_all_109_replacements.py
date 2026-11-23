import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('reports/all_109_targets.json', 'r', encoding='utf-8') as f:
    targets = json.load(f)

BANNED = [
    r'\bvision\b',
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

# Specific mappings dictionary:
rep_dict = {}

# 1. Priorities
rep_dict['job_0d920108a62c8874'] = "Develop and evaluate complex financial scenarios to test and enhance AI accuracy in valuation, forecasting, and analysis; collaborate in interactive sessions to assess model outputs for market relevance and compliance; provide detailed feedback to improve AI capabilities; and contribute to specialized projects in financial modeling, risk assessment, and equity research."
rep_dict['job_8ad086e5f89d9290'] = "Design complex clinical scenarios, evaluate model decision-making for safety and accuracy, and shape reasoning frameworks through structured, example-driven feedback."
rep_dict['job_9a8d370f471b9403'] = "Design complex clinical scenarios, evaluate model decision-making for safety and accuracy, and shape reasoning frameworks through structured, example-driven feedback."
rep_dict['job_4c10396068078ad5'] = "Build working prototypes quickly, from AI agents and evaluation pipelines to data and knowledge systems, and take the most promising ones to production"
rep_dict['job_ca9fd326e9b5b4a3'] = "Build systems of record that Finance can close the books on and trace back to the signed contract, with reconciliation against the CRM and every downstream billing system designed in from the start."
rep_dict['job_6b50fb83f97464c3'] = "Design and ship billing capabilities end to end — pricing primitives, payment flows, contract and entitlement models, revenue data pipelines"
rep_dict['job_4a03b7baf7f497e7'] = "Invent, design, and implement RL environments and evaluations for agentic RTL generation, design (including formal) verification, physical design optimization."
rep_dict['job_82c44ea0d56968c5'] = "You'll design RL environments and coding tasks, build the reward signals and verifiers that capture what \"good code\" means, run training experiments on frontier models, diagnose why a model does (or doesn't) get better at a class of software-engineering work, and improve the speed and reliability of the pipelines that make all of that iterate fast."
rep_dict['job_67d5b04df41fa9f1'] = "Design widely-used APIs, frameworks, and abstractions that other engineers and researchers build on, with careful attention to interface legibility and principled defaults"
rep_dict['job_63a3680d2fc7006a'] = "You’ll own the development and continuous refinement of Cresta’s positioning and messaging for the Healthcare industry, translating our platform capabilities into clear, differentiated industry narratives that resonate with buyers, operators, and executives at payers, providers, DSOs, and retail health organizations"
rep_dict['job_4fd5890a5e0e7831'] = "You’ll own the development and continuous refinement of Cresta’s positioning and messaging for Travel & Hospitality, Telecommunications, and more, translating our platform capabilities into clear, differentiated industry narratives that resonate with buyers, operators, and executives in each"

# CoreWeave Data Center Technicians
rep_dict['job_4f4361d44526f5d7'] = "Maintain data center operations to ensure service availability and reliability. Conduct hardware and network diagnostics and repairs."
rep_dict['job_a2b5203844474445'] = "Maintain data center operations to ensure service availability and reliability. Conduct hardware and network diagnostics and repairs."
rep_dict['job_de27bd5296f47999'] = "Maintain data center operations to ensure service availability and reliability. Conduct hardware and network diagnostics and repairs."
rep_dict['job_e6c5f4d8890b7630'] = "Maintain data center operations to ensure service availability and reliability.Conduct hardware and network diagnostics and repairs."
rep_dict['job_509b55147b60eecb'] = "Maintain data center operations to ensure availability and reliability of service levels Conduct hardware and network diagnostics and repairs"
rep_dict['job_7427cacb294b9060'] = "Performing hardware and network diagnostics, troubleshooting, and physical repairs"
rep_dict['job_f9a9b26d75b45013'] = "Assemble, rack, stack, and maintain data center server, storage, and networking hardware. Maintain hot/cold aisle containment, conduct inventory audits, and perform routine physical maintenance."
rep_dict['job_7d02a7727c51c1d9'] = "Maintain data center operations to ensure service availability and reliability.Conduct hardware and network diagnostics and repairs."

# Anthropic AI Outcomes Manager / CSM
for jid in ['job_45c1882c91f1b5d5', 'job_bc685344022df5e7', 'job_0023846c82f691f5']:
    rep_dict[jid] = "Build trusting, strategic relationships with key customer decision makers in complex, matrixed organizations; understand their business and objectives and identify opportunities for optimization and expansion"

# Anthropic Applied AI Architects (with paint the vision or intro)
arch_common_1 = "Working closely with our Sales, Product, and Engineering teams, you'll guide customers from initial technical discovery through successful deployment."
arch_common_2 = "Partner with account executives to deeply understand customer requirements and translate them into technical solutions, ensuring alignment between business objectives and technical implementation"
arch_common_3 = "Partner with account executives across Japan to deeply understand customer requirements and translate them into technical solutions, ensuring alignment between business objectives and technical implementation"
arch_common_4 = "Partner with account executives across South Korea to deeply understand customer requirements and translate them into technical solutions, ensuring alignment between business objectives and technical implementation"

# Scale GPS Engineers
gps_common = "Take on the hardest technical problems across our programs, stepping in where projects are stuck or the path forward is unclear"

# Databricks Database Engine Internals
db_engine_common = "design and implement these next gen systems that leapfrog state-of-the-art: Query compilation and optimization Distributed query execution and scheduling Vectorized execution engine"

# Databricks AI SWE
db_ai_swe = "Design and implement core services and APIs for the platform, ensuring scalability, reliability, and operational excellence."

# Mirakl Labs Senior AI Engineer
mirakl_ai = "Design, build and scale the core capabilities of the Mirakl Assistant, including RAG, LLM orchestration, tool use, memory and context engineering, from rapid prototype to robust production feature"

# Mirakl Labs MLOps Engineer
mirakl_mlops = "Design and implement a performant, robust, and scalable ML Platform architecture — covering training, evaluation, and inference — while keeping costs under control"

# Mirakl Labs DevEx
mirakl_devex = "Build agents and assistants as products - across the full software development lifecycle (code review, tech design, maintenance, incident response), from first prototype to tools teams genuinely rely on every day."

# Cresta Backend SWEs
cresta_backend = "Design, implement, and maintain backend services and APIs to support applications. Build and optimize data storage solutions using Postgres , ClickHouse and Elasticsearch to ensure high performance and scalability."

# Capco Infrastructure Manager
capco_infra = "Lead and coordinate a large-scale AI Ops implementation project, ensuring effective planning, execution, and alignment with business and technical objectives. Manage and coordinate cross-functional IT teams responsible for setting up, integrating, and managing complex infrastructure environments"

# Artefact Senior AI Strategist
artefact_strat = "vous cadrez, analysez, prototypez et recommandez, vous coachez les consultants juniors, et vous voyez vos recommandations prendre vie avec nos équipes Engineering"

for t in targets:
    jid = t['jobId']
    desc = t['description']
    if jid in rep_dict:
        continue
    
    # Try common patterns
    if arch_common_1 in desc:
        rep_dict[jid] = arch_common_1
    elif arch_common_2 in desc:
        rep_dict[jid] = arch_common_2
    elif arch_common_3 in desc:
        rep_dict[jid] = arch_common_3
    elif arch_common_4 in desc:
        rep_dict[jid] = arch_common_4
    elif gps_common in desc:
        rep_dict[jid] = gps_common
    elif db_engine_common in desc:
        rep_dict[jid] = db_engine_common
    elif db_ai_swe in desc:
        rep_dict[jid] = db_ai_swe
    elif mirakl_ai in desc:
        rep_dict[jid] = mirakl_ai
    elif mirakl_mlops in desc:
        rep_dict[jid] = mirakl_mlops
    elif mirakl_devex in desc:
        rep_dict[jid] = mirakl_devex
    elif cresta_backend in desc:
        rep_dict[jid] = cresta_backend
    elif capco_infra in desc:
        rep_dict[jid] = capco_infra
    elif artefact_strat in desc:
        rep_dict[jid] = artefact_strat

print(f"Mapped {len(rep_dict)} of {len(targets)} targets so far.")
unmapped = [t for t in targets if t['jobId'] not in rep_dict]
print(f"Remaining unmapped: {len(unmapped)}")
for u in unmapped:
    print(f"{u['jobId']} | {u['company']} | {u['title']}")
