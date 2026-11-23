"""
Audit 38A: News Content Quality & Extraction Audit
==================================================
Investigates the 948 historical articles with empty content/summary.
- Analyzes per-source content extraction success rates across all 1,138 news records.
- Distinguishes RSS metadata availability from full-text extraction.
- Preserves publication timestamps and provenance.
- Identifies sources requiring extraction improvements.
- Generates audit38a_news_content_quality.csv.
"""

import sqlite3
import csv
import os
from collections import defaultdict

WORKSPACE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(WORKSPACE_DIR, "data", "working", "rolling_ai_ecosystem.db")
OUTPUT_CSV = os.path.join(WORKSPACE_DIR, "audit38a_news_content_quality.csv")

def audit_news_content():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT news_id, title, source_name, article_url, author, published_at, 
               content, summary, provenance, freshness_status, in_rolling_window, 
               date_type, date_provenance
        FROM ai_news
        ORDER BY source_name, published_at DESC
    """)
    rows = c.fetchall()
    conn.close()

    print(f"Total news articles to analyze: {len(rows)}")

    # Aggregate stats per source
    source_stats = defaultdict(lambda: {
        "total": 0, "has_content": 0, "has_summary": 0, "empty_both": 0,
        "earliest_pub": None, "latest_pub": None
    })

    records = []
    for r in rows:
        source = r["source_name"]
        has_content = bool(r["content"] and r["content"].strip())
        has_summary = bool(r["summary"] and r["summary"].strip())
        empty_both = not has_content and not has_summary

        st = source_stats[source]
        st["total"] += 1
        if has_content: st["has_content"] += 1
        if has_summary: st["has_summary"] += 1
        if empty_both: st["empty_both"] += 1

        pub = r["published_at"]
        if st["earliest_pub"] is None or pub < st["earliest_pub"]:
            st["earliest_pub"] = pub
        if st["latest_pub"] is None or pub > st["latest_pub"]:
            st["latest_pub"] = pub

        # Determine extraction status and diagnostic finding
        if has_content and has_summary:
            extraction_status = "FULL_TEXT_AND_SUMMARY_EXTRACTED"
            diagnostic_finding = "RSS payload included complete content and summary."
        elif has_content:
            extraction_status = "CONTENT_ONLY"
            diagnostic_finding = "Article content extracted; standalone summary field omitted."
        elif has_summary:
            extraction_status = "SUMMARY_ONLY"
            diagnostic_finding = "RSS description provided summary; full-text body not fetched."
        else:
            extraction_status = "METADATA_ONLY_EMPTY_CONTENT"
            if "Hugging Face" in source:
                diagnostic_finding = "Hugging Face Blog RSS feed provides only title/link; body requires secondary HTML page scraping."
            elif "DeepMind" in source:
                diagnostic_finding = "DeepMind Blog feed entry omitted RSS description; body requires secondary page scraper."
            else:
                diagnostic_finding = "Feed entry provided metadata only; body extraction missing."

        records.append({
            "news_id": r["news_id"],
            "title": r["title"],
            "source_name": source,
            "article_url": r["article_url"],
            "published_at": r["published_at"],
            "has_content": "YES" if has_content else "NO",
            "has_summary": "YES" if has_summary else "NO",
            "content_char_count": len(r["content"]) if r["content"] else 0,
            "summary_char_count": len(r["summary"]) if r["summary"] else 0,
            "extraction_status": extraction_status,
            "diagnostic_finding": diagnostic_finding,
            "date_type": r["date_type"],
            "date_provenance": r["date_provenance"],
            "in_rolling_window": r["in_rolling_window"]
        })

    # Write per-article CSV audit
    fieldnames = [
        "news_id", "source_name", "title", "published_at", "article_url",
        "has_content", "has_summary", "content_char_count", "summary_char_count",
        "extraction_status", "diagnostic_finding", "date_type", "date_provenance", "in_rolling_window"
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {OUTPUT_CSV} with {len(records)} article records.")
    print("\nSource Content Extraction Success Rates:")
    print("-" * 80)
    print(f"{'Source Name':30} | {'Total':6} | {'With Content':12} | {'Empty Both':10} | {'Extraction Rate':15}")
    print("-" * 80)
    for src, st in sorted(source_stats.items()):
        rate = (st["has_content"] / st["total"]) * 100
        print(f"{src:30} | {st['total']:6} | {st['has_content']:12} | {st['empty_both']:10} | {rate:6.1f}%")
    print("-" * 80)
    total_articles = sum(st["total"] for st in source_stats.values())
    total_empty = sum(st["empty_both"] for st in source_stats.values())
    print(f"Total articles: {total_articles}, Total empty content: {total_empty} (948 exact match: {total_empty == 948})")

if __name__ == "__main__":
    audit_news_content()
