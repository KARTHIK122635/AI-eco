"""
Test full reclassification, salary extraction, company website resolution,
and skills separation on all 1,930 records.
"""

import json
import re
from collections import Counter

JSONL_PATH = "data/canonical/canonical_jobs.jsonl"

with open(JSONL_PATH, "r", encoding="utf-8") as f:
    jobs = [json.loads(line)["content"]["data"] for line in f if line.strip()]

# 1. Company Website Registry
COMPANY_WEBSITES = {
    "Anthropic": "https://www.anthropic.com",
    "CoreWeave": "https://www.coreweave.com",
    "Databricks": "https://www.databricks.com",
    "Scale AI": "https://scale.com",
    "Together AI": "https://www.together.ai",
    "SambaNova Systems": "https://sambanova.ai",
    "Cresta": "https://cresta.com",
    "Snorkel AI": "https://snorkel.ai",
    "Figure AI": "https://www.figure.ai",
    "Labelbox": "https://labelbox.com",
    "Stability AI": "https://stability.ai",
    "Palantir Technologies": "https://www.palantir.com",
    "Zilliz": "https://zilliz.com"
}

def resolve_company_website(company: str, url: str) -> str:
    if company in COMPANY_WEBSITES:
        return COMPANY_WEBSITES[company]
    # For Arbeitnow or other platforms, try domain from applicationUrl
    if "arbeitnow.com" not in url and "jobicy.com" not in url and "remotive.com" not in url:
        m = re.match(r'https?://([^/]+)', url)
        if m:
            return f"https://{m.group(1)}"
    return None

# 2. Reclassification Logic
def classify_ai_role(title: str, description: str, company: str) -> str:
    t = title.lower()
    d = (description or "").lower()

    # 1. NON_TECHNICAL: Business, corporate, finance, marketing, sales, recruiting, HR, legal, facilities, admin
    non_tech_words = [
        "account executive", "sales director", "sales lead", "sales manager", "sales development",
        "enterprise sales", "commercial sales", "business development", "inside sales", "renewals",
        "gtm enablement", "tax lead", "tax manager", "apac tax", "accountant", "accounting", "payroll",
        "billing", "controller", "accounts payable", "accounts receivable", "financial analyst",
        "treasury", "debt capital", "finance manager", "director of finance", "revenue assurance",
        "travel & expense", "recruiter", "recruiting", "talent acquisition", "people partner",
        "people operations", "human resources", "hr manager", "hr coordinator", "benefits",
        "equity admin", "compensation", "communications manager", "pr manager", "brand marketing",
        "growth marketing", "content writer", "marketing strategy", "product marketing", "demand gen",
        "events manager", "executive assistant", "administrative assistant", "office manager",
        "facilities", "receptionist", "workplace experience", "workplace operations", "workplace lead",
        "legal counsel", "paralegal", "compliance manager", "contracts manager", "trade compliance",
        "general counsel", "corporate counsel", "regulatory affairs", "customer support",
        "support agent", "support specialist", "operations manager", "business operations",
        "chief of staff", "partner marketing", "regional marketing", "brand content"
    ]
    if any(w in t for w in non_tech_words):
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
        "applied ai architect", "customer delivery", "partner engineer", "product designer",
        "technical solutions"
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
        "sde", "database engineer", "web engineer", "mobile engineer", "technical program manager", "tpm"
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
        "helpdesk", "desktop support", "it specialist", "it engineer"
    ]
    if any(w in t for w in non_ai_tech_words):
        return "NON_AI_TECH"

    # Fallbacks
    if is_pure_play_company:
        if any(w in t for w in ["director", "lead", "manager", "specialist"]):
            if any(w in t for w in ["security", "infra", "platform", "cloud", "data", "engineering", "systems"]):
                return "AI_SUPPORTING_TECH"
            return "NON_TECHNICAL"
        return "AI_SUPPORTING_TECH"

    if any(w in t for w in ["engineer", "developer", "architect"]):
        return "NON_AI_TECH"

    return "UNCERTAIN"

# 3. Skills Separation (Required vs Preferred)
COMMON_AI_SKILLS = [
    "Python", "PyTorch", "TensorFlow", "CUDA", "Kubernetes", "Docker", "SQL",
    "Spark", "LLMs", "RAG", "LangChain", "Hugging Face", "AWS", "GCP", "Azure",
    "C++", "Ray", "Triton", "JAX", "vLLM", "Transformers", "Git", "Linux",
    "FastAPI", "Pandas", "Scikit-Learn", "OpenCV", "NLP", "Computer Vision",
    "Reinforcement Learning", "Fine-Tuning", "Vector Databases", "Prompt Engineering"
]

def extract_skills_split(title: str, description: str):
    text = f"{title} {description or ''}"
    text_lower = text.lower()
    
    # Check if there is a "Preferred" or "Nice to have" section
    preferred_split = re.split(r'\b(preferred qualifications|nice to have|bonus points|what will help you stand out|plus if you have)\b', text_lower, maxsplit=1)
    
    req_skills = []
    pref_skills = []
    
    if len(preferred_split) == 3:
        req_text = preferred_split[0]
        pref_text = preferred_split[1] + " " + preferred_split[2]
        
        for sk in COMMON_AI_SKILLS:
            pat = r'\b' + re.escape(sk.lower()) + r'\b'
            if re.search(pat, req_text):
                req_skills.append(sk)
            elif re.search(pat, pref_text):
                pref_skills.append(sk)
    else:
        for sk in COMMON_AI_SKILLS:
            pat = r'\b' + re.escape(sk.lower()) + r'\b'
            if re.search(pat, text_lower):
                req_skills.append(sk)

    return sorted(list(set(req_skills))), sorted(list(set(pref_skills)))

# Run on all jobs
cat_counter = Counter()
pref_counter = 0
site_counter = 0

for j in jobs:
    cat = classify_ai_role(j["jobTitle"], j["jobDescription"], j["companyName"])
    cat_counter[cat] += 1
    req_s, pref_s = extract_skills_split(j["jobTitle"], j["jobDescription"])
    if pref_s:
        pref_counter += 1
    site = resolve_company_website(j["companyName"], j["applicationUrl"])
    if site:
        site_counter += 1

print("\n--- RECLASSIFICATION RESULTS ---")
for c, cnt in cat_counter.most_common():
    print(f"  {c:<25}: {cnt:>4} ({cnt/len(jobs)*100:.1f}%)")

print(f"\nPreferred skills populated: {pref_counter} ({pref_counter/len(jobs)*100:.1f}%)")
print(f"Company website populated: {site_counter} ({site_counter/len(jobs)*100:.1f}%)")
