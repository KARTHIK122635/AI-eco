import asyncio
import httpx
import re
import xml.etree.ElementTree as ET
import json
import csv
import sqlite3
import os
import sys
sys.path.insert(0, ".")
from datetime import datetime, timezone

from core.github_client import check_rate_limit, parse_github_owner_repo, fetch_github_stars

def extract_canonical_arxiv_id(url_or_id: str) -> str:
    """Extracts canonical arXiv ID without version suffix."""
    match = re.search(r'(\d{4}\.\d{4,5})(v\d+)?', url_or_id)
    if match:
        return match.group(1)
    match2 = re.search(r'([a-zA-Z\-]+/\d{7})(v\d+)?', url_or_id)
    if match2:
        return match2.group(1)
    return url_or_id

# 1. Load existing papers
with open("data/canonical/canonical_research_papers.jsonl", "r", encoding="utf-8") as f:
    existing_records = [json.loads(line) for line in f]

print(f"Loaded {len(existing_records)} existing paper records.")

# Group by core_arxiv_id
grouped = {}
for p in existing_records:
    d = p["content"]["data"]
    paper_url = d.get("paperUrl") or p["source"]["url"]
    core_id = extract_canonical_arxiv_id(paper_url)
    if core_id not in grouped:
        grouped[core_id] = []
    grouped[core_id].append(p)

print(f"Distinct core arXiv IDs: {len(grouped)}")

deduped_papers = []
merged_count = 0

for core_id, records in grouped.items():
    if len(records) == 1:
        rec = records[0]
        # Normalize ID and URL to canonical format
        d = rec["content"]["data"]
        d["paperId"] = f"arxiv_{core_id.replace('.', '_').replace('/', '_')}"
        d["paperUrl"] = f"https://arxiv.org/abs/{core_id}"
        rec["source"]["url"] = d["paperUrl"]
        deduped_papers.append(rec)
    else:
        # Merge the pair
        merged_count += 1
        # Sort so HF daily papers is prioritized for github info, arXiv for full metadata
        hf_rec = next((r for r in records if "Hugging Face" in r["source"]["name"]), None)
        arxiv_rec = next((r for r in records if "Hugging Face" not in r["source"]["name"]), None)
        
        base = hf_rec if hf_rec else records[0]
        supplement = arxiv_rec if arxiv_rec else records[1]
        
        b_data = base["content"]["data"]
        s_data = supplement["content"]["data"]
        
        # Merge authors
        authors = b_data.get("authors") or s_data.get("authors") or []
        if len(s_data.get("authors", [])) > len(b_data.get("authors", [])):
            authors = s_data["authors"]
            
        # Merge categories
        cats = list(set((b_data.get("categories") or []) + (s_data.get("categories") or [])))
        
        # Merge abstract
        abstract = b_data.get("abstract") or s_data.get("abstract") or ""
        if len(s_data.get("abstract", "")) > len(b_data.get("abstract", "")):
            abstract = s_data["abstract"]
            
        # Merge GitHub info
        gh_url = b_data.get("githubUrl") or s_data.get("githubUrl")
        gh_stars = b_data.get("githubStars") if b_data.get("githubStars") is not None else s_data.get("githubStars")
        gh_src = b_data.get("githubStarSource") or s_data.get("githubStarSource")
        gh_ts = b_data.get("githubStarRetrievedAt") or s_data.get("githubStarRetrievedAt")
        
        merged_rec = {
            "schemaVersion": "1.0",
            "recordType": "RESEARCH_PAPER",
            "source": {
                "name": "Hugging Face Daily Papers & arXiv API",
                "url": f"https://arxiv.org/abs/{core_id}"
            },
            "content": {
                "entityName": base["content"]["entityName"],
                "data": {
                    "paperId": f"arxiv_{core_id.replace('.', '_').replace('/', '_')}",
                    "authors": authors,
                    "publicationDate": b_data.get("publicationDate") or s_data.get("publicationDate"),
                    "categories": cats,
                    "paperUrl": f"https://arxiv.org/abs/{core_id}",
                    "abstract": abstract,
                    "githubUrl": gh_url,
                    "githubStars": gh_stars,
                    "githubStarSource": gh_src,
                    "githubStarRetrievedAt": gh_ts
                }
            },
            "collectedAt": base.get("collectedAt") or datetime.now(timezone.utc).isoformat()
        }
        deduped_papers.append(merged_rec)

