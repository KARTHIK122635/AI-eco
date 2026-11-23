import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

def extract_section(desc):
    # Find start
    m_start = re.search(r'\b(?:Key responsibilities|Responsibilities|What you\'ll do|Role Responsibilities)\b', desc, re.I)
    if not m_start:
        return None
    start_pos = m_start.end()
    # Find end
    m_end = re.search(r'\b(?:You may be a good fit if you|Qualifications|Minimum qualifications|Requirements|Preferred qualifications|Who you are|What we\'re looking for|Logistics|About the team)\b', desc[start_pos:], re.I)
    if m_end:
        end_pos = start_pos + m_end.start()
        return desc[start_pos:end_pos].strip()
    return desc[start_pos:start_pos+1500].strip()

anthropic_jobs = [j for j in jobs if j['companyName'].lower() == 'anthropic']
found = 0
for j in anthropic_jobs[:10]:
    sec = extract_section(j['jobDescription'])
    if sec:
        found += 1
        print(f"=== {j['jobTitle']} ===")
        print(sec[:300])
        print("...")
print(f"Extracted responsibilities section for {found}/10 sample Anthropic jobs")
