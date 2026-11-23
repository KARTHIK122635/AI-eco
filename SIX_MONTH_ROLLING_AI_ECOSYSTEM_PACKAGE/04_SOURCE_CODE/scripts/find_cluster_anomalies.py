import json
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

counts = Counter(r['classificationReason'] for r in records)

# For each cluster >= 10, list anomalies
anomalies = []

for reason, count in counts.most_common():
    if count < 10:
        continue
    matching = [r for r in records if r['classificationReason'] == reason]
    r_lower = reason.lower()
    
    # Check for mismatches
    for r in matching:
        t_lower = r['jobTitle'].lower()
        cat = r['category']
        
        # 80: Designs, trains, and optimizes machine learning and deep learning models for core algorithmic AI systems.
        if 'deep learning models for core algorithmic' in r_lower:
            if not any(k in t_lower for k in ['ml', 'machine learning', 'deep learning', 'algorithm', 'model', 'llm', 'nlp', 'computer vision', 'robotics', 'ia', 'ai', 'research']):
                anomalies.append((reason, r))
            elif 'account manager' in t_lower or 'sales' in t_lower or 'recruiter' in t_lower:
                anomalies.append((reason, r))
                
        # 62: Works with enterprise customers to design and deploy AI solutions and guide technical adoption.
        elif 'works with enterprise customers to design and deploy ai solutions' in r_lower:
            if not any(k in t_lower for k in ['architect', 'solutions', 'customer', 'deployment', 'field']):
                anomalies.append((reason, r))
                
        # 52: Develops marketing campaigns, brand messaging, content initiatives, and corporate communications.
        elif 'develops marketing campaigns' in r_lower:
            if not any(k in t_lower for k in ['market', 'brand', 'content', 'comm', 'pr', 'creative', 'inbound', 'growth', 'event', 'social']):
                anomalies.append((reason, r))
                
        # 50: Defines product strategy, technical roadmaps, and feature specifications for customer-facing AI applications.
        elif 'defines product strategy, technical roadmaps' in r_lower:
            if not any(k in t_lower for k in ['product', 'pm']):
                anomalies.append((reason, r))
                
        # 48: Develops predictive machine learning models, statistical analyses, and data algorithms for product decisions.
        elif 'predictive machine learning models, statistical analyses' in r_lower:
            if not any(k in t_lower for k in ['data scientist', 'data science', 'scientist', 'statistician']):
                anomalies.append((reason, r))
                
        # 45: Develops, fine-tunes, and evaluates domain-specific AI models and applications for specialized use cases.
        elif 'fine-tunes, and evaluates domain-specific ai models' in r_lower:
            if not any(k in t_lower for k in ['ai engineer', 'applied ai', 'engineer', 'developer', 'consultant']):
                anomalies.append((reason, r))

print(f"Total anomalies flagged in top repeated clusters: {len(anomalies)}")
for reason, r in anomalies:
    print(f"Cluster: {reason[:50]}...")
    print(f"  ID: {r['jobId']} | Cat: {r['category']} | Title: {r['jobTitle']}")
