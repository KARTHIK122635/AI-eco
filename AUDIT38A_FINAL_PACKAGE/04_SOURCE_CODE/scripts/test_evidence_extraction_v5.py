import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

def norm_ws(s):
    if not s: return ""
    return re.sub(r'\s+', ' ', s.replace('\u00a0', ' ').replace('\u202f', ' ')).strip()

def extract_verbatim_evidence(desc: str, title: str, company: str):
    """
    Extracts contiguous, verbatim substrings from desc for responsibility and qualification evidence.
    Returns: (resp_evidence, qual_evidence, resp_section_name, qual_section_name)
    """
    if not desc:
        return None, None, None, None

    # Section header patterns for responsibilities
    resp_headers = [
        r'(?:key\s+responsibilities|core\s+responsibilities|primary\s+responsibilities|responsibilities|what\s+you(?:’|\')ll\s+do|what\s+you\s+will\s+do|what\s+you(?:\'|’)?ll\s+be\s+doing|your\s+role|about\s+the\s+role|the\s+role|tasks|missions|you\s+will)',
    ]
    
    # Section header patterns for qualifications
    qual_headers = [
        r'(?:minimum\s+qualifications|basic\s+qualifications|required\s+qualifications|qualifications|requirements|what\s+you\s+bring|what\s+you(?:’|\')ll\s+need|what\s+you\s+need|what\s+we(?:’|\')re\s+looking\s+for|what\s+we\s+look\s+for|who\s+we(?:’|\')re\s+looking\s+for|who\s+you\s+are|you\s+may\s+be\s+a\s+good\s+fit\s+if\s+you\s+have|you\s+might\s+be\s+a\s+good\s+fit\s+if\s+you\s+have|you\s+may\s+be\s+a\s+good\s+fit\s+if\s+you|you\s+might\s+be\s+a\s+good\s+fit\s+if\s+you|you\s+may\s+be\s+a\s+good\s+fit|you\s+might\s+be\s+a\s+good\s+fit|profile|candidate\s+profile|skills\s+&\s+requirements)',
    ]
    
    # Boundary markers where a section ends
    boundary_headers = [
        r'(?:preferred\s+qualifications|nice\s+to\s+have|bonus\s+if|what\s+we\s+offer|benefits|perks|compensation|annual\s+salary|salary\s+range|pay\s+range|logistics|location-based|visa\s+sponsorship|for\s+roles\s+performing|how\s+to\s+apply|about\s+us|about\s+anthropic|about\s+databricks|about\s+coreweave|about\s+the\s+company|equal\s+opportunity|compliance|guidance\s+on\s+candidates|$)'
    ]
    
    # 1. Responsibilities extraction
    resp_ev = None
    resp_sec = None
    
    # Special handling for Anthropic Fellows Program
    if "fellows program" in title.lower():
        # Look for "What to expect" or overview
        m_exp = re.search(r'What to expect\s+(.*?)(?:The annual compensation|Logistics|Compensation|$)', desc, re.I)
        if m_exp:
            # take first 200 chars verbatim
            raw = m_exp.group(1).strip()
            # find first period or end of first sentence
            idx_p = raw.find('.')
            if idx_p != -1 and idx_p > 30:
                resp_ev = raw[:idx_p+1]
            else:
                resp_ev = raw[:250].rsplit(' ', 1)[0] + '.'
            resp_sec = "What to expect"
        else:
            # Look for overview
            m_ov = re.search(r'Anthropic Fellows Program overview\s+(.*?)(?:The annual compensation|Logistics|$)', desc, re.I)
            if m_ov:
                raw = m_ov.group(1).strip()
                idx_p = raw.find('.')
                if idx_p != -1 and idx_p > 30:
                    resp_ev = raw[:idx_p+1]
                else:
                    resp_ev = raw[:250].rsplit(' ', 1)[0] + '.'
                resp_sec = "Anthropic Fellows Program overview"

    if not resp_ev:
        # Search for responsibility header
        # We want to match headers that are actual section breaks, not inside a sentence
        # E.g. preceded by whitespace or start of line
        for pat in [
            r'(?:Key\s+responsibilities|Core\s+responsibilities|Responsibilities|What\s+you(?:’|\')ll\s+do|What\s+you\s+will\s+do|Your\s+role|Tasks|Missions)[:\s]+',
            r'(?:About\s+the\s+role)[:\s]+'
        ]:
            matches = list(re.finditer(pat, desc, re.I))
            if matches:
                # pick the best match
                for m in matches:
                    start_idx = m.end()
                    # take a slice of 500 chars from start_idx
                    chunk = desc[start_idx:start_idx+600]
                    # ignore if starts with another header or boilerplate
                    if any(chunk.strip().lower().startswith(b) for b in ['minimum education', 'visa', 'location']):
                        continue
                    # take first 1 or 2 clean sentences from this exact slice
                    # find period after at least 40 chars
                    m_period = re.search(r'(\.\s+[A-Z]|\.\s*\n)', chunk[40:])
                    if m_period:
                        end_pos = 40 + m_period.start() + 1
                        # check if we can get a second sentence up to 250 chars
                        m_period2 = re.search(r'(\.\s+[A-Z]|\.\s*\n)', chunk[end_pos+30:300])
                        if m_period2:
                            end_pos = end_pos + 30 + m_period2.start() + 1
                        candidate = chunk[:end_pos].strip()
                    else:
                        candidate = chunk[:250].rsplit(' ', 1)[0].strip()
                        if not candidate.endswith('.'):
                            candidate += '.'
                    
                    # Ensure candidate is actually in desc verbatim
                    if norm_ws(candidate) in norm_ws(desc):
                        resp_ev = candidate
                        resp_sec = m.group(0).strip(' :')
                        break
            if resp_ev:
                break

    # If still no resp_ev, take the first substantial paragraph of the description that is not company boilerplate
    if not resp_ev:
        # split by double newline or sentences
        parts = [p.strip() for p in desc.split('\n\n') if len(p.strip()) > 50]
        for p in parts:
            if not any(bp in p.lower() for bp in ['about anthropic', 'about us', 'about databricks', 'company description', 'equal opportunity']):
                # take first sentence
                idx_p = p.find('.')
                if idx_p > 30:
                    cand = p[:idx_p+1].strip()
                else:
                    cand = p[:250].rsplit(' ', 1)[0].strip() + '.'
                if norm_ws(cand) in norm_ws(desc):
                    resp_ev = cand
                    resp_sec = "Job Description Overview"
                    break

    # 2. Qualifications extraction
    qual_ev = None
    qual_sec = None
    
    qual_header_patterns = [
        r'(?:Minimum\s+qualifications|Basic\s+qualifications|Required\s+qualifications|Qualifications|Requirements|What\s+you\s+bring|What\s+you(?:’|\')ll\s+need|What\s+you\s+need|What\s+we(?:’|\')re\s+looking\s+for|Who\s+we(?:’|\')re\s+looking\s+for|You\s+may\s+be\s+a\s+good\s+fit\s+if\s+you\s+have|You\s+might\s+be\s+a\s+good\s+fit\s+if\s+you\s+have|You\s+may\s+be\s+a\s+good\s+fit\s+if\s+you|You\s+might\s+be\s+a\s+good\s+fit\s+if\s+you|You\s+may\s+be\s+a\s+good\s+fit|You\s+might\s+be\s+a\s+good\s+fit|Candidate\s+profile|Skills\s+&\s+requirements)[:\s]+'
    ]
    
    for pat in qual_header_patterns:
        matches = list(re.finditer(pat, desc, re.I))
        if matches:
            for m in matches:
                start_idx = m.end()
                chunk = desc[start_idx:start_idx+600]
                # exclude if immediately hits logistics or visa or hybrid
                if any(chunk.strip().lower().startswith(b) for b in ['location-based', 'visa sponsorship', 'for roles performing', 'compensation', 'annual salary']):
                    continue
                # take first 1 or 2 clean sentences from this exact slice
                m_period = re.search(r'(\.\s+[A-Z]|\.\s*\n)', chunk[40:])
                if m_period:
                    end_pos = 40 + m_period.start() + 1
                    m_period2 = re.search(r'(\.\s+[A-Z]|\.\s*\n)', chunk[end_pos+30:300])
                    if m_period2:
                        end_pos = end_pos + 30 + m_period2.start() + 1
                    candidate = chunk[:end_pos].strip()
                else:
                    candidate = chunk[:250].rsplit(' ', 1)[0].strip()
                    if not candidate.endswith('.'):
                        candidate += '.'
                
                # Check for visa, hybrid, fair chance, logistics
                if any(bad in candidate.lower() for bad in ['visa sponsorship', 'sponsor visas', 'hybrid policy', 'in our offices at least', 'fair chance ordinance']):
                    continue
                
                # Check verbatim in desc
                if norm_ws(candidate) in norm_ws(desc):
                    qual_ev = candidate
                    qual_sec = m.group(0).strip(' :')
                    break
        if qual_ev:
            break

    # Truncate clean verbatim without breaking words
    if resp_ev and len(resp_ev) > 280:
        # find last period or space before 280
        cut = resp_ev[:280].rfind('. ')
        if cut != -1 and cut > 80:
            resp_ev = resp_ev[:cut+1].strip()
        else:
            cut_sp = resp_ev[:280].rfind(' ')
            if cut_sp != -1:
                resp_ev = resp_ev[:cut_sp].strip() + '.'

    if qual_ev and len(qual_ev) > 280:
        cut = qual_ev[:280].rfind('. ')
        if cut != -1 and cut > 80:
            qual_ev = qual_ev[:cut+1].strip()
        else:
            cut_sp = qual_ev[:280].rfind(' ')
            if cut_sp != -1:
                qual_ev = qual_ev[:cut_sp].strip() + '.'

    # Final check: NEVER let visa, hybrid, fair chance into qual_ev
    if qual_ev and any(bad in qual_ev.lower() for bad in ['visa', 'sponsorship', 'hybrid policy', 'in our offices', 'fair chance']):
        qual_ev = None
        qual_sec = None

    return resp_ev, qual_ev, resp_sec, qual_sec

# Let's test on all 1930 records!
mismatched_resp = 0
mismatched_qual = 0
visa_qual = 0
null_qual_count = 0
null_resp_count = 0

for r in records:
    desc = r['jobDescription']
    title = r['jobTitle']
    comp = r['companyName']
    resp, qual, r_sec, q_sec = extract_verbatim_evidence(desc, title, comp)
    
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

print(f"Test on {len(records)} records:")
print(f"Mismatched resp: {mismatched_resp}")
print(f"Mismatched qual: {mismatched_qual}")
print(f"Visa boilerplate in qual: {visa_qual}")
print(f"Null qual count: {null_qual_count} / {len(records)}")
print(f"Null resp count: {null_resp_count} / {len(records)}")
