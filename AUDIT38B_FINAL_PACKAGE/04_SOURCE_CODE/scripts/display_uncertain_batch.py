import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

uncertain_jobs = [j for j in jobs if j['category'] == 'UNCERTAIN']

def display_batch(start, count):
    for i in range(start, min(start + count, len(uncertain_jobs))):
        j = uncertain_jobs[i]
        print("="*80)
        print(f"[{i+1}/{len(uncertain_jobs)}] ID: {j['jobId']}")
        print(f"Company: {j['companyName']} | Title: {j['jobTitle']}")
        print(f"Resp Evidence: {j.get('responsibilityEvidence')}")
        print(f"Qual Evidence: {j.get('qualificationEvidence')}")
        desc = (j.get('jobDescription') or '').strip()
        print(f"Description (first 500 chars):\n{desc[:500]}")
        print("="*80)

if __name__ == '__main__':
    import sys
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    display_batch(start, count)
