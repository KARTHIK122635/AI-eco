import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

INTRO_PATTERNS = [
    r'^\s*we are looking for\b',
    r'^\s*we are seeking\b',
    r'^\s*we’re looking for\b',
    r'^\s*we\'re looking for\b',
    r'^\s*we’re seeking\b',
    r'^\s*we\'re seeking\b',
    r'^\s*join our\b',
    r'^\s*join (?:anthropic|scale|openai|coreweave|our)\b',
    r'^\s*about (?:the|us|anthropic|scale|openai|coreweave|our|this)\b',
    r'^\s*who we are\b',
    r'^\s*at [a-zA-Z0-9\s]+, we\b',
    r'^\s*as a [a-zA-Z0-9\s]+ at [a-zA-Z0-9\s]+, you will join\b',
    r'^\s*our team is\b',
    r'^\s*our mission is\b',
    r'^\s*come join\b',
    r'is looking for a\b',
    r'is looking for an\b',
    r'is seeking a\b',
    r'is seeking an\b',
    r'^\s*overview\b',
    r'^\s*the role\b',
    r'^\s*the position\b',
    r'^\s*about the role\b',
    r'^\s*about the team\b',
    r'^\s*we are an equal\b'
]

def is_introductory(text):
    for pat in INTRO_PATTERNS:
        if re.search(pat, text.strip(), re.I):
            return True
    return False

def extract_best_evidence(job):
    desc = job.get('jobDescription') or ''
    reason = job.get('classificationReason') or ''
    current_ev = (job.get('responsibilityEvidence') or '').strip()
    
    # If current evidence is not introductory and has reasonable length and matches desc, we can evaluate it
    # But if it is introductory, we definitely need to find a better one
    needs_replacement = is_introductory(current_ev) or len(current_ev) < 20
    
    # Split desc into sentences
    raw_sents = re.split(r'(?<=[.!?])\s+', desc)
    
    # Clean reason terms for scoring
    stop_words = {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'as', 'is', 'are', 'was', 'were'}
    reason_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', reason.lower())) - stop_words
    
    candidates = []
    for s in raw_sents:
        s_clean = s.strip()
        # Must be exact substring of desc
        if s_clean not in desc:
            continue
        # Length filter
        if len(s_clean) < 30 or len(s_clean) > 350:
            continue
        # Check intro penalty
        if is_introductory(s_clean):
            continue
        # Check boilerplate penalty
        if any(b in s_clean.lower() for b in ['equal opportunity', 'visa sponsorship', 'benefits', 'salary range', 'accommodations', 'affirmative action']):
            continue
            
        # Score candidate
        score = 0
        s_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', s_clean.lower()))
        overlap = len(reason_words.intersection(s_words))
        score += overlap * 10
        
        # Boost for active verb beginnings
        if re.match(r'^(?:You will|Lead|Manage|Design|Build|Develop|Own|Drive|Conduct|Implement|Architect|Support|Partner|Create|Oversee|Coordinate|Deliver|Execute)\b', s_clean, re.I):
            score += 15
            
        # Boost for responsibility sections
        if re.match(r'^(?:Responsibilities|Key Responsibilities|In this role|Your mission|Your role)\b', s_clean, re.I):
            # If it starts with 'Key responsibilities Lead...', extract the lead part if possible or score it
            score += 5
            
        candidates.append((score, s_clean))
        
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    if candidates and candidates[0][0] > 0:
        return candidates[0][1], needs_replacement
    
    # Fallback to current evidence if valid verbatim substring
    if current_ev in desc:
        return current_ev, needs_replacement
        
    return current_ev, needs_replacement

# Run on flagged jobs
replaced_count = 0
examples = []

for j in jobs:
    current_ev = (j.get('responsibilityEvidence') or '').strip()
    if is_introductory(current_ev):
        best_ev, needed = extract_best_evidence(j)
        if best_ev != current_ev:
            replaced_count += 1
            if len(examples) < 10:
                examples.append((j['jobId'], j['companyName'], j['jobTitle'], j['classificationReason'], current_ev, best_ev))

print(f"Total introductory evidence replaced: {replaced_count}")
print("\nSample 5 replacements:")
for ex in examples[:5]:
    print(f"ID: {ex[0]} | {ex[1]} - {ex[2]}")
    print(f"  Reason:   {ex[3]}")
    print(f"  Old Ev:   {ex[4]}")
    print(f"  New Ev:   {ex[5]}")
    print("-" * 60)
