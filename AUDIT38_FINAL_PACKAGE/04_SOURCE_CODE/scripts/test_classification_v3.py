import json
import re
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

def classify_role_v3(title: str, desc: str, comp: str):
    t = title.lower()
    d = (desc or "").lower()

    # Specific role checks first

    # 1. NON_TECHNICAL (Finance, Accounting, Procurement, Sourcing, Asset Management, Real Estate, Community, Legal, GRC, Compliance, HR, Recruiting, Sales, Business Ops)
    # Check for non-technical leadership/functions even if they mention AI, GPU, Data Center, Infra:
    non_tech_exact_patterns = [
        # Finance & Investment
        r'\bfinance\b', r'\baccounting\b', r'\baccountant\b', r'\btax\b', r'\bpayroll\b',
        r'\bbilling\b', r'\bcontroller\b', r'\btreasury\b', r'\bfinancial\b', r'\bdebt capital\b',
        r'\binvestment strategy\b', r'\bcommercial associate\b',
        # Procurement, Sourcing & Asset Management
        r'\bstrategic sourcing\b', r'\bsourcing lead\b', r'\bsourcing manager\b', r'\bprocurement\b',
        r'\basset management\b', r'\bmaterials planner\b', r'\bsupply chain\b', r'\blogistics manager\b',
        # Community, Communications, PR & Marketing (Non-Product)
        r'\bcommunity engagement\b', r'\bcommunications\b', r'\bpr manager\b', r'\bpublic relations\b',
        r'\bbrand marketing\b', r'\bgrowth marketing\b', r'\bcontent marketing\b', r'\bevents manager\b',
        r'\bexternal affairs\b', r'\bgovernment affairs\b',
        # Policy, Economics & Governance
        r'\beconomics & policy\b', r'\bpolicy\b', r'\beconomic\b', r'\bfellows program.*policy\b',
        # Legal, GRC, Compliance & Audit
        r'\blegal\b', r'\bcounsel\b', r'\bparalegal\b', r'\bcompliance\b', r'\bgrc\b', r'\baudit\b',
        r'\btrade compliance\b', r'\bregulatory\b',
        # People, Recruiting & Workplace
        r'\brecruit', r'\btalent\b', r'\bpeople partner\b', r'\bpeople operations\b', r'\bhuman resources\b',
        r'\bhr\b', r'\bbenefits\b', r'\bequity admin\b', r'\bworkplace\b', r'\bfacilities\b',
        r'\boffice manager\b', r'\bexecutive assistant\b', r'\badministrative\b', r'\breceptionist\b',
        # Sales & Commercial
        r'\baccount executive\b', r'\bsales director\b', r'\bsales manager\b', r'\benterprise sales\b',
        r'\bcommercial sales\b', r'\bbusiness development\b', r'\bsales development\b', r'\brenewals\b',
        r'\bgtm enablement\b', r'\bpartner account\b', r'\bstrategic pursuits\b', r'\bchannel partner\b',
        r'\bcustomer success manager\b', r'\bcustomer support\b', r'\bsupport agent\b',
        # Operations (Non-engineering)
        r'\bbusiness operations\b', r'\bchief of staff\b', r'\boperations lead\b', r'\boperations associate\b',
        r'\bprogram manager.*finance\b', r'\bdemand planning\b'
    ]

    for pat in non_tech_exact_patterns:
        if re.search(pat, t):
            # Exception for technical solutions or sales engineering
            if not any(sw in t for sw in ["solutions architect", "sales engineer", "technical account manager", "solutions engineer"]):
                return "NON_TECHNICAL", "Corporate business, financial, procurement, legal, compliance, policy, talent, or operations function"

    # 2. CORE_AI_ML (Algorithm, Model Architecture, Pre/Post-training, LLM, Computer Vision, Research Science, NLP, ML/DL)
    core_ai_patterns = [
        r'\bmachine learning\b', r'\bml engineer\b', r'\bdeep learning\b', r'\bcomputer vision\b',
        r'\bnlp\b', r'\bnatural language\b', r'\bresearch scientist\b', r'\bai researcher\b',
        r'\bresearch engineer\b', r'\bapplied scientist\b', r'\bai scientist\b', r'\bresearch resident\b',
        r'\bllm\b', r'\bprompt engineer\b', r'\bfoundation model\b', r'\balignment\b', r'\bai safety\b',
        r'\bpost-training\b', r'\bpre-training\b', r'\breinforcement learning\b', r'\bgenerative ai\b',
        r'\bmlops\b', r'\bai engineer\b', r'\bdata scientist\b', r'\bdata science\b',
        r'\brobotics engineer\b', r'\bperception engineer\b', r'\bspeech\b'
    ]
    for pat in core_ai_patterns:
        if re.search(pat, t):
            return "CORE_AI_ML", "Direct machine learning, deep learning, LLM, or AI research engineering"

    # 3. AI_INFRASTRUCTURE (Technical Compute Cluster, GPU, CUDA, Triton, Accelerator, HPC Systems Engineering)
    # Must be technical engineering / systems roles!
    ai_infra_patterns = [
        r'\bgpu\b.*(?:engineer|systems|cluster|kernel|software|architect|infra)',
        r'\bcuda\b', r'\btriton\b', r'\bkernel\b', r'\baccelerator\b',
        r'\bcompute infrastructure\b', r'\bcluster operations\b', r'\bhpc\b',
        r'\bhigh performance computing\b', r'\bdistributed training\b',
        r'\bmodel serving\b', r'\binference infrastructure\b',
        r'\bdata center\b.*(?:engineer|architect|technician|network|systems)',
        r'\bdatacenter\b.*(?:engineer|architect|technician|network|systems)',
        r'\bhardware engineer\b', r'\basic\b', r'\bfpga\b',
        r'\bnetwork engineer\b', r'\bsre\b.*(?:infra|cluster|gpu|compute)'
    ]
    for pat in ai_infra_patterns:
        if re.search(pat, t):
            return "AI_INFRASTRUCTURE", "High-performance compute, GPU cluster, accelerator, or distributed systems infrastructure engineering"

    # 4. AI_PRODUCT_SOLUTIONS (Solutions Architect, Forward Deployed, AI Product Manager, Technical Enablement)
    ai_prod_patterns = [
        r'\bsolutions architect\b', r'\bsolution architect\b', r'\bforward deployed\b',
        r'\btechnical account manager\b', r'\bproduct manager\b', r'\btechnical product manager\b',
        r'\bdeveloper advocate\b', r'\bdeveloper relations\b', r'\bapplied ai architect\b',
        r'\bfield engineer\b', r'\btechnical solutions\b', r'\bproduct designer\b'
    ]
    for pat in ai_prod_patterns:
        if re.search(pat, t):
            return "AI_PRODUCT_SOLUTIONS", "AI solutions architecture, forward deployed customer engineering, or AI technical product management"

    # 5. AI_SUPPORTING_TECH (Software, Platform, Backend, Data, Security Engineering at AI Companies or supporting AI)
    pure_play = [
        "anthropic", "scale ai", "together ai", "coreweave", "sambanova",
        "cresta", "snorkel", "figure", "labelbox", "stability", "zilliz", "databricks"
    ]
    is_pure_play = any(pp in comp.lower() for pp in pure_play)

    supporting_tech_patterns = [
        r'\bsoftware engineer\b', r'\bbackend engineer\b', r'\bfrontend engineer\b',
        r'\bfull stack\b', r'\bdata engineer\b', r'\bplatform engineer\b',
        r'\binfrastructure engineer\b', r'\bdevops\b', r'\bsecurity engineer\b',
        r'\bcloud engineer\b', r'\bfirmware\b', r'\bembedded\b', r'\bsre\b',
        r'\bsite reliability\b', r'\bqa engineer\b', r'\btest engineer\b',
        r'\btechnical program manager\b', r'\btpm\b', r'\barchitect\b'
    ]
    for pat in supporting_tech_patterns:
        if re.search(pat, t):
            if is_pure_play:
                return "AI_SUPPORTING_TECH", f"Core software, platform, security, or data engineering supporting AI systems at {comp}"
            elif any(k in d for k in ["machine learning", "deep learning", "ai model", "llm", "neural", "pytorch", "tensorflow"]):
                return "AI_SUPPORTING_TECH", "Engineering role with substantive AI/ML tech stack in description"
            else:
                return "NON_AI_TECH", "General software or infrastructure engineering without substantive AI specialization"

    # 6. NON_AI_TECH
    non_ai_tech_patterns = [
        r'\bit support\b', r'\bsysadmin\b', r'\bsystems administrator\b', r'\bhelpdesk\b',
        r'\bdesktop support\b', r'\bit specialist\b', r'\bdatabase administrator\b'
    ]
    for pat in non_ai_tech_patterns:
        if re.search(pat, t):
            return "NON_AI_TECH", "Traditional enterprise IT support, systems administration, or database maintenance"

    # Fallback based on pure-play vs general
    if is_pure_play:
        if any(w in t for w in ["engineer", "developer", "architect", "systems"]):
            return "AI_SUPPORTING_TECH", f"Technical engineering position at {comp}"
        return "NON_TECHNICAL", f"Corporate operational function at {comp}"

    if any(w in t for w in ["engineer", "developer"]):
        return "NON_AI_TECH", "Generic software engineering role from general job board"

    return "UNCERTAIN", "Title and description do not provide sufficient evidence to classify definitively"

