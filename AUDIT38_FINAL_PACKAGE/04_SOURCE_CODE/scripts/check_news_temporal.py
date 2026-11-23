import json
from collections import Counter

with open("data/canonical/canonical_news.jsonl", "r", encoding="utf-8") as f:
    news = [json.loads(line) for line in f]

years = Counter()
hf_years = Counter()
other_years = Counter()

for n in news:
    d = n["content"]["data"]
    pub = d.get("publishedAt", "")
    yr = pub[:4] if len(pub) >= 4 else "Unknown"
    src = d.get("sourceName", "")
    years[yr] += 1
    if src == "Hugging Face Blog":
        hf_years[yr] += 1
    else:
        other_years[yr] += 1

print("Overall publication year breakdown:")
for y in sorted(years.keys()):
    print(f"  {y}: {years[y]:,} articles ({years[y]/len(news)*100:.1f}%)")

print("\nHugging Face Blog publication years:")
for y in sorted(hf_years.keys()):
    print(f"  {y}: {hf_years[y]:,}")

print("\nOther sources publication years:")
for y in sorted(other_years.keys()):
    print(f"  {y}: {other_years[y]:,}")
