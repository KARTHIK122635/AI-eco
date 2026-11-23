import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

target = "You'll combine your deep technical expertise with customer-facing skills to architect innovative LLM solutions that address complex business challenges while maintaining our high standards for safety and reliability."

count = 0
for j in jobs:
    if target in j['jobDescription']:
        count += 1
print('Matches count:', count)