print(f"Successfully merged {merged_count} duplicate groups.")
print(f"Total deduplicated unique papers: {len(deduped_papers)}")

# Build lookup sets
existing_core_ids = set(extract_canonical_arxiv_id(p["content"]["data"]["paperUrl"]) for p in deduped_papers)
existing_titles = set(p["content"]["entityName"].strip().lower() for p in deduped_papers)

print(f"Existing core IDs: {len(existing_core_ids)}, Existing titles: {len(existing_titles)}")

# 2. Asynchronously collect additional papers from arXiv API
async def fetch_additional_papers(target_total: int = 1060):
    papers_to_add = []
    query = "cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.CV+OR+cat:cs.RO+OR+cat:cs.NE"
    batch_size = 100
    start = 1200
    
    rate_info = check_rate_limit()
    print(f"GitHub API limit status: Remaining={rate_info['remaining']}")
    
    headers = {"User-Agent": "AcademicAIResearchHarvester/1.0 (academic-research@aisolution.internal)"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20.0) as client:
        while len(deduped_papers) + len(papers_to_add) < target_total:
            url = f"https://export.arxiv.org/api/query?search_query={query}&start={start}&max_results={batch_size}&sortBy=submittedDate&sortOrder=descending"
            print(f"Querying arXiv start={start}...")
            r = await client.get(url)
            if r.status_code != 200:
                print(f"arXiv query failed with status {r.status_code}")
                break
                
            root = ET.fromstring(r.text)
            ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
            entries = root.findall("atom:entry", ns)
            if not entries:
                print("No more entries returned.")
                break
                
            for entry in entries:
                id_elem = entry.find("atom:id", ns)
                raw_url = id_elem.text.strip().replace("http://", "https://") if id_elem is not None else ""
                core_id = extract_canonical_arxiv_id(raw_url)
                
                title_elem = entry.find("atom:title", ns)
                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else "Untitled"
                clean_title = re.sub(r'\s+', ' ', title).strip()
                
                if not core_id or core_id in existing_core_ids or clean_title.lower() in existing_titles:
                    continue
                    
                summary_elem = entry.find("atom:summary", ns)
                abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else ""
                clean_abstract = re.sub(r'\s+', ' ', abstract).strip()
                
                published_elem = entry.find("atom:published", ns)
                pub_date = published_elem.text.strip() if published_elem is not None else ""
                
                authors = []
                for a in entry.findall("atom:author", ns):
                    name_elem = a.find("atom:name", ns)
                    if name_elem is not None and name_elem.text:
                        authors.append(name_elem.text.strip())
                        
                categories = []
                for c in entry.findall("atom:category", ns):
                    term = c.attrib.get("term")
                    if term:
                        categories.append(term)
                        
                comment_elem = entry.find("arxiv:comment", ns)
                comment_text = comment_elem.text if comment_elem is not None else ""
                
                # Check for GitHub link
                combined_text = f"{comment_text} {clean_abstract}"
                gh_match = re.search(r'https?://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)', combined_text)
                github_url = None
                github_stars = None
                github_star_src = None
                github_star_ts = None
                
                if gh_match:
                    owner, repo = gh_match.group(1), gh_match.group(2).rstrip('.').rstrip(')').rstrip('/')
                    if owner.lower() not in ['sponsors', 'topics', 'features', 'site', 'about', 'blog']:
                        github_url = f"https://github.com/{owner}/{repo}"
                        if rate_info["remaining"] > 0:
                            s, src, ts = fetch_github_stars(owner, repo)
                            if s is not None:
                                github_stars = s
                                github_star_src = src
                                github_star_ts = ts
                                rate_info["remaining"] -= 1

                canonical_url = f"https://arxiv.org/abs/{core_id}"
                canonical_id = f"arxiv_{core_id.replace('.', '_').replace('/', '_')}"
                
                new_paper = {
                    "schemaVersion": "1.0",
                    "recordType": "RESEARCH_PAPER",
                    "source": {
                        "name": "arXiv API",
                        "url": canonical_url
                    },
                    "content": {
                        "entityName": clean_title,
                        "data": {
                            "paperId": canonical_id,
                            "authors": authors,
                            "publicationDate": pub_date,
                            "categories": categories,
                            "paperUrl": canonical_url,
                            "abstract": clean_abstract,
                            "githubUrl": github_url,
                            "githubStars": github_stars,
                            "githubStarSource": github_star_src,
                            "githubStarRetrievedAt": github_star_ts
                        }
                    },
                    "collectedAt": datetime.now(timezone.utc).isoformat()
                }
                
                papers_to_add.append(new_paper)
                existing_core_ids.add(core_id)
                existing_titles.add(clean_title.lower())
                
                if len(deduped_papers) + len(papers_to_add) >= target_total:
                    break
                    
            start += batch_size
            await asyncio.sleep(2.0)
            
    return papers_to_add

