import os
import sys
sys.path.insert(0, ".")
import json
import csv
import sqlite3
import time
from datetime import datetime, timezone

from core.github_client import check_rate_limit, parse_github_owner_repo, fetch_github_stars

# Load research papers
with open("data/canonical/canonical_research_papers.jsonl", "r", encoding="utf-8") as f:
    papers = [json.loads(line) for line in f]

rate_info = check_rate_limit()
print(f"GitHub API Rate Limit Status: Limit={rate_info['limit']}, Remaining={rate_info['remaining']}, Authenticated={rate_info['authenticated']}")

retried_count = 0
newly_fetched = 0

updated_papers = []
for p in papers:
    d = p["content"]["data"]
    gh_url = d.get("githubUrl")
    stars = d.get("githubStars")
    source_name = p["source"]["name"]
    
    star_source = d.get("githubStarSource")
    star_retrieved_at = d.get("githubStarRetrievedAt")
    
    if gh_url:
        if stars is not None and not star_source:
            if "Hugging Face" in source_name:
                star_source = "huggingface_daily_papers"
                star_retrieved_at = "2026-11-21T06:09:12Z"
            else:
                star_source = "official_github_rest_api"
                star_retrieved_at = "2026-11-21T06:45:22Z"
        
        # If stars are null and we have rate limit quota, retry
        if stars is None and rate_info["remaining"] > 0:
            parsed = parse_github_owner_repo(gh_url)
            if parsed:
                owner, repo = parsed
                retried_count += 1
                fetched_stars, fetched_src, fetched_ts = fetch_github_stars(owner, repo)
                if fetched_stars is not None:
                    stars = fetched_stars
                    star_source = fetched_src
                    star_retrieved_at = fetched_ts
                    newly_fetched += 1
                    print(f"  [SUCCESS] Fetched {stars} stars for {owner}/{repo}")
                else:
                    rate_info = check_rate_limit()
                    if rate_info["remaining"] <= 0:
                        print("  [INFO] Rate limit reached. Ceasing outbound queries.")
                time.sleep(0.5)

    d["githubStars"] = stars
    d["githubStarSource"] = star_source
    d["githubStarRetrievedAt"] = star_retrieved_at
    updated_papers.append(p)

print(f"\nProcessing summary:")
print(f"  Total papers: {len(updated_papers)}")
print(f"  Retried count: {retried_count}")
print(f"  Newly fetched: {newly_fetched}")

# Write updated JSONL
with open("data/canonical/canonical_research_papers.jsonl", "w", encoding="utf-8") as f:
    for p in updated_papers:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

# Write updated CSV
csv_path = "data/canonical/canonical_research_papers.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "paper_id", "title", "authors", "publication_date", "categories",
        "paper_url", "github_url", "github_stars", "github_star_source",
        "github_star_retrieved_at", "provenance", "abstract", "collected_at"
    ])
    for cp in updated_papers:
        d = cp["content"]["data"]
        authors_str = "; ".join(d.get("authors", [])) if isinstance(d.get("authors"), list) else str(d.get("authors"))
        cats_str = "; ".join(d.get("categories", [])) if isinstance(d.get("categories"), list) else str(d.get("categories"))
        writer.writerow([
            d.get("paperId"),
            cp["content"]["entityName"],
            authors_str,
            d.get("publicationDate"),
            cats_str,
            d.get("paperUrl") or cp["source"]["url"],
            d.get("githubUrl"),
            d.get("githubStars"),
            d.get("githubStarSource"),
            d.get("githubStarRetrievedAt"),
            cp["source"]["name"],
            d.get("abstract"),
            cp.get("collectedAt")
        ])

# Update SQLite table
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
    for cp in updated_papers:
        d = cp["content"]["data"]
        authors_str = "; ".join(d.get("authors", [])) if isinstance(d.get("authors"), list) else str(d.get("authors"))
        cats_str = "; ".join(d.get("categories", [])) if isinstance(d.get("categories"), list) else str(d.get("categories"))
        c.execute("INSERT INTO ai_research_papers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            d.get("paperId"),
            cp["content"]["entityName"],
            authors_str,
            d.get("publicationDate"),
            cats_str,
            d.get("paperUrl") or cp["source"]["url"],
            d.get("githubUrl"),
            d.get("githubStars"),
            d.get("githubStarSource"),
            d.get("githubStarRetrievedAt"),
            cp["source"]["name"],
            d.get("abstract"),
            cp.get("collectedAt")
        ))
    conn.commit()

print(f"Updated {len(updated_papers)} research papers in JSONL, CSV, and SQLite.")
