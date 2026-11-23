import json
import re

with open('data/startups_and_products.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line) for line in f]

print(f"Total records to inspect: {len(records)}")

ai_keywords = [
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "neural", "llm", "language model", "nlp", "computer vision",
    "speech-to-speech", "text-to-speech", "voice", "generative", "agent",
    "transformer", "diffusion", "outpainting", "lora", "safetensors",
    "gradio", "pytorch", "algorithm", "edge ai"
]

def check_ai_evidence(r):
    text = " ".join([
        r.get('company_name') or '',
        r.get('product_name') or '',
        r.get('description') or '',
        " ".join(r.get('categories') or [])
    ]).lower()
    
    matches = []
    for kw in ai_keywords:
        # Match whole word or exact pattern
        if re.search(r'\b' + re.escape(kw) + r'\b', text):
            matches.append(kw)
    return matches

ai_records = []
non_ai_records = []

for idx, r in enumerate(records):
    matches = check_ai_evidence(r)
    r['ai_matches'] = matches
    if matches:
        ai_records.append(r)
    else:
        non_ai_records.append(r)

print(f"AI-related records identified: {len(ai_records)}")
print(f"Non-AI records identified: {len(non_ai_records)}")

print("\n--- Non-AI Records Sample ---")
for r in non_ai_records:
    print(f"[{r['source_directory']}] Company: {r['company_name']} | Categories: {r['categories']} | Desc: {r['description'][:60]}")

print("\n--- AI Records Sample ---")
for r in ai_records[:10]:
    print(f"[{r['source_directory']}] Company: {r['company_name']} | Product: {r['product_name']} | Matches: {r['ai_matches']} | Desc: {r['description'][:60]}")
