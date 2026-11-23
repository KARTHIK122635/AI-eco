import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

uncertain_jobs = [j for j in jobs if j['category'] == 'UNCERTAIN']

# Let's inspect each job and build a clear proposal
for i, j in enumerate(uncertain_jobs):
    jid = j['jobId']
    comp = j['companyName']
    title = j['jobTitle']
    resp = j.get('responsibilityEvidence') or ''
    qual = j.get('qualificationEvidence') or ''
    desc = j.get('jobDescription') or ''
    print(f"--- RECORD {i+1}: {jid} | {comp} | {title} ---")
    print(f"RESP EVIDENCE: {resp[:200]}")
    if qual:
        print(f"QUAL EVIDENCE: {qual[:200]}")
    # print relevant snippet of desc
    print(f"DESC SNIPPET: {desc[:300].replace(chr(10), ' ')}")
    print()
