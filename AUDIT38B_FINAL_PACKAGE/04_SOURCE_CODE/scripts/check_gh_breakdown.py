import json

with open("data/canonical/canonical_research_papers.jsonl", "r", encoding="utf-8") as f:
    papers = [json.loads(line) for line in f]

gh_papers = [p for p in papers if p["content"]["data"].get("githubUrl")]
print(f"Total papers with GitHub URL: {len(gh_papers)}")
hf_stars = [p for p in gh_papers if "Hugging Face" in p["source"]["name"] and p["content"]["data"].get("githubStars") is not None]
arxiv_stars = [p for p in gh_papers if "Hugging Face" not in p["source"]["name"] and p["content"]["data"].get("githubStars") is not None]
arxiv_null = [p for p in gh_papers if "Hugging Face" not in p["source"]["name"] and p["content"]["data"].get("githubStars") is None]

print(f"Hugging Face Daily Papers with stars: {len(hf_stars)}")
print(f"arXiv API with GitHub stars retrieved: {len(arxiv_stars)}")
print(f"arXiv API with GitHub repo but null stars: {len(arxiv_null)}")
