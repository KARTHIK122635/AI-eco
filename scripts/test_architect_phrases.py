import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

arch_jobs = [j for j in jobs if 'applied ai architect' in j['jobTitle'].lower()]
print(f"Total Applied AI Architect jobs: {len(arch_jobs)}")

phrase1 = "You'll combine your deep technical expertise with customer-facing skills to architect innovative LLM solutions that address complex business challenges while maintaining our high standards for safety and reliability."
phrase2 = "Working closely with our Sales, Product, and Engineering teams, you'll guide customers from initial technical discovery through successful deployment."

for j in arch_jobs:
    desc = j['jobDescription']
    has_p1 = phrase1 in desc
    has_p2 = phrase2 in desc
    print(f"{j['jobId']} | {j['jobTitle']} | p1: {has_p1} | p2: {has_p2}")
