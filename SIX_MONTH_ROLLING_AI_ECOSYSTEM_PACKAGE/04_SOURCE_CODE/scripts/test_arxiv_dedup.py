import json
import re

def extract_canonical_arxiv_id(url_or_id: str) -> str:
    """Extracts canonical arXiv ID without version suffix."""
    match = re.search(r'(\d{4}\.\d{4,5})(v\d+)?', url_or_id)
    if match:
        return match.group(1)
    match2 = re.search(r'([a-zA-Z\-]+/\d{7})(v\d+)?', url_or_id)
    if match2:
        return match2.group(1)
    return url_or_id

with open("data/canonical/canonical_research_papers.jsonl", "r", encoding="utf-8") as f:
    papers = [json.loads(line) for line in f]

canonical_map = {}
for p in papers:
    d = p["content"]["data"]
    paper_url = d.get("paperUrl") or p["source"]["url"]
    canon_id = extract_canonical_arxiv_id(paper_url)
    if canon_id not in canonical_map:
        canonical_map[canon_id] = []
    canonical_map[canon_id].append(p)

print(f"Total paper records: {len(papers)}")
print(f"Distinct canonical arXiv IDs: {len(canonical_map)}")
multi_records = {k: v for k, v in canonical_map.items() if len(v) > 1}
print(f"Canonical IDs with multiple records: {len(multi_records)}")
for k, v in list(multi_records.items())[:5]:
    print(f"\nCanonical arXiv ID: {k} (Records: {len(v)})")
    for r in v:
        d = r["content"]["data"]
        print("  - ID:", d.get("paperId"), "| Prov:", r["source"]["name"], "| URL:", d.get("paperUrl") or r["source"]["url"])
        print("    GitHub:", d.get("githubUrl"), "| Stars:", d.get("githubStars"))
