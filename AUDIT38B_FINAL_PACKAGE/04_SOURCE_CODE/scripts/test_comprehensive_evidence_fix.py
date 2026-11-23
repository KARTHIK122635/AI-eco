import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

SPECIFIC_TARGET_EXCERPTS = {
    # The 6 mandated by user
    'job_d207b42e585bf8e6': "Design paid and digital campaign strategies for legislative and policy goals, including objectives, audiences, messaging, tactics, phasing, and budget",
    'job_80a480dfe5f61806': "Translate technical research, model capability, and scientific content into policy-ready language for federal, state, and international policymakers, their staff, and legislators.",
    'job_03adf198b79570b7': "Execute molecular biology and biochemistry experiments at the bench under the direction of senior scientists Maintain meticulous, reproducible records and contribute to shared protocols",
    'job_3ab4fad59bd0a42d': "Generate experimental and computational data, for example from quantum mechanical calculations, that research teams use to train and evaluate AI models",
    'job_b30c4117b32b2e1b': "Evaluate AI-designed antibodies, drive them to experimental readout, and feed results back to research teams",
    'job_d2ffb1910190a82b': "Invent the deal structures. You'll work with Scale’s legal team to define the first version of how these transactions get priced. Close. Own it from cold outreach to signature.",
    # Additional specific inspected cases
    'job_db2382f595bbb7fd': "Respond to user support cases, in English and Japanese, with a variety of complexity, from simple billing or account questions for individuals to complex API debugging for large businesses",
    'job_38af1bff8a24f3e0': "Respond to user support cases with a variety of complexity, from simple billing or account questions for individuals to complex API debugging for large businesses",
    'job_14dc84751adf9885': "we help developers and enterprises build, deploy, and scale AI-powered applications, from semantic search and RAG to emerging agentic AI workloads.",
    'job_0c9a644f7ce24142': "You will work across both the cloud platform and database runtime, building cloud-and-engine integrated systems around Vector Lakebase so AI workloads can be scheduled faster, run more reliably, and serve real customers more efficiently.",
    'job_7a2f4f5d6e716be5': "Cloud-Native: Designed for elastic scaling and large-scale operation in the cloud\nLake-Native: Built on a data-lake architecture that works naturally with data at massive scale\nFor this team, scalability, performance, cost efficiency, and reliability are the core engineering goals.",
    'job_42f62c099c1fde9e': "You will read papers, evaluate new algorithms, build prototypes, and turn promising ideas into production-grade vector indexing and retrieval systems.",
    'job_e8015aba26dd5fc8': "You'll work with customers on real-world challenges involving vector search, RAG, AI agents, hybrid search, and other AI-powered applications.",
}

# Verify specific targets
for jid, text in SPECIFIC_TARGET_EXCERPTS.items():
    job = [j for j in jobs if j['jobId'] == jid][0]
    desc = job['jobDescription']
    assert text in desc, f"Missing target {jid}: {text}"

PROMOTIONAL_PATTERNS = [
    r'^\s*we are hiring\b',
    r'^\s*we\'re hiring\b',
    r'^\s*we’re hiring\b',
    r'^\s*we are looking\b',
    r'^\s*we\'re looking\b',
    r'^\s*we’re looking\b',
    r'^\s*we are seeking\b',
    r'^\s*we\'re seeking\b',
    r'^\s*we’re seeking\b',
    r'^\s*join\b',
    r'^\s*about (?:the|us|anthropic|scale|openai|coreweave|our|this|zilliz|google|databricks|nebius|mistral)\b',
    r'^\s*who we are\b',
    r'\bis seeking\b',
    r'\bis looking\b',
    r'\bis hiring\b',
    r'team is building\b',
    r'is building the\b',
    r'is building a\b',
    r'builds RL environments\b',
    r'^\s*at [a-zA-Z0-9\s]+, we\b',
    r'^\s*our mission is\b',
    r'^\s*come join\b',
    r'^\s*overview\b',
    r'^\s*the role\b',
    r'^\s*the position\b',
    r'^\s*about the role\b',
    r'^\s*about the team\b',
    r'^\s*we are an equal\b',
    r'^\s*anthropic is\b',
    r'^\s*scale is\b',
    r'^\s*coreweave is\b',
    r'^\s*openai is\b',
    r'^\s*databricks is\b',
    r'^\s*cresta is\b',
    r'^\s*together ai is\b',
    r'^\s*figure ai is\b',
    r'^\s*snorkel is\b',
    r'^\s*cohere is\b',
    r'^\s*mistral is\b',
    r'^\s*nebius (?:token factory )?is\b',
    r'^\s*company [a-zA-Z0-9\s]+ is\b',
    r'^\s*we believe\b',
    r'^\s*we value\b',
    r'^\s*we think\b',
    r'^\s*you will join\b',
    r'^\s*in this role, you will join\b'
]

