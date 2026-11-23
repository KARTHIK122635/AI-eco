import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

SPECIFIC_TARGET_EXCERPTS = {
    # 6 Mandated by user
    'job_d207b42e585bf8e6': "Design paid and digital campaign strategies for legislative and policy goals, including objectives, audiences, messaging, tactics, phasing, and budget",
    'job_80a480dfe5f61806': "Translate technical research, model capability, and scientific content into policy-ready language for federal, state, and international policymakers, their staff, and legislators.",
    'job_03adf198b79570b7': "Execute molecular biology and biochemistry experiments at the bench under the direction of senior scientists Maintain meticulous, reproducible records and contribute to shared protocols",
    'job_3ab4fad59bd0a42d': "Generate experimental and computational data, for example from quantum mechanical calculations, that research teams use to train and evaluate AI models",
    'job_b30c4117b32b2e1b': "Evaluate AI-designed antibodies, drive them to experimental readout, and feed results back to research teams",
    'job_d2ffb1910190a82b': "Invent the deal structures. You'll work with Scale’s legal team to define the first version of how these transactions get priced. Close. Own it from cold outreach to signature.",

    # Anthropic Product Support Specialists
    'job_db2382f595bbb7fd': "Respond to user support cases, in English and Japanese, with a variety of complexity, from simple billing or account questions for individuals to complex API debugging for large businesses",
    'job_38af1bff8a24f3e0': "Respond to user support cases with a variety of complexity, from simple billing or account questions for individuals to complex API debugging for large businesses",

    # Zilliz roles
    'job_14dc84751adf9885': "we help developers and enterprises build, deploy, and scale AI-powered applications, from semantic search and RAG to emerging agentic AI workloads.",
    'job_0c9a644f7ce24142': "You will work across both the cloud platform and database runtime, building cloud-and-engine integrated systems around Vector Lakebase so AI workloads can be scheduled faster, run more reliably, and serve real customers more efficiently.",
    'job_7a2f4f5d6e716be5': "Cloud-Native: Designed for elastic scaling and large-scale operation in the cloud\nLake-Native: Built on a data-lake architecture that works naturally with data at massive scale\nFor this team, scalability, performance, cost efficiency, and reliability are the core engineering goals.",
    'job_42f62c099c1fde9e': "You will read papers, evaluate new algorithms, build prototypes, and turn promising ideas into production-grade vector indexing and retrieval systems.",
    'job_e8015aba26dd5fc8': "You'll work with customers on real-world challenges involving vector search, RAG, AI agents, hybrid search, and other AI-powered applications.",

    # Anthropic specifically checked roles
    'job_49ea2bf597ea9b3b': "Design and run capability, uplift, and safety evaluations to assess cyber-relevant risk in new models",
    'job_b678befa49d8eca6': "Track payment schedules and rent recovery against each site's construction milestones, with Finance",
    'job_ef2b2e6a4d0da47e': "Conduct research and implement solutions in areas such as model architecture, algorithms, data processing, and optimizer development",
    'job_1e8b2d8ee5e34329': "Own the data strategy for vision capabilities end-to-end, from building evals and scaling RL environments",
    'job_b9afa5fa330d4cfe': "Design and build reinforcement learning environments for chemistry end to end, including task design, data curation, automated grading, and checks against shortcuts and data leakage",
    'job_9e3c061de5f3230d': "Develop and run expression and purification processes for antibodies and other recombinant proteins end to end, including transient and stable expression in mammalian cells (HEK293, CHO), affinity capture (Protein A, IMAC), polishing chromatography, buffer exchange, and formulation",
    'job_5239de691155afc1': "Rapidly design, prototype, and ship full-stack features across backend, frontend, and infrastructure",
    'job_3eb7f06aac9c95df': "Rapidly design, prototype, and ship full-stack features across backend, frontend, and infrastructure",
    'job_f3386228b7398977': "Architect and ship deployments that meet public sector compliance and security requirements, from FedRAMP to classified networks",
    'job_7bfbdf8b1ac820ea': "Negotiate Master Purchase Agreements, national pricing agreements, and blanket orders with manufacturers and distributors, including index-based pricing for copper, aluminum, and steel, capacity reservations, and volume rebates.",

    # Anthropic Community Engagement Managers
    'job_f8809da8ade216a4': "Develop and execute a community engagement strategy for each of your markets, spanning site selection, pre-development, construction, and ongoing operations",
    'job_547a71edc830f006': "Develop and execute a community engagement strategy for each of your markets, spanning site selection, pre-development, construction, and ongoing operations",
    'job_22ce0dd8878d0646': "Develop and execute a community engagement strategy for each of your markets, spanning site selection, pre-development, construction, and ongoing operations",
    'job_498f8f352202b404': "Develop and execute a community engagement strategy for each of your markets, spanning site selection, pre-development, construction, and ongoing operations",
    'job_932f15923af0d3cc': "Develop and execute a community engagement strategy for each of your markets, spanning site selection, pre-development, construction, and ongoing operations",
    'job_17d97fbfc48871d9': "Develop and execute a community engagement strategy for each of your markets, spanning site selection, pre-development, construction, and ongoing operations",
    'job_643aad676fad2d07': "Develop and execute a community engagement strategy for each of your markets, spanning site selection, pre-development, construction, and ongoing operations",

    # Residual 15 targets
    'job_84ec2ec6b9367148': "Review and investigate potential instances of Agentic Misalignment, working from transcripts, tool-use traces, and code",
    'job_d3243e36ab914802': "Set the team's investment strategy, deciding which teams get embedded engineers, and for how long, as demand outgrows the team",
    'job_38be0729c2816ee2': "Lead and develop a team of engineers building out features and foundations that make Claude enterprise-ready at scale",
    'job_87e7a826e1904b7b': "You’ll decide which security customers the team serves first, who you hire and in what order, and how the team works with Sales, Applied AI Engineering, and our security, legal, and trust partners.",
    'job_0186f49221af64aa': "Own growth for how people use Claude in their everyday work, end to end, as your full-time focus",
    'job_8341f8a6faee8aef': "Collaborate with product managers, engineers, AI researchers and other stakeholders to define product vision, strategy and roadmaps, and play an active role in shipping.",
    'job_c4a4457141216031': "Deeply engage with enterprise developers and technical leaders to understand their integration needs and pain points",
    'job_205d2992ea142ea2': "Determine how to build in safety by design upstream and leverage downstream defenses for Anthropic’s frontier models, AI products, customers on different surfaces - Claude.ai, 1P API, external Cloud providers.",
    'job_7cd7101cda12baa2': "Develop and execute strategic recruiting plans to identify, source, and hire highly qualified candidates, with a focus on Machine Learning and AI research talent",
    'job_ae1e07a4aa366094': "As a Research Engineer, you'll touch all parts of our code and infrastructure, whether that's making the cluster more reliable for our big jobs, improving throughput and efficiency, running and designing scientific experiments, or improving our dev tooling.",
    'job_b3d1e130c59fe4fc': "Own reseller onboarding for Japan and Korea end to end: application intake, screening coordination, agreement execution, marketplace authorization, entitlement setup, and activation, and keep the partner record in Salesforce decision-grade for both regions.",
    'job_3d50e2974f8de07f': "Own technical design and delivery for enterprise-facing products end-to-end across the stack—from admin consoles and governance surfaces to the APIs and data models behind them",
    'job_44dd96877e47a62c': "Define and drive multi-year technical strategy for foundational enterprise systems, including our distributability and multi-cloud direction",
    'job_038d41b8c91f9424': "Build security for large-scale AI clusters across multiple clouds and bare-metal data centers, including IAM, network segmentation and encryption controls",
    'job_70b073ff12a85c03': "The role translates third-party research, competitor disclosures, and benchmark data into roadmap, pricing, and positioning decisions, while building AI-powered tooling to make that intelligence faster, deeper, and more scalable."
}

