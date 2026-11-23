import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

def norm_ws(s):
    if not s: return ""
    return re.sub(r'\s+', ' ', s.replace('\u00a0', ' ').replace('\u202f', ' ')).strip()

def extract_verbatim_slice(desc: str, start_pos: int, max_len: int = 280) -> str:
    """
    Given a start position in desc, extracts a clean, sentence-bounded, verbatim substring.
    Guaranteed: norm_ws(slice) in norm_ws(desc).
    """
    raw_slice = desc[start_pos:start_pos + max_len + 50]
    # Trim leading whitespace
    while start_pos < len(desc) and desc[start_pos].isspace():
        start_pos += 1
    
    # We want a slice up to max_len that ends on a sentence boundary (period + space/newline/capital, or just period)
    # Find all periods within [start_pos + 40, start_pos + max_len]
    search_end = min(len(desc), start_pos + max_len)
    
    # Try to find a period followed by space or newline or capital
    best_end = -1
    for m in re.finditer(r'\.(?:\s+[A-Z]|\s*\n|\s*$)', desc[start_pos:search_end + 30]):
        period_pos = start_pos + m.start() + 1
        if period_pos <= start_pos + max_len:
            best_end = period_pos
        elif best_end == -1 and period_pos <= start_pos + max_len + 25:
            best_end = period_pos
            
    if best_end != -1 and (best_end - start_pos) >= 40:
        res = desc[start_pos:best_end].strip()
    else:
        # Fall back to word boundary
        cutoff = min(len(desc), start_pos + max_len)
        # Find last space
        last_space = desc.rfind(' ', start_pos, cutoff)
        if last_space != -1 and (last_space - start_pos) >= 40:
            res = desc[start_pos:last_space].strip()
        else:
            res = desc[start_pos:cutoff].strip()

    return res

def get_evidence_v5(desc: str, title: str, company: str):
    if not desc:
        return None, None
        
    desc_norm = norm_ws(desc)
    
    # -------------------------------------------------------------
    # 1. RESPONSIBILITY EVIDENCE
    # -------------------------------------------------------------
    resp_ev = None
    
    # Responsibilities patterns (headers)
    resp_pats = [
        r'(?:Key\s+responsibilities|Core\s+responsibilities|Primary\s+responsibilities|Responsibilities|What\s+you(?:’|\')ll\s+do|What\s+you\s+will\s+do|What\s+You(?:’|\')ll\s+Do|What\s+You\s+Will\s+Do|What\s+you(?:\'|’)?ll\s+be\s+doing|Your\s+role|About\s+the\s+role|The\s+role|Tasks|Missions|What\s+to\s+expect|Role\s+Overview|Overview)[:\s]+',
    ]
    
    # If Fellows Program
    if "fellows program" in title.lower():
        m_exp = re.search(r'What to expect\s+', desc, re.I)
        if m_exp:
            resp_ev = extract_verbatim_slice(desc, m_exp.end(), 260)
        else:
            m_ov = re.search(r'Anthropic Fellows Program overview\s+', desc, re.I)
            if m_ov:
                resp_ev = extract_verbatim_slice(desc, m_ov.end(), 260)

    if not resp_ev:
        for pat in resp_pats:
            matches = list(re.finditer(pat, desc))
            if not matches:
                matches = list(re.finditer(pat, desc, re.I))
            for m in matches:
                pos = m.end()
                # Check that next text is not logistics or salary
                check_ahead = desc[pos:pos+100].lower()
                if any(bad in check_ahead for bad in ['minimum education', 'visa', 'location-based', 'compensation', 'salary', 'equal opportunity']):
                    continue
                cand = extract_verbatim_slice(desc, pos, 260)
                if cand and len(cand) > 30 and norm_ws(cand) in desc_norm:
                    resp_ev = cand
                    break
            if resp_ev:
                break
                
    if not resp_ev:
        # Fall back to opening paragraph of description that is not company boilerplate
        # find where company boilerplate ends
        m_start = 0
        for bp in [r'About\s+Anthropic[^\n.]+[\n.]+', r'About\s+Us[^\n.]+[\n.]+', r'Company\s+Description:[^\n.]+[\n.]+']:
            mb = re.search(bp, desc, re.I)
            if mb and mb.start() < 100:
                m_start = max(m_start, mb.end())
        cand = extract_verbatim_slice(desc, m_start, 260)
        if cand and len(cand) > 30 and norm_ws(cand) in desc_norm:
            resp_ev = cand

    # -------------------------------------------------------------
    # 2. QUALIFICATION EVIDENCE
    # -------------------------------------------------------------
    qual_ev = None
    
    # Header patterns for required qualifications ONLY
    qual_pats = [
        r'(?:Minimum\s+qualifications|Basic\s+qualifications|Required\s+qualifications|Qualifications|Requirements|What\s+you\s+bring|What\s+You\s+Bring|What\s+you(?:’|\')ll\s+need|What\s+you\s+need|What\s+we(?:’|\')re\s+looking\s+for|What\s+We(?:’|\')re\s+Looking\s+For|Who\s+we(?:’|\')re\s+looking\s+for|Who\s+You\s+Are|Who\s+you\s+are|You\s+may\s+be\s+a\s+good\s+fit\s+if\s+you\s+have|You\s+might\s+be\s+a\s+good\s+fit\s+if\s+you\s+have|You\s+Might\s+Be\s+a\s+Good\s+Fit\s+If\s+You\s+Have|You\s+may\s+be\s+a\s+good\s+fit\s+if\s+you|You\s+might\s+be\s+a\s+good\s+fit\s+if\s+you|You\s+may\s+be\s+a\s+good\s+fit|You\s+might\s+be\s+a\s+good\s+fit|Candidate\s+profile|Skills\s+&\s+requirements)[:\s]+'
    ]
    
    for pat in qual_pats:
        matches = list(re.finditer(pat, desc))
        if not matches:
            matches = list(re.finditer(pat, desc, re.I))
        for m in matches:
            pos = m.end()
            check_ahead = desc[pos:pos+150].lower()
            # Strict rejection of logistics, hybrid policy, visa sponsorship, benefits, compensation
            if any(bad in check_ahead for bad in [
                'location-based', 'visa sponsorship', 'for roles performing',
                'compensation', 'annual salary', 'pay range', 'benefits',
                'equal opportunity', 'minimum education'
            ]):
                continue
            cand = extract_verbatim_slice(desc, pos, 260)
            if cand and len(cand) > 30 and norm_ws(cand) in desc_norm:
                # Double check no visa, hybrid policy, fair chance
                if not any(bad in cand.lower() for bad in ['visa', 'sponsorship', 'hybrid policy', 'in our offices at least', 'fair chance ordinance']):
                    qual_ev = cand
                    break
        if qual_ev:
            break
            
    # Guarantee strict verbatim check
    if resp_ev and norm_ws(resp_ev) not in desc_norm:
        resp_ev = None
    if qual_ev and norm_ws(qual_ev) not in desc_norm:
        qual_ev = None
        
    # Guarantee zero visa/hybrid in qual_ev
    if qual_ev and any(bad in qual_ev.lower() for bad in ['visa', 'sponsorship', 'hybrid policy', 'in our offices', 'fair chance']):
        qual_ev = None

    return resp_ev, qual_ev

