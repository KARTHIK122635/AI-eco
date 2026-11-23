import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

EXACT_PROMOTIONAL_PATTERNS = [
    r'\bmission\b',
    r'\bculture\b',
    r'\bwe believe\b',
    r'\bwe think\b',
    r'\bwe view\b',
    r'\bwe are building\b',
    r'\bis building\b',
    r'\bteam is building\b',
    r'\byou will join\b',
    r'\byou\'ll join\b',
    r'\byou’ll join\b',
    r'\bjoin our\b',
    r'\bjoin the\b',
    r'\bjoin us\b',
    r'^\s*join\b',
    r'\bfoundational to our\b',
    r'\bcore part of\b',
    r'\bsoftware is eating the world\b',
    r'\bthe team is based\b',
    r'\borganization is foundational\b',
    r'\borganization makes sure\b',
    r'\bdeep part of our\b',
    r'\bat [A-Z][a-zA-Z0-9\s]+, we\b',
    r'\bwe are a\b',
    r'\bwe\'re a\b',
    r'\bwe’re a\b',
    r'\bour goal is\b',
    r'\bour vision is\b',
    r'\bour team\b',
    r'\babout (?:us|the|our|scale|anthropic|coreweave|openai|databricks|nebius)\b',
    r'^\s*as an? [^.]*?(?:you will join|welcome to)\b',
    r'\bwe are hiring\b',
    r'\bwe\'re hiring\b',
    r'\bwe are looking\b',
    r'\bwe\'re looking\b',
    r'\bis hiring\b',
    r'\bis looking\b',
    r'\bis seeking\b',
    r'\bwho we are\b',
    r'\babout the role\b',
    r'\babout the team\b'
]

def is_promotional(text):
    if not text:
        return True
    for p in EXACT_PROMOTIONAL_PATTERNS:
        if re.search(p, text.strip(), re.I):
            return True
    return False

# Explicit targets mapping for known prompt targets
AUDIT13_EXPLICIT_TARGETS = {
    # Section 1 examples from prompt
    'job_090ae3e6187d0e95': "Lead a team of engineers building the connectivity infrastructure that powers tool use across Anthropic's product suite, from the MCP proxy to OAuth and token management",
    'job_99a16541f25f6011': "Own the technical strategy and roadmap for agent-driven cluster lifecycle management - provisioning, updates and decommissioning",
    'job_8fa1c552d19c1545': "You'll design, build, and operate the core connectivity infrastructure behind external tool calls — the MCP proxy and the OAuth and token management systems that keep connections authenticated.",
    'job_312c813f6ac2ff0d': "Act as the interface between research and the outside world. Stay close to the researchers working on Claude's scientific capabilities and translate rapid capability gain into use by external researchers.",
    'job_95b43ad5f542500c': "Serve as the Finance business partner to support the Applications BU Leadership Team in quarterly and annual strategic and financial planning discussions",
    'job_5fcaf184c259b65a': "Quickly respond to all inbound support requests, including email, live chat, and community forums",
    'job_61fd4233c744a6f8': "Respond to inbound support requests across email, Slack, and community forums, triaging by customer tier and severity and meeting response SLAs",
    'job_a8b0b2fba1f2d038': "Respond to inbound support requests across email, Slack, and community forums, triaging by customer tier and severity and meeting response SLAs",
    'job_61144ba521cc8449': "Drive AI Runtime's architecture and lead Databricks' long-term technical direction in AI training infrastructure.",
    'job_1b9058f92fab34da': "Some weeks you might be optimizing how training loads are scheduled on our cluster and making the pipeline more robust and performant so we can iterate faster.",
    'job_366b4bea010eed1f': "Some weeks you might be optimizing how training loads are scheduled on our cluster and making the pipeline more robust and performant so we can iterate faster.",
    'job_889d2fb771307d3f': "You'll design clean abstractions for a rapidly evolving business model, build reliable distributed workflows where correctness and consistency are as important as performance, and help shape a modern platform from the ground up.",
    'job_2c80e5fb066f0e51': "Own and improve the reliability, performance, and capacity of our YTsaurus clusters, with particular attention to data durability and predictable behavior under load.",
    'job_10c062ac3703d86a': "Own and improve the reliability, performance, and capacity of our YTsaurus clusters, with particular attention to data durability and predictable behavior under load.",
    'job_56be0fafcdaa036c': "take a leadership role in both internal and external projects while actively building strong relationships with clients to expand into additional engagements",
    'job_2131aa478b54ee53': "play a key role in technical consulting and implementation, particularly on external client projects",
    'job_3c5d6884b25b32d7': "contribute to client projects and play and active role in development tasks",
    
    # Section 2 Mandated Audit 12 targets preserved
    'job_d207b42e585bf8e6': "Design paid and digital campaign strategies for legislative and policy goals, including objectives, audiences, messaging, tactics, phasing, and budget",
    'job_80a480dfe5f61806': "Translate technical research, model capability, and scientific content into policy-ready language for federal, state, and international policymakers, their staff, and legislators.",
    'job_03adf198b79570b7': "Execute molecular biology and biochemistry experiments at the bench under the direction of senior scientists Maintain meticulous, reproducible records and contribute to shared protocols",
    'job_3ab4fad59bd0a42d': "Generate experimental and computational data, for example from quantum mechanical calculations, that research teams use to train and evaluate AI models",
    'job_b30c4117b32b2e1b': "Evaluate AI-designed antibodies, drive them to experimental readout, and feed results back to research teams",
    'job_d2ffb1910190a82b': "Invent the deal structures. You'll work with Scale’s legal team to define the first version of how these transactions get priced. Close. Own it from cold outreach to signature.",
}

