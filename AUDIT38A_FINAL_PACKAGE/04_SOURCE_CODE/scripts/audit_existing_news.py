import json
import pandas as pd

with open("data/canonical/canonical_news.jsonl", "r", encoding="utf-8") as f:
    news = [json.loads(line) for line in f]

print(f"Total news records: {len(news)}")

source_counts = {}
gen_summary_count = 0
real_summary_count = 0

for n in news:
    d = n["content"]["data"]
    src = d.get("sourceName")
    source_counts[src] = source_counts.get(src, 0) + 1
    
    summary = d.get("summary", "")
    if summary.startswith("Official research announcement from") or summary.startswith("News report from"):
        gen_summary_count += 1
    else:
        real_summary_count += 1

print("\nSource distribution:")
for s, c in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {s:30}: {c}")

print(f"\nGenerated synthetic summaries: {gen_summary_count}")
print(f"Genuine publisher summaries:   {real_summary_count}")