# Test on all 1930 records!
mismatched_resp = 0
mismatched_qual = 0
visa_qual = 0
null_qual_count = 0
null_resp_count = 0

for r in records:
    desc = r['jobDescription']
    title = r['jobTitle']
    comp = r['companyName']
    resp, qual = get_evidence_v5(desc, title, comp)
    desc_norm = norm_ws(desc)
    
    if resp:
        if norm_ws(resp) not in desc_norm:
            mismatched_resp += 1
    else:
        null_resp_count += 1
        
    if qual:
        if norm_ws(qual) not in desc_norm:
            mismatched_qual += 1
        if any(w in qual.lower() for w in ['visa', 'sponsorship', 'work authorization']):
            visa_qual += 1
    else:
        null_qual_count += 1

print("--- RESULTS ON ALL 1930 RECORDS ---")
print(f"Mismatched resp: {mismatched_resp}")
print(f"Mismatched qual: {mismatched_qual}")
print(f"Visa boilerplate in qual: {visa_qual}")
print(f"Null qual count: {null_qual_count} / {len(records)}")
print(f"Null resp count: {null_resp_count} / {len(records)}")

# Test the specific roles called out by the user:
specific_targets = [
    '3P Revenue Accounting & Reporting',
    'AI Infrastructure Operations, Demand Planning',
    'Applied AI Architect, Beneficial Deployment',
    'Applied AI Architect, Beneficial Deployments (Global & Public Health)',
    'Anthropic Fellows Program, AI Safety'
]

print("\n--- SPECIFIC TARGET ROLES CHECK ---")
for r in records:
    for t in specific_targets:
        if t.lower() in r['jobTitle'].lower():
            resp, qual = get_evidence_v5(r['jobDescription'], r['jobTitle'], r['companyName'])
            print(f"\nRole: {r['jobTitle']}")
            print(f"  RESP ({len(resp) if resp else 0}): {repr(resp)}")
            print(f"  QUAL ({len(qual) if qual else 0}): {repr(qual)}")
            print(f"  RESP in desc?: {norm_ws(resp) in norm_ws(r['jobDescription']) if resp else 'N/A'}")
            print(f"  QUAL in desc?: {norm_ws(qual) in norm_ws(r['jobDescription']) if qual else 'N/A'}")
            break
