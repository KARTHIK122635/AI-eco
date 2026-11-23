"""
Core Job Schemas and Normalization Utilities for AI Job Acquisition.
Phase II - Stage 2: Data Quality Corrections
"""

import re
import html
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from bs4 import BeautifulSoup


# Canonical 7 Categories per Second Audit Specification
CANONICAL_AI_CATEGORIES = [
    "CORE_AI_ML",
    "AI_INFRASTRUCTURE",
    "AI_PRODUCT_SOLUTIONS",
    "AI_SUPPORTING_TECH",
    "NON_AI_TECH",
    "NON_TECHNICAL",
    "UNCERTAIN"
]

COMMON_AI_SKILLS = [
    "Python", "PyTorch", "TensorFlow", "CUDA", "Kubernetes", "Docker", "SQL",
    "Spark", "LLMs", "RAG", "LangChain", "Hugging Face", "AWS", "GCP", "Azure",
    "C++", "Ray", "Triton", "JAX", "vLLM", "Transformers", "Git", "Linux",
    "FastAPI", "Pandas", "Scikit-Learn", "OpenCV", "NLP", "Computer Vision",
    "Reinforcement Learning", "Fine-Tuning", "Vector Databases", "Prompt Engineering"
]

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


def clean_html(raw_html: Optional[str]) -> Optional[str]:
    """Strip HTML tags and normalize whitespace with full entity unescaping."""
    if not raw_html:
        return None
    unescaped = html.unescape(raw_html)
    soup = BeautifulSoup(unescaped, "html.parser")
    text = soup.get_text(separator=" ")
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else None


def resolve_company_website(company: str, url: str) -> Optional[str]:
    """Resolve authoritative official company website."""
    if company in COMPANY_WEBSITES:
        return COMPANY_WEBSITES[company]
    if url and "arbeitnow.com" not in url and "jobicy.com" not in url and "remotive.com" not in url:
        m = re.match(r'https?://([^/]+)', url)
        if m:
            return f"https://{m.group(1)}"
    return None


def normalize_employment_type(raw: Optional[str]) -> str:
    """Normalize raw employment type to standard canonical enums."""
    if not raw:
        return "FULL_TIME"
    raw_lower = raw.lower().replace("-", " ").replace("_", " ")
    if "intern" in raw_lower:
        return "INTERNSHIP"
    if "contract" in raw_lower or "freelance" in raw_lower or "temp" in raw_lower:
        return "CONTRACT"
    if "part time" in raw_lower or "parttime" in raw_lower:
        return "PART_TIME"
    if "full time" in raw_lower or "fulltime" in raw_lower or "permanent" in raw_lower:
        return "FULL_TIME"
    return "FULL_TIME"


def normalize_remote_type(raw_type: Optional[str], location_str: Optional[str] = "") -> Optional[str]:
    """Normalize remote type to REMOTE, HYBRID, ONSITE, or null."""
    combined = f"{raw_type or ''} {location_str or ''}".lower()
    if "remote" in combined or "anywhere" in combined or "work from home" in combined or "wfh" in combined:
        if "hybrid" in combined:
            return "HYBRID"
        return "REMOTE"
    if "hybrid" in combined:
        return "HYBRID"
    if "onsite" in combined or "on-site" in combined or "in-office" in combined:
        return "ONSITE"
    if location_str:
        return "ONSITE"
    return None


def normalize_experience_level(title: str, description: Optional[str] = None) -> str:
    """Detect experience level from title and description using word-boundary matching."""
    t_lower = title.lower()
    
    if re.search(r'\bintern\b|\binternship\b', t_lower):
        return "Internship"
    if re.search(r'\b(director|head of|vp|vice president|chief|executive)\b', t_lower):
        return "Director/Executive"
    if re.search(r'\b(principal|staff|fellow)\b', t_lower):
        return "Principal/Staff"
    if re.search(r'\b(lead|manager|team lead)\b', t_lower):
        return "Lead"
    if re.search(r'\b(senior|sr\.?|iii|iv|v)\b', t_lower):
        return "Senior"
    if re.search(r'\b(junior|jr\.?|associate|entry|graduate)\b', t_lower):
        return "Entry-Level"
    if re.search(r'\b(mid|ii)\b', t_lower):
        return "Mid-Level"
    if re.search(r'\b(i)\b', t_lower):
        return "Entry-Level"
    
    if description:
        m = re.search(r'([0-9]+)\+?\s*(?:-\s*([0-9]+)\+?)?\s*years?\s+(?:of\s+)?experience', description, re.IGNORECASE)
        if m:
            years = int(m.group(1))
            if years >= 7:
                return "Senior"
            if years >= 3:
                return "Mid-Level"
            return "Entry-Level"
            
    return "Mid-Level"


def classify_ai_role(title: str, description: Optional[str], company: str) -> str:
    """
    Classify job vacancy based on actual role responsibilities into 7 canonical tiers:
    - CORE_AI_ML
    - AI_INFRASTRUCTURE
    - AI_PRODUCT_SOLUTIONS
    - AI_SUPPORTING_TECH
    - NON_AI_TECH
    - NON_TECHNICAL
    - UNCERTAIN
    """
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
        if any(pp in company.lower() for pp in ["coreweave", "together", "anthropic", "scale", "sambanova"]):
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


