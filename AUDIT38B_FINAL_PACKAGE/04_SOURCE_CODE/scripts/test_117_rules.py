import sys, os
sys.path.insert(0, os.path.abspath('.'))
from scripts.audit10_uncertain_data import UNCERTAIN_REVIEWS
import re

BAD_GRAMMAR_PATTERNS = [
    r'\bresponsible for (?:drive|turn|lead|build|design|manage|support|conduct|oversee|coordinate|provide)\b',
    r'\bfocused on (?:turn|build|design|manage|lead|drive)\b',
    r'\bpartnering with customers on be\b',
    r'\bfor understand\b',
    r'\bworking with customers to [a-z]',
    r'\b(\w+)\s+\1\b'
]

COMPANY_INTRO_PATTERNS = [
    r'\bat cresta\b', r'\bto cresta\b', r'\banthropic is dedicated\b', r'\banthropic is building\b',
    r'\bscale ai is at the\b', r'\bat scale, we\b', r'more than \d+[\d,]*\s+organizations',
    r'\babout the role\b', r'\babout anthropic\b', r'\bjoin our team\b'
]

BOILERPLATE_PATTERNS = [
    r'stipend of', r'weekly stipend', r'annual salary', r'4 months of full-time',
    r'visa sponsorship', r'equal opportunity', r'fair chance', r'benefits \(these vary',
    r'\$\d+', r'€\d+', r'£\d+'
]

CATEGORY_KEYWORDS = {
    'CORE_AI_ML': [
        'ai', 'model', 'machine learning', 'deep learning', 'algorithm', 'pre-training',
        'post-training', 'alignment', 'rlhf', 'evaluat', 'data scien', 'linguistic', 'biomedical', 'robotics'
    ],
    'AI_INFRASTRUCTURE': [
        'infrastructure', 'data center', 'cluster', 'gpu', 'accelerator', 'network', 'fabric',
        'compute', 'hardware', 'power', 'cooling', 'demand', 'asic', 'silicon', 'kernel', 'server',
        'inference', 'serving', 'foundation model', 'bare-metal', 'virtualization', 'telemetry', 'dynamo', 'kubernetes'
    ],
    'AI_PRODUCT_SOLUTIONS': [
        'customer', 'enterprise', 'solution', 'architect', 'deploy', 'forward-deployed',
        'adoption', 'product', 'integrat', 'partner', 'field engineering', 'design', 'client', 'consulting', 'workflow', 'assistant', 'prompt'
    ],
    'AI_SUPPORTING_TECH': [
        'software', 'pipeline', 'data', 'platform', 'system', 'security', 'infrastructure',
        'database', 'backend', 'frontend', 'web', 'test', 'qa', 'sre', 'devops', 'tool', 'mobile',
        'asic', 'hardware', 'processor', 'verification', 'runtime', 'compiler', 'api', 'etl', 'elt', 'teleoperation', 'annotation'
    ],
    'NON_AI_TECH': [
        'it', 'endpoint', 'support', 'hardware', 'network', 'telecom', 'enterprise',
        'application', 'database', 'warehouse', 'software', 'robotics', 'server', 'sre', 'qa', 'tracking', 'helpdesk'
    ],
    'NON_TECHNICAL': [
        'operat', 'account', 'financial', 'tax', 'legal', 'recruit', 'talent', 'people',
        'sales', 'marketing', 'policy', 'economic', 'administrative', 'workplace', 'procurement',
        'customer', 'contract', 'credit', 'risk', 'partner', 'alliance', 'merger', 'acquisition',
        'revenue', 'reconciliation', 'sox', 'control', 'construction', 'energy', 'utility',
        'vendor', 'design', 'clinical', 'biomedical', 'corporate', 'compensation', 'reward',
        'benefits', 'strategy', 'transformation', 'roadmap', 'briefing', 'intelligence', 'affairs',
        'communication', 'media', 'commercial', 'pmo', 'content', 'patient', 'investigation', 'compliance', 'creative'
    ],
    'UNCERTAIN': [
        'detail', 'specificity', 'classify', 'definitive', 'vocational', 'training', 'coursework', 'curriculum'
    ]
}

defects_found = []

for jid, d in UNCERTAIN_REVIEWS.items():
    cat = d['category']
    r = d['reason']
    if not r.endswith('.'):
        defects_found.append((jid, 'no terminal period', r))
    if not r[0].isupper():
        defects_found.append((jid, 'does not start uppercase', r))
    if len(r.split()) < 5:
        defects_found.append((jid, 'under 5 words', r))
    for pat in BAD_GRAMMAR_PATTERNS:
        if re.search(pat, r, re.I):
            defects_found.append((jid, f'grammar defect {pat}', r))
    for pat in COMPANY_INTRO_PATTERNS:
        if re.search(pat, r, re.I):
            defects_found.append((jid, f'company intro {pat}', r))
    for pat in BOILERPLATE_PATTERNS:
        if re.search(pat, r, re.I):
            defects_found.append((jid, f'boilerplate {pat}', r))
    kws = CATEGORY_KEYWORDS.get(cat, [])
    if not any(k in r.lower() for k in kws):
        defects_found.append((jid, f'does not match {cat} keywords', r))

print(f"Total defects in 117 uncertain reviews: {len(defects_found)}")
if defects_found:
    for item in defects_found:
        print(item)
else:
    print("ALL 117 REVIEWS PASSED WITH 0 DEFECTS!")
