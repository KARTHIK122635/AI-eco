import json
import csv
import re
from collections import defaultdict, Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

# Let's inspect all 1,930 records against comprehensive domain vocabulary and quality checks
CATEGORY_KEYWORDS = {
    'CORE_AI_ML': [
        'ai', 'model', 'machine learning', 'deep learning', 'algorithm', 'neural',
        'training', 'fine-tuning', 'pre-training', 'post-training', 'alignment', 'rlhf',
        'evaluat', 'data scien', 'linguistic', 'biomedical', 'robotics', 'nlp', 'vision',
        'foundation', 'vlm', 'generative', 'reinforcement', 'geometry', 'computational'
    ],
    'AI_INFRASTRUCTURE': [
        'infrastructure', 'data center', 'cluster', 'gpu', 'accelerator', 'network',
        'fabric', 'compute', 'hardware', 'power', 'cooling', 'demand', 'asic', 'silicon',
        'kernel', 'server', 'inference', 'serving', 'foundation model', 'bare-metal',
        'virtualization', 'telemetry', 'dynamo', 'kubernetes', 'k8s', 'slurm', 'node',
        'provisioning', 'uptime', 'vm', 'hypervisor', 'hpc', 'control plane', 'vpc'
    ],
    'AI_PRODUCT_SOLUTIONS': [
        'customer', 'enterprise', 'solution', 'architect', 'architecture', 'deploy',
        'deployment', 'forward-deployed', 'adoption', 'product', 'integrat', 'partner',
        'field engineering', 'design', 'client', 'consulting', 'workflow', 'assistant',
        'prompt', 'agent', 'transformation', 'application', 'discovery', 'readiness',
        'advisor', 'governance', 'advisory'
    ],
    'AI_SUPPORTING_TECH': [
        'software', 'pipeline', 'data', 'platform', 'system', 'security', 'infrastructure',
        'database', 'backend', 'frontend', 'web', 'test', 'qa', 'sre', 'devops', 'tool',
        'mobile', 'asic', 'hardware', 'processor', 'verification', 'runtime', 'compiler',
        'api', 'etl', 'elt', 'teleoperation', 'annotation', 'telemetry', 'monitoring',
        'identity', 'iam', 'auth', 'caching', 'kernel', 'engine', 'engineering', 'developer',
        'warehouse', 'code', 'optimization', 'salesforce', 'apex', 'crm'
    ],
    'NON_AI_TECH': [
        'it', 'endpoint', 'support', 'hardware', 'network', 'telecom', 'enterprise',
        'application', 'database', 'warehouse', 'software', 'robotics', 'server', 'sre',
        'qa', 'tracking', 'helpdesk', 'dental', 'logistics', 'mechatronic', 'firmware',
        'embedded', 'systems', 'analyst', 'clinical'
    ],
    'NON_TECHNICAL': [
        'operat', 'account', 'financial', 'tax', 'legal', 'recruit', 'talent', 'people',
        'sales', 'marketing', 'policy', 'economic', 'administrative', 'workplace',
        'procurement', 'customer', 'contract', 'credit', 'risk', 'partner', 'alliance',
        'merger', 'acquisition', 'revenue', 'reconciliation', 'sox', 'control', 'construction',
        'energy', 'utility', 'vendor', 'design', 'clinical', 'biomedical', 'corporate',
        'compensation', 'reward', 'benefits', 'strategy', 'transformation', 'roadmap',
        'briefing', 'intelligence', 'affairs', 'communication', 'media', 'commercial',
        'pmo', 'content', 'patient', 'investigation', 'compliance', 'creative', 'facilities',
        'safety', 'forecast', 'demand', 'fellowship', 'training', 'event', 'licensing',
        'deal', 'sourcing', 'merchandising', 'localization', 'linguistic', 'care', 'support'
    ],
    'UNCERTAIN': [
        'detail', 'specificity', 'classify', 'definitive', 'vocational', 'training', 'coursework', 'curriculum'
    ]
}

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

reasons_to_titles = defaultdict(list)
for r in records:
    reasons_to_titles[r['classificationReason']].append((r['category'], r['jobTitle']))