# Verify all explicit targets are verbatim substrings
for jid, text in AUDIT13_EXPLICIT_TARGETS.items():
    job = [j for j in jobs if j['jobId'] == jid][0]
    assert text in job['jobDescription'], f"Missing target in {jid}: {text}"
print(f"Verified all {len(AUDIT13_EXPLICIT_TARGETS)} explicit targets are exact verbatim substrings!")

def get_candidate_sentences(text):
    candidates = []
    lines = text.split('\n')
    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
        sub_sents = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', line_s)
        for s in sub_sents:
            s_clean = s.strip()
            s_clean_nobullet = re.sub(r'^[\s*•\-–—:]+\s*', '', s_clean)
            if s_clean_nobullet and s_clean_nobullet in text:
                candidates.append(s_clean_nobullet)
            elif s_clean and s_clean in text:
                candidates.append(s_clean)
    return candidates

def clean_evidence_v13(job):
    jid = job['jobId']
    if jid in AUDIT13_EXPLICIT_TARGETS:
        return AUDIT13_EXPLICIT_TARGETS[jid], True

    current_ev = (job.get('responsibilityEvidence') or '').strip()
    desc = job.get('jobDescription') or ''
    reason = job.get('classificationReason') or ''

    if not is_promotional(current_ev) and len(current_ev) >= 30 and current_ev in desc:
        return current_ev, False

    stop_words = {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'as', 'is', 'are', 'was', 'were', 'that', 'this', 'from'}
    reason_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', reason.lower())) - stop_words

    segments = get_candidate_sentences(desc)
    ranked = []
    for s in segments:
        if s not in desc:
            continue
        if len(s) < 30 or len(s) > 350:
            continue
        if is_promotional(s):
            continue
        if any(b in s.lower() for b in ['equal opportunity', 'visa sponsorship', 'benefits', 'salary range', 'accommodations', 'affirmative action', 'background check', 'how we\'re different', 'guidance on candidates', 'your safety matters', 'years experience', 'years of experience', 'degree in', 'bachelor\'s degree']):
            continue

        score = 0
        s_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', s.lower()))
        overlap = len(reason_words.intersection(s_words))
        score += overlap * 12

        if re.match(r'^(?:You will|Lead|Manage|Design|Build|Develop|Own|Drive|Conduct|Implement|Architect|Support|Partner|Create|Oversee|Coordinate|Deliver|Execute|Maintain|Collaborate|Provide|Operate|Optimize|Scale|Ensure|Work with|Negotiate|Translate|Investigate|Direct)\b', s, re.I):
            score += 25

        if re.search(r'\b(?:responsible for|responsibility|duties|work with|focus on)\b', s, re.I):
            score += 10

        ranked.append((score, s))

    ranked.sort(key=lambda x: x[0], reverse=True)
    if ranked and ranked[0][0] > 0:
        return ranked[0][1], True

    non_promo = [s for s in segments if not is_promotional(s) and 35 <= len(s) <= 300 and s in desc]
    if non_promo:
        return non_promo[0], True

    return current_ev, False

# Sweep all jobs
updated_count = 0
remaining_promo = []
non_verbatim = []

for j in jobs:
    ev, ch = clean_evidence_v13(j)
    desc = j.get('jobDescription') or ''
    if ch:
        updated_count += 1
    if ev not in desc:
        non_verbatim.append((j['jobId'], ev))
    if is_promotional(ev):
        remaining_promo.append((j['jobId'], j['companyName'], j['jobTitle'], ev))

print(f"Total jobs: {len(jobs)}")
print(f"Updated: {updated_count}")
print(f"Non-verbatim errors: {len(non_verbatim)}")
print(f"Remaining promotional: {len(remaining_promo)}")

if remaining_promo:
    for r in remaining_promo:
        print(r)
