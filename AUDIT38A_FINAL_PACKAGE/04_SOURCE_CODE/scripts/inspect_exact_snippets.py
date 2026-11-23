import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f if line.strip()}

test_ids = [
    'job_4657d6865ca86588', # Together AI: Director of Brand
    'job_2f3ae38c86e79b73', # Together AI: Solutions Architect
    'job_3c77bfa1cfea1adb', # CoreWeave: Software Engineer, Inference
    'job_9b9c7d627f230577', # CoreWeave: Executive Assistant
    'job_90a3078b4542f9c4', # Databricks: Data Science Intern
    'job_b90714e7252b07a6', # Cresta: Software Engineer Intern
    'job_9bf8834899fc4d48', # Squid Support: AI Engineer / LLM Engineer
    'job_5bb0ce075f67a09a', # LINKIT B.V.: AI Machine Learning Engineer
]

for jid in test_ids:
    j = jobs[jid]
    print("=" * 80)
    print(f"{j['jobId']} | {j['companyName']} | {j['jobTitle']}")
    desc = j.get('jobDescription', '')
    # Find sentences with numbers or compensation words
    matches = re.findall(r'.{0,40}(?:salary|compensation|pay|rate|stipend|\$|€|cad|eur|usd|ote|\bper\b).{0,60}', desc, re.I)
    for m in matches[:10]:
        print(f"  Snippet: {m.strip()}")
