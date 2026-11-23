import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

target_ids = [
    'job_49ea2bf597ea9b3b',
    'job_b678befa49d8eca6',
    'job_ef2b2e6a4d0da47e',
    'job_1e8b2d8ee5e34329',
    'job_b9afa5fa330d4cfe',
    'job_9e3c061de5f3230d',
    'job_5239de691155afc1',
    'job_3eb7f06aac9c95df',
    'job_f3386228b7398977',
    'job_7bfbdf8b1ac820ea',
    'job_f8809da8ade216a4',
    'job_547a71edc830f006',
    'job_22ce0dd8878d0646',
    'job_498f8f352202b404',
    'job_932f15923af0d3cc',
    'job_17d97fbfc48871d9',
    'job_643aad676fad2d07'
]

for jid in target_ids:
    j = jobs[jid]
    print(f"=== {jid}: {j['jobTitle']} ===")
    print("Reason:", j.get('classificationReason'))
    desc = j['jobDescription']
    # Find position of Responsibilities
    idx = -1
    for kw in ['responsibilities', 'responsibility', 'you will', 'what you\'ll do']:
        m = re.search(r'\b' + kw + r'\b', desc, re.I)
        if m:
            idx = m.start()
            break
    if idx != -1:
        snippet = desc[idx:idx+700]
        print("Section excerpt:")
        print(snippet)
    else:
        print("No responsibilities section found! First 500 chars:")
        print(desc[:500])
    print("-" * 60)