def parse_salary_comprehensive(text: Optional[str]) -> Tuple[Optional[float], Optional[float], Optional[str], Optional[str]]:
    """
    Extract min, max salary, currency, and compensationType.
    Handles em-dash (—), en-dash (–), hyphen (-), and 'to'.
    Distinguishes ANNUAL_BASE vs ANNUAL_OTE vs HOURLY.
    Never fabricates missing information.
    """
    if not text:
        return None, None, None, None

    is_ote = bool(re.search(r'\bOTE\b|on[\s-]target[\s-]earnings', text, re.I))

    # Pattern 1: Explicit "Annual Salary:" / "Base Salary:" / "Salary Range:" with any dash
    m_labeled = re.search(
        r'(?:annual\s+salary|base\s+salary|salary\s+range|compensation\s+range)\s*:\s*([$£€])?\s*([0-9]{2,3}(?:,[0-9]{3})+|[0-9]{2,3}k)\s*(?:—|–|-|to)\s*([$£€])?\s*([0-9]{2,3}(?:,[0-9]{3})+|[0-9]{2,3}k)\s*(USD|GBP|EUR)?',
        text,
        re.IGNORECASE
    )
    if m_labeled:
        curr_sym = m_labeled.group(1) or m_labeled.group(3)
        curr_code = m_labeled.group(5)
        raw_min = m_labeled.group(2).lower()
        raw_max = m_labeled.group(4).lower()
        
        val_min = float(raw_min.replace("k", "000").replace(",", ""))
        val_max = float(raw_max.replace("k", "000").replace(",", ""))
        
        currency = "USD"
        if curr_code:
            currency = curr_code.upper()
        elif curr_sym == "£":
            currency = "GBP"
        elif curr_sym == "€":
            currency = "EUR"
            
        comp_type = "ANNUAL_OTE" if is_ote else "ANNUAL_BASE"
        if 20000 <= val_min <= 2000000 and 20000 <= val_max <= 3000000 and val_max >= val_min:
            return val_min, val_max, currency, comp_type

    # Pattern 2: Standard Currency Symbol with Dash/To
    m_standard = re.search(
        r'([$£€])\s*([0-9]{2,3}(?:,[0-9]{3})+)\s*(?:—|–|-|to)\s*([$£€])?\s*([0-9]{2,3}(?:,[0-9]{3})+)\s*(USD|GBP|EUR)?(?:\s*(?:/\s*year|annually|per\s+year|a\s+year))?',
        text,
        re.IGNORECASE
    )
    if m_standard:
        curr_sym = m_standard.group(1)
        curr_code = m_standard.group(5)
        val_min = float(m_standard.group(2).replace(",", ""))
        val_max = float(m_standard.group(4).replace(",", ""))
        
        currency = "USD"
        if curr_code:
            currency = curr_code.upper()
        elif curr_sym == "£":
            currency = "GBP"
        elif curr_sym == "€":
            currency = "EUR"
            
        comp_type = "ANNUAL_OTE" if is_ote else "ANNUAL_BASE"
        if 20000 <= val_min <= 2000000 and 20000 <= val_max <= 3000000 and val_max >= val_min:
            return val_min, val_max, currency, comp_type

    # Pattern 3: Hourly rates
    m_hourly = re.search(
        r'([$£€])\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(?:—|–|-|to)\s*([$£€])?\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(?:/\s*hr|per\s+hour|hourly)',
        text,
        re.IGNORECASE
    )
    if m_hourly:
        curr_sym = m_hourly.group(1)
        val_min = float(m_hourly.group(2))
        val_max = float(m_hourly.group(4))
        currency = "GBP" if curr_sym == "£" else ("EUR" if curr_sym == "€" else "USD")
        if 15 <= val_min <= 500 and val_max >= val_min:
            return val_min, val_max, currency, "HOURLY"

    # Pattern 4: $150k - $200k USD
    m_k = re.search(
        r'([$£€])\s*([0-9]{2,3})\s*k\s*(?:—|–|-|to)\s*([$£€])?\s*([0-9]{2,3})\s*k\s*(USD|GBP|EUR)?',
        text,
        re.IGNORECASE
    )
    if m_k:
        curr_sym = m_k.group(1)
        curr_code = m_k.group(5)
        val_min = float(m_k.group(2)) * 1000
        val_max = float(m_k.group(4)) * 1000
        currency = "USD"
        if curr_code:
            currency = curr_code.upper()
        elif curr_sym == "£":
            currency = "GBP"
        elif curr_sym == "€":
            currency = "EUR"
        comp_type = "ANNUAL_OTE" if is_ote else "ANNUAL_BASE"
        if val_max >= val_min:
            return val_min, val_max, currency, comp_type

    return None, None, None, None


def extract_skills_split(title: str, description: Optional[str]) -> Tuple[List[str], List[str]]:
    """Separate skills into requiredSkills and preferredSkills based on job section."""
    text = f"{title} {description or ''}"
    text_lower = text.lower()
    
    preferred_split = re.split(
        r'\b(preferred qualifications|nice to have|bonus points|what will help you stand out|plus if you have|preferred skills)\b',
        text_lower,
        maxsplit=1
    )
    
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


def generate_job_id(source_name: str, source_id: str, url: str) -> str:
    """Generate deterministic, stable unique job ID."""
    raw = f"{source_name}:{source_id}:{url}".encode("utf-8")
    return f"job_{hashlib.sha256(raw).hexdigest()[:16]}"


# Backward compatibility aliases for collectors and test harnesses
categorize_ai_job = classify_ai_role
SUPPORTED_AI_CATEGORIES = CANONICAL_AI_CATEGORIES


def extract_salary(description: Optional[str]) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    val_min, val_max, currency, _ = parse_salary_comprehensive(description)
    return val_min, val_max, currency


def extract_skills(text: str) -> List[str]:
    req, pref = extract_skills_split(text, "")
    return sorted(list(set(req + pref)))

