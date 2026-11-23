"""
Refine role classifier to ensure high precision across all 7 categories.
"""

import json
import re
from collections import Counter

JSONL_PATH = "data/canonical/canonical_jobs.jsonl"

with open(JSONL_PATH, "r", encoding="utf-8") as f:
    jobs = [json.loads(line)["content"]["data"] for line in f if line.strip()]

def classify_role_v2(title: str, description: str, company: str) -> str:
    t = title.lower()
    d = (description or "").lower()

    # 1. NON_TECHNICAL: Business, corporate, finance, marketing, sales, recruiting, HR, legal, facilities, admin
    non_tech_words = [
        "account executive", "sales director", "sales lead", "sales manager", "sales development",
        "enterprise sales", "commercial sales", "business development", "inside sales", "renewals",
        "gtm enablement", "tax lead", "tax manager", "accountant", "accounting", "payroll",
        "billing", "controller", "accounts payable", "accounts receivable", "financial analyst",
        "treasury", "debt capital", "finance manager", "director of finance", "revenue assurance",
        "recruiter", "recruiting", "talent acquisition", "people partner", "people operations",
        "human resources", "hr manager", "hr coordinator", "benefits", "equity admin", "compensation",
        "communications manager", "pr manager", "brand marketing", "growth marketing", "content writer",
        "marketing strategy", "product marketing", "demand gen", "events manager", "executive assistant",
        "administrative assistant", "office manager", "facilities", "receptionist", "workplace experience",
        "workplace operations", "legal counsel", "paralegal", "compliance manager", "contracts manager",
        "trade compliance", "general counsel", "corporate counsel", "regulatory affairs", "customer support",
        "support agent", "support specialist", "operations manager", "business operations", "chief of staff"
    ]
    if any(w in t for w in non_tech_words):
        # Unless explicitly technical engineering sales/solutions
        if not any(w in t for w in ["solutions architect", "sales engineer", "technical account manager"]):
            return "NON_TECHNICAL"

    # 2. CORE_AI_ML: Direct machine learning, deep learning, LLM, NLP, computer vision, research
    core_ai_words = [
        "machine learning", "ml engineer", "deep learning", "computer vision", "nlp engineer",
        "natural language", "research scientist", "ai researcher", "research engineer",
        "applied scientist", "ai scientist", "research resident", "llm engineer", "prompt engineer",
        "foundation model", "alignment researcher", "ai safety", "post-training", "pre-training",
        "reinforcement learning", "generative ai engineer", "mlops engineer", "ai engineer",
        "algorithm engineer", "speech scientist", "perception engineer", "data scientist",
        "data science", "applied ai engineer", "applied machine learning", "ai fellow", "robotics engineer"
    ]
    if any(w in t for w in core_ai_words):
        return "CORE_AI_ML"

    # 3. AI_INFRASTRUCTURE: GPU cluster, CUDA, kernels, distributed systems, accelerators, cloud infra at AI companies
    ai_infra_words = [
        "gpu", "cuda", "triton", "kernel", "accelerator", "distributed training",
        "compute infrastructure", "ai infrastructure", "inference infrastructure",
        "model serving", "cluster operations", "datacenter", "data center",
        "high performance computing", "hpc", "cloud infrastructure", "network engineer",
        "site reliability engineer", "sre", "hardware engineer", "asic", "fpga", "systems engineer"
    ]
    if any(w in t for w in ai_infra_words):
        if "coreweave" in company.lower() or "together" in company.lower() or "anthropic" in company.lower() or "scale" in company.lower() or "sambanova" in company.lower():
            return "AI_INFRASTRUCTURE"
        if any(w in t for w in ["gpu", "cuda", "triton", "kernel", "accelerator", "cluster", "hpc", "inference", "ai infrastructure"]):
            return "AI_INFRASTRUCTURE"

    # 4. AI_PRODUCT_SOLUTIONS: Product managers, solutions architects, forward deployed, customer delivery
    ai_prod_words = [
        "product manager", "technical product manager", "solutions architect", "solution architect",
        "forward deployed", "technical account manager", "developer advocate", "developer relations",
        "ai outcomes", "ai evangelist", "field engineer", "transformation leader", "delivery architect",
        "applied ai architect", "customer delivery", "partner engineer"
    ]
    if any(w in t for w in ai_prod_words):
        return "AI_PRODUCT_SOLUTIONS"

    # 5. AI_SUPPORTING_TECH: Software, data, platform, security at AI companies or directly touching AI
    pure_play = [
        "anthropic", "scale ai", "together ai", "coreweave", "sambanova",
        "cresta", "snorkel", "figure", "labelbox", "stability", "zilliz"
    ]
    is_pure_play_company = any(pp in company.lower() for pp in pure_play)

    supporting_tech_words = [
        "software engineer", "backend engineer", "full stack", "frontend engineer",
        "data engineer", "platform engineer", "infrastructure engineer", "devops",
        "security engineer", "cloud engineer", "firmware engineer", "embedded engineer",
        "robotics software", "qa engineer", "test engineer", "software development engineer",
        "sde", "database engineer", "web engineer", "mobile engineer"
    ]
    if any(w in t for w in supporting_tech_words):
        if is_pure_play_company:
            return "AI_SUPPORTING_TECH"
        elif any(k in d for k in ["machine learning", "deep learning", "ai model", "llm", "neural", "pytorch", "tensorflow"]):
            return "AI_SUPPORTING_TECH"
        else:
            return "NON_AI_TECH"

    # 6. NON_AI_TECH: General tech from general job boards
    non_ai_tech_words = [
        "it support", "sysadmin", "database administrator", "systems administrator",
        "helpdesk", "desktop support", "it specialist"
    ]
    if any(w in t for w in non_ai_tech_words):
        return "NON_AI_TECH"

    # Check company-wide fallbacks
    if is_pure_play_company:
        if any(w in t for w in ["director", "lead", "manager", "specialist"]):
            if any(w in t for w in ["security", "infra", "platform", "cloud", "data", "engineering", "systems"]):
                return "AI_SUPPORTING_TECH"
            return "NON_TECHNICAL"
        return "AI_SUPPORTING_TECH"

    if any(w in t for w in ["engineer", "developer", "architect"]):
        return "NON_AI_TECH"

    return "UNCERTAIN"

counts = Counter()
uncertain_titles = []
for j in jobs:
    cat = classify_role_v2(j["jobTitle"], j["jobDescription"], j["companyName"])
    counts[cat] += 1
    if cat == "UNCERTAIN":
        uncertain_titles.append((j["jobTitle"], j["companyName"]))

print("\n--- RECLASSIFICATION V2 RESULTS ---")
for cat, cnt in counts.most_common():
    print(f"  {cat:<25}: {cnt:>4} ({cnt/len(jobs)*100:.1f}%)")

print(f"\nRemaining UNCERTAIN: {len(uncertain_titles)}")
if uncertain_titles:
    print("Sample uncertain titles:")
    for t, c in uncertain_titles[:15]:
        print(f"  * {t} ({c})")
