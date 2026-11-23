import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

def clean_sentence_splits(text):
    # Split text into candidate sentences while preserving original text verbatim
    # Typical sentence boundaries in clean text: '. ', '! ', '? '
    parts = re.split(r'(?<=[.!?])\s+', text)
    sentences = []
    for p in parts:
        p = p.strip()
        if len(p) >= 20:
            sentences.append(p)
    return sentences

# Test on job_e98b00bb44e6a41d
j0 = [j for j in jobs if j['jobId'] == 'job_e98b00bb44e6a41d'][0]
desc = j0['jobDescription']
reason = j0['classificationReason']

print("Reason:", reason)
sents = clean_sentence_splits(desc)
print(f"Total sentences: {len(sents)}")
for i, s in enumerate(sents[:10]):
    print(f"[{i}] {s}")
