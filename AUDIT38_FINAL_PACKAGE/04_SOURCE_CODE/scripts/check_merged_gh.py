import json

# Check the pre-merged papers
with open("data/canonical/canonical_research_papers.jsonl", "r", encoding="utf-8") as f:
    papers = [json.loads(line) for line in f]

for p in papers:
    d = p["content"]["data"]
    if d.get("githubUrl") and d.get("githubStars") is None:
        pass
