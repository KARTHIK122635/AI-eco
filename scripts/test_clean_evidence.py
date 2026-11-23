import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

def clean_extracted_text(text: str) -> str:
    if not text:
        return ""
    # Strip common boilerplate blocks
    text = re.sub(r'Location-based hybrid policy:.*?(?=\.|$)', '', text, flags=re.I)
    text = re.sub(r'Visa sponsorship:.*?(?=\.|$)', '', text, flags=re.I)
    text = re.sub(r'For roles performing work in California:.*?(?=\.|$)', '', text, flags=re.I)
    text = re.sub(r'We encourage you to apply even if.*?(?=\.|$)', '', text, flags=re.I)
    text = re.sub(r'Your safety matters to us.*?(?=\.|$)', '', text, flags=re.I)
    text = re.sub(r'How we’re different.*?(?=\.|$)', '', text, flags=re.I)
    text = re.sub(r'About (?:Anthropic|CoreWeave|Databricks|Scale|Together|Cresta).*?(?:beneficial AI systems\.|\.|$)', '', text, flags=re.I)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_evidence_v4(desc: str, title: str):
    if not desc:
        return None, None

    # 1. Responsibilities extraction
    resp_patterns = [
        r'(?:key\s+responsibilities|responsibilities|what\s+you(?:’|\')ll\s+do|what\s+you\s+will\s+do|the\s+role|about\s+the\s+role|your\s+role|tasks|missions|you\s+will)[:\s]+(.*?)(?:qualifications|requirements|you\s+may\s+be\s+a\s+good\s+fit|what\s+you\s+bring|what\s+we(?:’|\')re\s+looking\s+for|what\s+to\s+expect|logistics|$)',
        r'(?:about\s+the\s+role)[:\s]+(.*?)(?:key\s+responsibilities|responsibilities|qualifications|requirements|$)'
    ]
    
    resp_evidence = None
    for pat in resp_patterns:
        m = re.search(pat, desc, re.I | re.S)
        if m:
            raw_resp = clean_extracted_text(m.group(1))
            sentences = [s.strip() for s in re.split(r'[\.\n;]', raw_resp) if len(s.strip()) > 20]
            if sentences:
                resp_evidence = ". ".join(sentences[:2]).strip()
                if not resp_evidence.endswith('.'):
                    resp_evidence += '.'
                break
    
    if not resp_evidence:
        # Fallback to first non-boilerplate sentences of desc
        clean_desc = clean_extracted_text(desc)
        sentences = [s.strip() for s in re.split(r'[\.\n;]', clean_desc) if len(s.strip()) > 25]
        if sentences:
            resp_evidence = ". ".join(sentences[:2]).strip()
            if not resp_evidence.endswith('.'):
                resp_evidence += '.'

    # 2. Qualifications extraction
    qual_patterns = [
        r'(?:you\s+may\s+be\s+a\s+good\s+fit\s+if|minimum\s+qualifications|basic\s+qualifications|required\s+qualifications|qualifications|requirements|what\s+you\s+bring|what\s+you(?:’|\')ll\s+need|what\s+we(?:’|\')re\s+looking\s+for|we\s+are\s+looking\s+for|profile|skills\s+&\s+requirements)[:\s]+(.*?)(?:preferred\s+qualifications|nice\s+to\s+have|benefits|what\s+we\s+offer|what\s+to\s+expect|logistics|how\s+to\s+apply|about\s+us|$)',
        r'(?:minimum\s+education)[:\s]+(.*?)(?:location-based|visa|for\s+roles|how\s+we|$)'
    ]
    
    qual_evidence = None
    for pat in qual_patterns:
        m = re.search(pat, desc, re.I | re.S)
        if m:
            raw_qual = clean_extracted_text(m.group(1))
            # Filter out lines that are purely location or hybrid
            sentences = [
                s.strip() for s in re.split(r'[\.\n;]', raw_qual)
                if len(s.strip()) > 20
                and not any(hw in s.lower() for hw in ['hybrid policy', 'in one of our offices', '25% of the time', 'visa sponsorship', 'fair chance'])
            ]
            if sentences:
                qual_evidence = ". ".join(sentences[:2]).strip()
                if not qual_evidence.endswith('.'):
                    qual_evidence += '.'
                break

    # If qualification evidence is empty or contains hybrid/location statements, set to None
    if qual_evidence:
        if any(hw in qual_evidence.lower() for hw in ['hybrid policy', 'in one of our offices', '25% of the time', 'visa sponsorship']):
            qual_evidence = None

    return (resp_evidence[:280] if resp_evidence else None), (qual_evidence[:280] if qual_evidence else None)

# Run on all jobs
null_quals = 0
hybrid_quals = 0
placeholder_quals = 0

for j in jobs:
    r_ev, q_ev = extract_evidence_v4(j.get('jobDescription', ''), j['jobTitle'])
    if q_ev is None:
        null_quals += 1
    else:
        if "Role requirements embedded" in q_ev:
            placeholder_quals += 1
        if any(hw in q_ev.lower() for hw in ['hybrid policy', 'in one of our offices', '25% of the time']):
            hybrid_quals += 1

print(f"Total jobs: {len(jobs)}")
print(f"Null qualifications (truthful absent): {null_quals}")
print(f"Placeholder qualifications remaining: {placeholder_quals}")
print(f"Hybrid/location qualifications remaining: {hybrid_quals}")
