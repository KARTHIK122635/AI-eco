import json
import pandas as pd

df_r = pd.read_csv("data/canonical/canonical_research_papers.csv")
with open("data/canonical/canonical_research_papers.jsonl", "r", encoding="utf-8") as f:
    papers = [json.loads(line) for line in f]

hf_with_stars = 0
arxiv_with_stars = 0
hf_null_stars = 0
arxiv_null_stars = 0

for p in papers:
    d = p["content"]["data"]
    gh = d.get("githubUrl")
    stars = d.get("githubStars")
    prov = p["source"]["name"]
    if gh:
        if "Hugging Face" in prov:
            if stars is not None:
                hf_with_stars += 1
            else:
                hf_null_stars += 1
        else:
            if stars is not None:
                arxiv_with_stars += 1
            else:
                arxiv_null_stars += 1

print(f"HF Daily Papers with GitHub repo: {hf_with_stars + hf_null_stars}")
print(f"  - stars populated: {hf_with_stars}")
print(f"  - stars null: {hf_null_stars}")
print(f"arXiv API with GitHub repo: {arxiv_with_stars + arxiv_null_stars}")
print(f"  - stars populated: {arxiv_with_stars}")
print(f"  - stars null: {arxiv_null_stars}")
