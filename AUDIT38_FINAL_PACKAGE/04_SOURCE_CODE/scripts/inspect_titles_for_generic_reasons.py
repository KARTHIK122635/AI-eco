import json
from collections import defaultdict

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

# Group by classificationReason
reason_groups = defaultdict(list)
for r in records:
    reason_groups[r['classificationReason']].append(r)

generic_keys = [
    "Technical engineering position at CoreWeave",
    "Technical engineering position at Anthropic",
    "Corporate operational function at Anthropic",
    "Core software, platform, security, or data engineering supporting AI systems at Anthropic",
    "AI solutions architecture, forward-deployed customer engineering, developer advocacy, or technical AI product management at Databricks",
    "Corporate operational function at CoreWeave",
    "Core software, platform, security, or data engineering supporting AI systems at CoreWeave",
    "Core software, platform, security, or data engineering supporting AI systems at Databricks",
    "AI solutions architecture, forward-deployed customer engineering, developer advocacy, or technical AI product management at Anthropic",
    "Corporate operational function at Scale AI",
    "Technical engineering position at Scale AI",
    "Corporate financial planning, accounting, taxation, or fiscal administration at CoreWeave",
    "Commercial enterprise sales, client account management, revenue generation, or customer support operations at Anthropic",
    "Core software, platform, security, or data engineering supporting AI systems at Scale AI",
    "Corporate financial planning, accounting, taxation, or fiscal administration at Anthropic",
    "Technical engineering position at SambaNova Systems",
    "AI solutions architecture, forward-deployed customer engineering, developer advocacy, or technical AI product management at Scale AI",
    "Direct machine learning, deep learning, LLM model architecture, or AI scientific research at Databricks",
    "AI solutions architecture, forward-deployed customer engineering, developer advocacy, or technical AI product management at CoreWeave",
    "General software or infrastructure engineering without substantive AI specialization at Palantir Technologies",
    "Corporate operational function at Cresta",
    "Direct machine learning, deep learning, LLM model architecture, or AI scientific research at Scale AI",
    "Core software, platform, security, or data engineering supporting AI systems at Cresta",
    "Corporate operational function at SambaNova Systems",
    "High-performance compute clusters, GPU accelerators, CUDA/Triton kernels, or distributed AI hardware infrastructure engineering at CoreWeave",
    "Core software, platform, security, or data engineering supporting AI systems at SambaNova Systems",
    "Technical engineering position at Databricks",
    "Technical engineering position at Together AI",
    "Corporate operational function at Together AI",
    "Corporate operational function at Figure AI",
    "Talent acquisition, human resources, workplace facilities, executive administrative assistance, or people operations at CoreWeave",
    "Public policy analysis, economics research, regulatory affairs, or societal governance at Anthropic",
    "Core software, platform, security, or data engineering supporting AI systems at Together AI",
    "Corporate operational function at Databricks",
    "Technical engineering position at Cresta",
    "AI solutions architecture, forward-deployed customer engineering, developer advocacy, or technical AI product management at Cresta",
    "Corporate operational function at Snorkel AI",
    "High-performance compute clusters, GPU accelerators, CUDA/Triton kernels, or distributed AI hardware infrastructure engineering at Anthropic",
    "Legal counsel, governance, risk management, regulatory compliance (GRC), or internal audit at Anthropic",
    "External communications, public relations, community engagement, brand management, or corporate marketing at Anthropic"
]

total_generic = sum(len(reason_groups[k]) for k in generic_keys)
print(f"Total records covered by these generic reasons: {total_generic}")

# Print sample titles for top 5
for k in generic_keys[:5]:
    jobs = reason_groups[k]
    print(f"\n--- {k} ({len(jobs)} jobs) ---")
    for j in jobs[:8]:
        print(f"   [{j['category']}] {j['jobTitle']} | Resp: {j['responsibilityEvidence'][:60]}...")
