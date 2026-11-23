import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

# Explicit targets mapping for the 6 specific records
SPECIFIC_TARGET_EXCERPTS = {
    'job_d207b42e585bf8e6': "Design paid and digital campaign strategies for legislative and policy goals, including objectives, audiences, messaging, tactics, phasing, and budget",
    'job_80a480dfe5f61806': "Translate technical research, model capability, and scientific content into policy-ready language for federal, state, and international policymakers, their staff, and legislators.",
    'job_03adf198b79570b7': "Execute molecular biology and biochemistry experiments at the bench under the direction of senior scientists Maintain meticulous, reproducible records and contribute to shared protocols",
    'job_3ab4fad59bd0a42d': "Generate experimental and computational data, for example from quantum mechanical calculations, that research teams use to train and evaluate AI models",
    'job_b30c4117b32b2e1b': "Evaluate AI-designed antibodies, drive them to experimental readout, and feed results back to research teams",
    'job_d2ffb1910190a82b': "Invent the deal structures. You'll work with Scale’s legal team to define the first version of how these transactions get priced. Close. Own it from cold outreach to signature."
}

# Verify all specific targets are exact substrings of their job description
for jid, text in SPECIFIC_TARGET_EXCERPTS.items():
    job = [j for j in jobs if j['jobId'] == jid][0]
    desc = job['jobDescription']
    assert text in desc, f"Target excerpt not in job description for {jid}: {text}"
print("Verified: All 6 specific target excerpts are exact verbatim substrings!")

SUSPECT_PATTERNS = [
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
    r'^\s*about (?:the|us|anthropic|scale|openai|coreweave|our|this|zilliz)\b',
    r'^\s*who we are\b',
    r'is seeking\b',
    r'is looking\b',
    r'is hiring\b',
    r'team is building\b',
    r'is building the\b',
    r'is building a\b',
    r'builds RL environments\b',
    r'^\s*at [a-zA-Z0-9\s]+, we\b',
    r'^\s*our mission is\b',
    r'^\s*come join\b',
    r'^\s*company [a-zA-Z0-9\s]+ is building\b',
    r'^\s*overview\b',
    r'^\s*the role\b',
    r'^\s*the position\b',
    r'^\s*about the role\b',
    r'^\s*about the team\b',
    r'^\s*we are an equal\b'
]

def is_suspect(text):
    if not text:
        return True
    for pat in SUSPECT_PATTERNS:
        if re.search(pat, text.strip(), re.I):
            return True
    return False

def extract_best_evidence_v12(job):
    jid = job['jobId']
    if jid in SPECIFIC_TARGET_EXCERPTS:
        return SPECIFIC_TARGET_EXCERPTS[jid], True

    desc = job.get('jobDescription') or ''
    reason = job.get('classificationReason') or ''
    current_ev = (job.get('responsibilityEvidence') or '').strip()

    if not is_suspect(current_ev) and len(current_ev) >= 30 and current_ev in desc:
        return current_ev, False

    raw_sents = re.split(r'(?<=[.!?])\s+', desc)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'as', 'is', 'are', 'was', 'were'}
    reason_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', reason.lower())) - stop_words

    candidates = []
    for s in raw_sents:
        s_clean = s.strip()
        if s_clean not in desc:
            continue
        if len(s_clean) < 30 or len(s_clean) > 350:
            continue
        if is_suspect(s_clean):
            continue
        if any(b in s_clean.lower() for b in ['equal opportunity', 'visa sponsorship', 'benefits', 'salary range', 'accommodations', 'affirmative action']):
            continue

        score = 0
        s_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', s_clean.lower()))
        overlap = len(reason_words.intersection(s_words))
        score += overlap * 10

        if re.match(r'^(?:You will|Lead|Manage|Design|Build|Develop|Own|Drive|Conduct|Implement|Architect|Support|Partner|Create|Oversee|Coordinate|Deliver|Execute)\b', s_clean, re.I):
            score += 15

        if re.match(r'^(?:Responsibilities|Key Responsibilities|In this role|Your mission|Your role)\b', s_clean, re.I):
            score += 5

        candidates.append((score, s_clean))

    candidates.sort(key=lambda x: x[0], reverse=True)
    if candidates and candidates[0][0] > 0:
        return candidates[0][1], True

    if current_ev in desc:
        return current_ev, False

    return current_ev, False

# Test across all 1930 records
changed_count = 0
still_suspect = []
for j in jobs:
    best_ev, changed = extract_best_evidence_v12(j)
    if changed:
        changed_count += 1
    if is_suspect(best_ev):
        still_suspect.append((j['jobId'], j['companyName'], j['jobTitle'], best_ev))

print(f"Total records updated: {changed_count}")
print(f"Total remaining suspect snippets: {len(still_suspect)}")
if still_suspect:
    for s in still_suspect:
        print(s)