# Test specific user examples
test_roles = [
    ("Community Engagement Manager, Data Centers", "", "CoreWeave"),
    ("Data Center Asset Management, Commercial Associate", "", "CoreWeave"),
    ("Data Center Strategic Sourcing Lead", "", "CoreWeave"),
    ("Product Finance Director, AI Products & GPU Investment Strategy", "", "Anthropic"),
    ("Anthropic Fellows Program, The Anthropic Institute (Economics & Policy)", "", "Anthropic"),
    ("Audit, Security GRC", "", "Anthropic"),
    ("3P Revenue Accounting & Reporting", "", "Anthropic"),
    ("APAC Tax Lead", "", "Anthropic"),
    ("Recruiting Coordinator", "", "Anthropic"),
    ("Account Executive, AI Native", "", "Anthropic"),
    ("Anthropic Research Resident", "", "Anthropic"),
    ("Compute Infrastructure Engineer", "", "CoreWeave")
]

print("=== User Review Examples Verification ===")
for title, desc, comp in test_roles:
    cat, reason = classify_role_v3(title, desc, comp)
    print(f"  {title:<64} -> {cat:<22} ({reason[:60]}...)")

# Run on all 1,930 jobs
counts = Counter()
for j in jobs:
    cat, reason = classify_role_v3(j['jobTitle'], j.get('jobDescription', ''), j['companyName'])
    counts[cat] += 1

print("\n=== Full Dataset Classification Breakdown (1,930 jobs) ===")
for cat, cnt in counts.most_common():
    print(f"  {cat:<24}: {cnt:>4} ({cnt/len(jobs)*100:.1f}%)")