def is_promotional(text):
    if not text:
        return True
    for p in PROMOTIONAL_PATTERNS:
        if re.search(p, text.strip(), re.I):
            return True
    return False

def get_clean_sentences(text):
    # Split text into candidate segments by newlines, bullets, and sentence endings
    # Preserving exact substrings
    raw_segments = []
    # Split by newlines first
    lines = text.split('\n')
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        # If line contains multiple sentences, split by period followed by space and capital
        sub_sents = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', line_str)
        for s in sub_sents:
            s_clean = s.strip()
            # Strip common bullet points if at start
            s_clean_nobullet = re.sub(r'^[\s*•\-–—]+\s*', '', s_clean)
            if s_clean_nobullet and s_clean_nobullet in text:
                raw_segments.append(s_clean_nobullet)
            elif s_clean and s_clean in text:
                raw_segments.append(s_clean)
    return raw_segments

def extract_substantive_evidence(job):
    jid = job['jobId']
    if jid in SPECIFIC_TARGET_EXCERPTS:
        return SPECIFIC_TARGET_EXCERPTS[jid], True

    current_ev = (job.get('responsibilityEvidence') or '').strip()
    desc = job.get('jobDescription') or ''
    reason = job.get('classificationReason') or ''

    # If current evidence is good, not promotional, >= 30 chars, and verbatim substring
    if not is_promotional(current_ev) and len(current_ev) >= 30 and current_ev in desc:
        return current_ev, False

    stop_words = {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'as', 'is', 'are', 'was', 'were', 'that', 'this', 'from'}
    reason_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', reason.lower())) - stop_words

    segments = get_clean_sentences(desc)
    candidates = []

    for s in segments:
        if s not in desc:
            continue
        if len(s) < 30 or len(s) > 350:
            continue
        if is_promotional(s):
            continue
        if any(b in s.lower() for b in ['equal opportunity', 'visa sponsorship', 'benefits', 'salary range', 'accommodations', 'affirmative action', 'background check', 'how we\'re different', 'guidance on candidates', 'your safety matters']):
            continue

        score = 0
        s_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', s.lower()))
        overlap = len(reason_words.intersection(s_words))
        score += overlap * 12

        # Reward strong duty verbs
        if re.match(r'^(?:You will|Lead|Manage|Design|Build|Develop|Own|Drive|Conduct|Implement|Architect|Support|Partner|Create|Oversee|Coordinate|Deliver|Execute|Maintain|Collaborate|Provide|Operate|Optimize|Scale|Ensure|Work with)\b', s, re.I):
            score += 20

        # Reward role/responsibility markers
        if re.search(r'\b(?:responsible for|responsibility|duties|work with|focus on)\b', s, re.I):
            score += 10

        candidates.append((score, s))

    candidates.sort(key=lambda x: x[0], reverse=True)
    if candidates and candidates[0][0] > 0:
        return candidates[0][1], True

    # Fallback if no candidate scored > 0: pick the longest non-promotional segment
    non_promo = [s for s in segments if not is_promotional(s) and 35 <= len(s) <= 300 and s in desc]
    if non_promo:
        return non_promo[0], True

    return current_ev, False

# Test run across all 1930 jobs
updated = 0
remaining_suspect = []
non_verbatim = []

for j in jobs:
    ev, changed = extract_substantive_evidence(j)
    desc = j.get('jobDescription') or ''
    if changed:
        updated += 1
    if ev not in desc:
        non_verbatim.append((j['jobId'], ev))
    if is_promotional(ev):
        remaining_suspect.append((j['jobId'], j['companyName'], j['jobTitle'], ev))

print(f"Total jobs evaluated: {len(jobs)}")
print(f"Total updated: {updated}")
print(f"Non-verbatim errors: {len(non_verbatim)}")
print(f"Remaining suspect/promotional evidence: {len(remaining_suspect)}")

if remaining_suspect:
    print("\n--- REMAINING SUSPECT ---")
    for r in remaining_suspect:
        print(r)
