import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

uncertain_jobs = [j for j in jobs if j['category'] == 'UNCERTAIN']
print(f"Total uncertain jobs: {len(uncertain_jobs)}")

# We will create a precise mapping for each of the 117 records.
# Let's write out a skeleton and test it.
