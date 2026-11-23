import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

def extract_evidence(desc: str, title: str):
    if not desc:
        return "No description text available", "No qualifications text available"
    
    # Extract responsibilities snippet
    resp_match = re.search(r'(?:responsibilities|about the role|what you(?:’|\')ll do|tasks|key responsibilities)[:\s]+(.*?)(?:qualifications|requirements|what you bring|about you|$)', desc, re.I | re.S)
    if resp_match:
        resp_text = resp_match.group(1).strip()
        # Take first 1-2 clean sentences
        sentences = [s.strip() for s in re.split(r'[\.\n]', resp_text) if len(s.strip()) > 20]
        resp_evidence = ". ".join(sentences[:2]) if sentences else resp_text[:200]
    else:
        # Fallback to first substantive sentences
        sentences = [s.strip() for s in re.split(r'[\.\n]', desc) if len(s.strip()) > 30]
        resp_evidence = ". ".join(sentences[:2]) if sentences else desc[:200]
        
    # Extract qualifications snippet
    qual_match = re.search(r'(?:qualifications|requirements|what you bring|minimum qualifications|basic qualifications)[:\s]+(.*?)(?:preferred|benefits|what to expect|how to apply|about us|$)', desc, re.I | re.S)
    if qual_match:
        qual_text = qual_match.group(1).strip()
        sentences = [s.strip() for s in re.split(r'[\.\n]', qual_text) if len(s.strip()) > 20]
        qual_evidence = ". ".join(sentences[:2]) if sentences else qual_text[:200]
    else:
        qual_evidence = "Role requirements embedded in main text"
        
    return resp_evidence[:280].strip(), qual_evidence[:280].strip()

# Test on 5 diverse jobs
for j in jobs[:6]:
    r_ev, q_ev = extract_evidence(j.get('jobDescription', ''), j['jobTitle'])
    print(f"\nTitle: {j['jobTitle']} ({j['companyName']})")
    print(f"  Resp Ev: {r_ev}")
    print(f"  Qual Ev: {q_ev}")
