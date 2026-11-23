import re

BOILERPLATE_PATTERNS = [
    r'while candidates in the listed locations',
    r'remote candidates in other',
    r'shape the trajectory of one of the most',
    r'we develop reliable ai systems',
    r'anthropic is dedicated to developing',
    r'anthropic is building ai systems',
    r'scale ai is at the forefront',
    r'at scale, we develop',
    r'mission is to create reliable',
    r'committed researchers, engineers',
    r'werde teil der digitalen zukunft',
    r'req\s*id:',
    r'location:\s*',
    r'hybrid policy',
    r'visa sponsorship'
]

def is_boilerplate(text):
    if not text:
        return True
    t = text.lower()
    return any(re.search(p, t) for p in BOILERPLATE_PATTERNS)

def extract_real_responsibility(desc, fallback_snippet=""):
    if fallback_snippet and not is_boilerplate(fallback_snippet):
        return fallback_snippet
        
    if not desc:
        return ""
        
    # Split desc into sentences
    sentences = re.split(r'(?<=[.!?])\s+', desc)
    action_keywords = [
        'responsib', 'design', 'build', 'develop', 'architect', 'lead', 'manage',
        'support', 'analyz', 'implement', 'scale', 'train', 'evaluat', 'deploy',
        'partner', 'deliver', 'create', 'help large enterprises', 'work with'
    ]
    for sent in sentences:
        s = sent.strip()
        if len(s) < 30 or len(s) > 250:
            continue
        if is_boilerplate(s):
            continue
        s_lower = s.lower()
        if any(ak in s_lower for ak in action_keywords):
            # Clean up
            return s
            
    return ""

test_desc = "P-146 While candidates in the listed locations are encouraged for this role, we are open to remote candidates in other locations in various cities around the US. We are looking for experienced pre-sales professionals who have a successful track record helping large enterprises become more data-driven. The Solutions Architect is a senior technical customer-facing role. In this role, you will partner with our customers to design and build scalable data and AI architectures on Databricks."
print("Extracted from Databricks SA:", extract_real_responsibility(test_desc, "P-146 While candidates in the listed locations are encouraged for this role"))