results = []
status_counts = Counter()
defect_counts = Counter()

for r in records:
    jid = r['jobId']
    comp = r['companyName']
    title = r['jobTitle']
    cat = r['category']
    reason = r['classificationReason']

    defects = []
    requires_review = []

    # 1. Empty explanations
    if not reason or not reason.strip():
        defects.append("EMPTY_EXPLANATION")
        defect_counts["EMPTY_EXPLANATION"] += 1

    # 2. Sentence fragments / formatting
    if not reason.endswith('.'):
        defects.append("MISSING_TERMINAL_PERIOD")
        defect_counts["MISSING_TERMINAL_PERIOD"] += 1
    if reason and reason[0].islower():
        defects.append("STARTS_WITH_LOWERCASE")
        defect_counts["STARTS_WITH_LOWERCASE"] += 1
    if len(reason.split()) < 5:
        defects.append("TOO_SHORT_UNDER_5_WORDS")
        defect_counts["TOO_SHORT_UNDER_5_WORDS"] += 1
    if re.match(r'^(?:for|to|that|because|as|with)\s+', reason, re.I):
        defects.append("SUBORDINATING_PREPOSITION_FRAGMENT")
        defect_counts["SUBORDINATING_PREPOSITION_FRAGMENT"] += 1

    # 3. Grammar pattern defects
    for pat in BAD_GRAMMAR_PATTERNS:
        if re.search(pat, reason, re.I):
            defects.append(f"GRAMMAR_DEFECT_{pat}")
            defect_counts["GRAMMAR_DEFECT"] += 1

    # 4. Irrelevant company introductions
    for pat in COMPANY_INTRO_PATTERNS:
        if re.search(pat, reason, re.I):
            defects.append(f"COMPANY_INTRO_{pat}")
            defect_counts["COMPANY_INTRO"] += 1

    # 5. Compensation / benefits / visa boilerplate
    for pat in BOILERPLATE_PATTERNS:
        if re.search(pat, reason, re.I):
            defects.append(f"BOILERPLATE_{pat}")
            defect_counts["BOILERPLATE"] += 1

    # 6. Category keyword alignment
    expected_kws = CATEGORY_KEYWORDS.get(cat, [])
    if not any(kw in reason.lower() for kw in expected_kws):
        requires_review.append(f"CATEGORY_ALIGNMENT_REVIEW_RECOMMENDED (Reason lacks explicit {cat} vocabulary)")

    # 7. Cross-category explanation collisions
    shared_cats = {c for c, t in reasons_to_titles[reason]}
    if len(shared_cats) > 1:
        requires_review.append(f"CROSS_CATEGORY_SHARED_EXPLANATION ({', '.join(sorted(shared_cats))})")

    # Determine status
    if defects:
        status = "FAIL"
        status_counts["FAIL"] += 1
        note = "; ".join(defects)
    elif requires_review:
        status = "REQUIRES_REVIEW"
        status_counts["REQUIRES_REVIEW"] += 1
        note = "; ".join(requires_review)
    else:
        status = "PASS"
        status_counts["PASS"] += 1
        note = "None"

    results.append({
        'job_id': jid,
        'company_name': comp,
        'job_title': title,
        'category': cat,
        'audit_status': status,
        'defects_detected': note,
        'classification_reason': reason
    })

print(f"Audit Status Breakdown across all 1,930 records:")
for s, cnt in sorted(status_counts.items()):
    print(f"  {s}: {cnt} ({cnt/len(records)*100:.2f}%)")

print(f"\nHard Defects Count: {sum(defect_counts.values())}")
if status_counts['REQUIRES_REVIEW'] > 0:
    print(f"\nSample of records requiring review ({status_counts['REQUIRES_REVIEW']} total):")
    revs = [r for r in results if r['audit_status'] == 'REQUIRES_REVIEW']
    for r in revs[:10]:
        print(f"  [{r['job_id']}] {r['company_name']} - {r['job_title']} ({r['category']}) -> {r['defects_detected']}")
