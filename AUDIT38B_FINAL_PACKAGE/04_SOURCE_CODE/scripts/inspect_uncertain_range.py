import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

uncertain_jobs = [j for j in jobs if j['category'] == 'UNCERTAIN']

def show_range(start_idx, end_idx):
    for i in range(start_idx, end_idx):
        j = uncertain_jobs[i]
        print(f"--- [{i+1}] {j['jobId']} | {j['companyName']} | {j['jobTitle']} ---")
        print(f"Resp: {j.get('responsibilityEvidence')}")
        print(f"Qual: {j.get('qualificationEvidence')}")
        desc = j.get('jobDescription') or ''
        lines = [line.strip() for line in desc.split('\n') if line.strip()]
        print("Desc lines:")
        for line in lines[:8]:
            print(f"  * {line[:120]}")
        print()

if __name__ == '__main__':
    import sys
    s = int(sys.argv[1])
    e = int(sys.argv[2])
    show_range(s, e)