# Run additional collection
additional_papers = asyncio.run(fetch_additional_papers(target_total=1060))
print(f"Collected {len(additional_papers)} additional genuinely unique research papers.")

final_paper_records = deduped_papers + additional_papers
print(f"Final total research papers: {len(final_paper_records)}")

# Validate final uniqueness
final_ids = [p["content"]["data"]["paperId"] for p in final_paper_records]
final_urls = [p["content"]["data"]["paperUrl"] for p in final_paper_records]
final_titles = [p["content"]["entityName"].strip() for p in final_paper_records]

print(f"Unique paper IDs: {len(set(final_ids))} / {len(final_paper_records)}")
print(f"Unique paper URLs: {len(set(final_urls))} / {len(final_paper_records)}")
print(f"Unique paper titles: {len(set(final_titles))} / {len(final_paper_records)}")

# Write to canonical_research_papers.jsonl
with open("data/canonical/canonical_research_papers.jsonl", "w", encoding="utf-8") as f:
    for p in final_paper_records:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

# Write to canonical_research_papers.csv
with open("data/canonical/canonical_research_papers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "paper_id", "title", "authors", "publication_date", "categories",
        "paper_url", "github_url", "github_stars", "github_star_source",
        "github_star_retrieved_at", "provenance", "abstract", "collected_at"
    ])
    for cp in final_paper_records:
        d = cp["content"]["data"]
        authors_str = "; ".join(d.get("authors", [])) if isinstance(d.get("authors"), list) else str(d.get("authors"))
        cats_str = "; ".join(d.get("categories", [])) if isinstance(d.get("categories"), list) else str(d.get("categories"))
        writer.writerow([
            d.get("paperId"),
            cp["content"]["entityName"],
            authors_str,
            d.get("publicationDate"),
            cats_str,
            d.get("paperUrl"),
            d.get("githubUrl"),
            d.get("githubStars"),
            d.get("githubStarSource"),
            d.get("githubStarRetrievedAt"),
            cp["source"]["name"],
            d.get("abstract"),
            cp.get("collectedAt")
        ])

# Write to SQLite
with sqlite3.connect("data/normalized/ai_ecosystem.db") as conn:
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS ai_research_papers")
    c.execute("""
    CREATE TABLE ai_research_papers (
        paper_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        authors TEXT,
        publication_date TEXT,
        categories TEXT,
        paper_url TEXT,
        github_url TEXT,
        github_stars INTEGER,
        github_star_source TEXT,
        github_star_retrieved_at TEXT,
        provenance TEXT,
        abstract TEXT,
        collected_at TEXT
    )
    """)
    for cp in final_paper_records:
        d = cp["content"]["data"]
        authors_str = "; ".join(d.get("authors", [])) if isinstance(d.get("authors"), list) else str(d.get("authors"))
        cats_str = "; ".join(d.get("categories", [])) if isinstance(d.get("categories"), list) else str(d.get("categories"))
        c.execute("INSERT INTO ai_research_papers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            d.get("paperId"),
            cp["content"]["entityName"],
            authors_str,
            d.get("publicationDate"),
            cats_str,
            d.get("paperUrl"),
            d.get("githubUrl"),
            d.get("githubStars"),
            d.get("githubStarSource"),
            d.get("githubStarRetrievedAt"),
            cp["source"]["name"],
            d.get("abstract"),
            cp.get("collectedAt")
        ))
    conn.commit()

print("canonical_research_papers updated successfully across JSONL, CSV, and SQLite!")