# Verify all specific targets are exact substrings
for jid, text in SPECIFIC_TARGET_EXCERPTS.items():
    job = [j for j in jobs if j['jobId'] == jid][0]
    desc = job['jobDescription']
    assert text in desc, f"Target excerpt not in job description for {jid}: {text}"

BOILERPLATE_PATTERNS = [
    r'we are hiring\b',
    r'we\'re hiring\b',
    r'we’re hiring\b',
    r'we are looking\b',
    r'we\'re looking\b',
    r'we’re looking\b',
    r'we are seeking\b',
    r'we\'re seeking\b',
    r'we’re seeking\b',
    r'\bis seeking\b',
    r'\bis looking\b',
    r'\bis hiring\b',
    r'join the team\b',
    r'join our team\b',
    r'join us\b',
    r'^\s*join\b',
    r'about the role\b',
    r'about the team\b',
    r'about anthropic\b',
    r'about zilliz\b',
    r'about scale\b',
    r'about openai\b',
    r'about nebius\b',
    r'about mistral\b',
    r'^\s*about (?:the|us|anthropic|scale|openai|coreweave|our|this|zilliz|google|databricks|nebius|mistral)\b',
    r'who we are\b',
    r'our mission is\b',
    r'mission is to\b',
    r'central to anthropic\'s mission\b',
    r'safe and beneficial\b',
    r'quickly growing group\b',
    r'committed researchers\b',
    r'connective tissue between\b',
    r'research shows that people who identify\b',
    r'we encourage you to apply\b',
    r'how we\'re different\b',
    r'your safety matters\b',
    r'we believe that the highest-impact\b',
    r'come work with us\b',
    r'public benefit corporation\b',
    r'equal opportunity\b',
    r'affirmative action\b',
    r'visa sponsorship\b',
    r'team is building\b',
    r'is building the\b',
    r'is building a\b',
    r'builds RL environments\b',
    r'^\s*at [a-zA-Z0-9\s]+, we\b',
    r'^\s*come join\b',
    r'^\s*overview\b',
    r'^\s*the role\s*[:\n\-–—]?\s*$',
    r'^\s*the position\b',
    r'anthropic is\b',
    r'scale is\b',
    r'coreweave is\b',
    r'openai is\b',
    r'databricks is\b',
    r'cresta is\b',
    r'together ai is\b',
    r'figure ai is\b',
    r'snorkel is\b',
    r'cohere is\b',
    r'mistral is\b',
    r'nebius (?:token factory )?is\b',
    r'company [a-zA-Z0-9\s]+ is\b',
    r'^\s*we believe\b',
    r'^\s*we value\b',
    r'^\s*we think\b',
    r'^\s*you will join\b',
    r'^\s*in this role, you will join\b',
    r'we\'re a small design team\b',
    r'we\'re a small team\b',
    r'this research continues many of the directions\b',
    r'preferred qualifications\b',
    r'minimum qualifications\b',
    r'basic qualifications\b',
    r'minimum years of experience\b',
    r'coursework, training, or professional experience\b',
    r'in this pivotal role, you will be instrumental\b'
]

