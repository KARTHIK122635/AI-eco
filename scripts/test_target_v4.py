import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

from test_clean_evidence import extract_evidence_v4

target_roles = [
    "AI Outcomes Manager, Financial Services",
    "Data Center Asset Management, Commercial Associate",
    "Anthropic Fellows Program, The Anthropic Institute (Economics & Policy)"
]

for title in target_roles:
    matching = [j for j in jobs if title.lower() in j['jobTitle'].lower()]
    for j in matching:
        r_ev, q_ev = extract_evidence_v4(j.get('jobDescription', ''), j['jobTitle'])
        print("=" * 80)
        print(f"Title: {j['jobTitle']} ({j['companyName']})")
        print(f"Resp Ev: {r_ev}")
        print(f"Qual Ev: {q_ev}")
