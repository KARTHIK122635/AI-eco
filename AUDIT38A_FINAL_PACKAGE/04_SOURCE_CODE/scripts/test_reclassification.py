"""
Test Reclassification Algorithm for Correction 1:
Categories required:
- CORE_AI_ML
- AI_INFRASTRUCTURE
- AI_PRODUCT_SOLUTIONS
- AI_SUPPORTING_TECH
- NON_AI_TECH
- NON_TECHNICAL
- UNCERTAIN
"""

import json
import re
from collections import Counter

JSONL_PATH = "data/canonical/canonical_jobs.jsonl"

with open(JSONL_PATH, "r", encoding="utf-8") as f:
    jobs = [json.loads(line)["content"]["data"] for line in f if line.strip()]

def classify_role(title: str, description: str, company: str) -> str:
    t = title.lower()
    d = (description or "").lower()

    # 1. NON_TECHNICAL: Finance, legal, HR, recruiting, sales, marketing, operations, admin, facilities
    non_tech_patterns = [
        r'\b(account\s+executive|sales\s+director|sales\s+lead|sales\s+manager|business\s+development|enterprise\s+account)\b',
        r'\b(tax\s+lead|tax\s+manager|accountant|accounting|payroll|billing|controller|accounts\s+payable|financial\s+analyst|treasury|debt\s+capital)\b',
        r'\b(recruiter|recruiting|talent\s+acquisition|people\s+partner|people\s+operations|hr\s+|human\s+resources|benefits|equity\s+admin)\b',
        r'\b(communications\s+manager|pr\s+manager|brand\s+marketing|growth\s+marketing|content\s+writer|copywriter|social\s+media)\b',
        r'\b(executive\s+assistant|administrative\s+assistant|office\s+manager|facilities|receptionist|workplace\s+experience)\b',
        r'\b(legal\s+counsel|paralegal|compliance\s+manager|contracts\s+manager|trade\s+compliance)\b',
        r'\b(general\s+counsel|corporate\s+counsel|regulatory\s+affairs)\b',
        r'\b(customer\s+support\s+specialist|support\s+agent|support\s+rep|billing\s+analyst)\b'
    ]
    for pat in non_tech_patterns:
        if re.search(pat, t):
            # Check if it's explicitly technical sales engineering
            if "sales engineer" in t or "solutions architect" in t:
                return "AI_PRODUCT_SOLUTIONS"
            return "NON_TECHNICAL"

    # 2. CORE_AI_ML: Direct machine learning, deep learning, LLM, NLP, computer vision, research
    core_ai_patterns = [
        r'\b(machine\s+learning\s+engineer|ml\s+engineer|deep\s+learning|computer\s+vision|nlp\s+engineer|natural\s+language)\b',
        r'\b(research\s+scientist|ai\s+researcher|research\s+engineer|applied\s+scientist|ai\s+scientist)\b',
        r'\b(llm\s+engineer|prompt\s+engineer|foundation\s+model|alignment\s+researcher|ai\s+safety\s+researcher)\b',
        r'\b(post-training|pre-training|reinforcement\s+learning|generative\s+ai\s+engineer|mlops\s+engineer)\b',
        r'\b(ai\s+engineer|algorithm\s+engineer|speech\s+scientist|perception\s+engineer)\b',
        r'\b(data\s+scientist|applied\s+ai\s+engineer)\b'
    ]
    for pat in core_ai_patterns:
        if re.search(pat, t):
            return "CORE_AI_ML"

    # 3. AI_INFRASTRUCTURE: GPU cluster, CUDA, kernels, distributed systems, accelerators
    ai_infra_patterns = [
        r'\b(gpu|cuda|triton|kernel|accelerator|distributed\s+training|compute\s+infrastructure|ai\s+infrastructure)\b',
        r'\b(high\s+performance\s+computing|hpc|cluster\s+engineer|inference\s+infrastructure|model\s+serving)\b',
        r'\b(cluster\s+operations|network\s+engineer.*data\s+center|datacenter.*engineer)\b'
    ]
    for pat in ai_infra_patterns:
        if re.search(pat, t):
            return "AI_INFRASTRUCTURE"

    # 4. AI_PRODUCT_SOLUTIONS: Product managers, solutions architects, forward deployed
    ai_prod_patterns = [
        r'\b(product\s+manager|technical\s+product\s+manager|solutions\s+architect|solution\s+architect)\b',
        r'\b(forward\s+deployed|technical\s+account\s+manager|developer\s+advocate|developer\s+relations|ai\s+outcomes)\b',
        r'\b(ai\s+evangelist|field\s+engineer)\b'
    ]
    for pat in ai_prod_patterns:
        if re.search(pat, t):
            return "AI_PRODUCT_SOLUTIONS"

    # 5. AI_SUPPORTING_TECH: Software, data, platform, security at AI companies or directly touching AI
    pure_play = [
        "anthropic", "scale ai", "together ai", "coreweave", "sambanova",
        "cresta", "snorkel", "figure", "labelbox", "stability", "zilliz"
    ]
    is_pure_play_company = any(pp in company.lower() for pp in pure_play)

    supporting_patterns = [
        r'\b(software\s+engineer|backend\s+engineer|full\s+stack|frontend\s+engineer|systems\s+engineer)\b',
        r'\b(data\s+engineer|platform\s+engineer|infrastructure\s+engineer|devops|site\s+reliability|sre)\b',
        r'\b(security\s+engineer|cloud\s+engineer|firmware\s+engineer|embedded\s+engineer|robotics\s+software)\b',
        r'\b(qa\s+engineer|test\s+engineer|software\s+development\s+engineer|sde)\b'
    ]
    for pat in supporting_patterns:
        if re.search(pat, t):
            if is_pure_play_company:
                return "AI_SUPPORTING_TECH"
            elif any(k in d for k in ["machine learning", "deep learning", "ai model", "llm", "pipeline", "model"]):
                return "AI_SUPPORTING_TECH"
            else:
                return "NON_AI_TECH"

    # 6. NON_AI_TECH: General tech from general job boards
    non_ai_tech_patterns = [
        r'\b(web\s+developer|mobile\s+developer|ios\s+developer|android\s+developer|it\s+support|sysadmin|database\s+administrator)\b'
    ]
    for pat in non_ai_tech_patterns:
        if re.search(pat, t):
            return "NON_AI_TECH"

    # Check description for pure-play operational vs tech
    if is_pure_play_company:
        if any(w in t for w in ["manager", "lead", "director", "specialist"]):
            if any(w in t for w in ["security", "infra", "platform", "systems", "cloud", "data", "engineering"]):
                return "AI_SUPPORTING_TECH"
            else:
                return "NON_TECHNICAL"
        return "AI_SUPPORTING_TECH"

    if any(k in t for k in ["engineer", "developer", "architect"]):
        return "NON_AI_TECH"

    return "UNCERTAIN"

counts = Counter()
samples_by_cat = {}
for j in jobs:
    cat = classify_role(j["jobTitle"], j["jobDescription"], j["companyName"])
    counts[cat] += 1
    if cat not in samples_by_cat:
        samples_by_cat[cat] = []
    if len(samples_by_cat[cat]) < 5:
        samples_by_cat[cat].append((j["jobTitle"], j["companyName"]))

print("\n--- RECLASSIFICATION RESULTS ---")
for cat, cnt in counts.most_common():
    print(f"  {cat:<25}: {cnt:>4} ({cnt/len(jobs)*100:.1f}%)")

print("\nSamples per category:")
for cat, samples in samples_by_cat.items():
    print(f"\n[{cat}]")
    for title, comp in samples:
        print(f"  * {title} ({comp})")