def contains_boilerplate(text):
    if not text:
        return True
    for p in BOILERPLATE_PATTERNS:
        if re.search(p, text.strip(), re.I):
            return True
    return False

def get_candidate_segments(text):
    segments = []
    lines = text.split('\n')
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        sub_sents = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', line_str)
        for s in sub_sents:
            s_clean = s.strip()
            s_clean_nobullet = re.sub(r'^[\s*•\-–—]+\s*', '', s_clean)
            if s_clean_nobullet and s_clean_nobullet in text:
                segments.append(s_clean_nobullet)
            elif s_clean and s_clean in text:
                segments.append(s_clean)
    return segments

def extract_clean_evidence(job):
    jid = job['jobId']
    if jid in SPECIFIC_TARGET_EXCERPTS:
        return SPECIFIC_TARGET_EXCERPTS[jid], True

    current_ev = (job.get('responsibilityEvidence') or '').strip()
    desc = job.get('jobDescription') or ''
    reason = job.get('classificationReason') or ''

    # If current evidence is good, not boilerplate, >= 30 chars, and verbatim substring
    if not contains_boilerplate(current_ev) and len(current_ev) >= 30 and current_ev in desc:
        return current_ev, False

    stop_words = {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'as', 'is', 'are', 'was', 'were', 'that', 'this', 'from'}
    reason_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', reason.lower())) - stop_words

    segments = get_candidate_segments(desc)
    candidates = []

    for s in segments:
        if s not in desc:
            continue
        if len(s) < 30 or len(s) > 350:
            continue
        if contains_boilerplate(s):
            continue
        if any(b in s.lower() for b in ['equal opportunity', 'visa sponsorship', 'benefits', 'salary range', 'accommodations', 'affirmative action', 'background check', 'how we\'re different', 'guidance on candidates', 'your safety matters', 'years experience', 'years of experience', 'degree in', 'bachelor\'s degree']):
            continue

        score = 0
        s_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', s.lower()))
        overlap = len(reason_words.intersection(s_words))
        score += overlap * 12

        # Reward strong duty verbs
        if re.match(r'^(?:You will|Lead|Manage|Design|Build|Develop|Own|Drive|Conduct|Implement|Architect|Support|Partner|Create|Oversee|Coordinate|Deliver|Execute|Maintain|Collaborate|Provide|Operate|Optimize|Scale|Ensure|Work with|Negotiate|Translate)\b', s, re.I):
            score += 20

        # Reward role/responsibility markers
        if re.search(r'\b(?:responsible for|responsibility|duties|work with|focus on)\b', s, re.I):
            score += 10

        candidates.append((score, s))

    candidates.sort(key=lambda x: x[0], reverse=True)
    if candidates and candidates[0][0] > 0:
        return candidates[0][1], True

    # Fallback if no candidate scored > 0: pick the longest non-boilerplate segment
    non_bp = [s for s in segments if not contains_boilerplate(s) and 35 <= len(s) <= 300 and s in desc]
    if non_bp:
        return non_bp[0], True

    return current_ev, False

if __name__ == '__main__':
    changed_count = 0
    remaining_boilerplate = []
    non_verbatim = []

    for j in jobs:
        ev, ch = extract_clean_evidence(j)
        desc = j.get('jobDescription') or ''
        if ch:
            changed_count += 1
        if ev not in desc:
            non_verbatim.append((j['jobId'], ev))
        if contains_boilerplate(ev):
            remaining_boilerplate.append((j['jobId'], j['companyName'], j['jobTitle'], ev))

    print(f"Total jobs evaluated: {len(jobs)}")
    print(f"Total updated: {changed_count}")
    print(f"Non-verbatim errors: {len(non_verbatim)}")
    print(f"Remaining boilerplate evidence: {len(remaining_boilerplate)}")

    if remaining_boilerplate:
        print("\n--- REMAINING BOILERPLATE ---")
        for r in remaining_boilerplate:
            print(r)
