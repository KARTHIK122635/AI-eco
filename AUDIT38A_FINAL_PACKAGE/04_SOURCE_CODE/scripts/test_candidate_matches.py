import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('reports/all_109_targets.json', 'r', encoding='utf-8') as f:
    targets = json.load(f)

# Banned patterns that should NEVER appear in evidence:
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

# Let's inspect each of the 109 targets and determine the replacement
replacements = {}

# Explicit priority positions:
# 1. Finance Fellow
replacements['job_0d920108a62c8874'] = "Develop and evaluate complex financial scenarios to test and enhance AI accuracy in valuation, forecasting, and analysis; collaborate in interactive sessions to assess model outputs for market relevance and compliance; provide detailed feedback to improve AI capabilities; and contribute to specialized projects in financial modeling, risk assessment, and equity research."

# 2. Medical Fellows
replacements['job_8ad086e5f89d9290'] = "Design complex clinical scenarios, evaluate model decision-making for safety and accuracy, and shape reasoning frameworks through structured, example-driven feedback."
replacements['job_9a8d370f471b9403'] = "Design complex clinical scenarios, evaluate model decision-making for safety and accuracy, and shape reasoning frameworks through structured, example-driven feedback."

# 3. Principal Software Engineer, GPS
replacements['job_4c10396068078ad5'] = "Build working prototypes quickly, from AI agents and evaluation pipelines to data and knowledge systems, and take the most promising ones to production"

# 4. Billing Platform (EM & Staff+ SWE)
replacements['job_ca9fd326e9b5b4a3'] = "Build systems of record that Finance can close the books on and trace back to the signed contract, with reconciliation against the CRM and every downstream billing system designed in from the start."
replacements['job_6b50fb83f97464c3'] = "Design and ship billing capabilities end to end — pricing primitives, payment flows, contract and entitlement models, revenue data pipelines"

# 5. RL roles:
replacements['job_4a03b7baf7f497e7'] = "Invent, design, and implement RL environments and evaluations for agentic RTL generation, design (including formal) verification, physical design optimization."
replacements['job_82c44ea0d56968c5'] = "You'll design RL environments and coding tasks, build the reward signals and verifiers that capture what \"good code\" means, run training experiments on frontier models, diagnose why a model does (or doesn't) get better at a class of software-engineering work, and improve the speed and reliability of the pipelines that make all of that iterate fast."
replacements['job_67d5b04df41fa9f1'] = "Design widely-used APIs, frameworks, and abstractions that other engineers and researchers build on, with careful attention to interface legibility and principled defaults"

# 6. Cresta Senior PMM Healthcare & Vertical Solutions:
replacements['job_63a3680d2fc7006a'] = "You’ll own the development and continuous refinement of Cresta’s positioning and messaging for the Healthcare industry, translating our platform capabilities into clear, differentiated industry narratives that resonate with buyers, operators, and executives at payers, providers, DSOs, and retail health organizations"
replacements['job_4fd5890a5e0e7831'] = "You’ll own the development and continuous refinement of Cresta’s industry-specific positioning and messaging, translating our platform capabilities into clear, differentiated narratives that resonate with buyers, operators, and executives across key verticals."

# 7. CoreWeave Data Center Technicians:
dct_map = {
    'job_4f4361d44526f5d7': "Maintain data center operations to ensure service availability and reliability. Conduct hardware and network diagnostics and repairs.",
    'job_a2b5203844474445': "Maintain data center operations to ensure service availability and reliability. Conduct hardware and network diagnostics and repairs.",
    'job_de27bd5296f47999': "Maintain data center operations to ensure service availability and reliability. Conduct hardware and network diagnostics and repairs.",
    'job_e6c5f4d8890b7630': "Maintain data center operations to ensure service availability and reliability.Conduct hardware and network diagnostics and repairs.",
    'job_509b55147b60eecb': "Maintain data center operations to ensure availability and reliability of service levels Conduct hardware and network diagnostics and repairs",
    'job_7427cacb294b9060': "Performing hardware and network diagnostics, troubleshooting, and physical repairs",
    'job_f9a9b26d75b45013': "Assemble, rack, stack, and maintain data center server, storage, and networking hardware. Maintain hot/cold aisle containment, conduct inventory audits, and perform routine physical maintenance.",
    'job_7d02a7727c51c1d9': "Maintain data center operations to ensure service availability and reliability.Conduct hardware and network diagnostics and repairs."
}
replacements.update(dct_map)

# Check all defined so far
for jid, rep in replacements.items():
    t = next(t for t in targets if t['jobId'] == jid)
    assert rep in t['description'], f"FAIL verbatim for {jid}: {rep}"
    clean, banned_pat = check_clean(rep)
    assert clean, f"FAIL banned pattern {banned_pat} in {jid}: {rep}"

print(f"Verified {len(replacements)} priority replacements so far! All verbatim and clean.")
