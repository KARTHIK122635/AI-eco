import os
import json
import sqlite3
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime

print("=" * 80)
print("DEEP INDEPENDENT AUDIT OF PHASE I DATASETS")
print("=" * 80)

# ---------------------------------------------------------
# 1. STARTUPS AUDIT
# ---------------------------------------------------------
jsonl_startups_file = 'data/canonical/canonical_startups.jsonl'
csv_startups_file = 'data/canonical/canonical_startups.csv'

with open(jsonl_startups_file, 'r', encoding='utf-8') as f:
    startups_jsonl = [json.loads(line) for line in f]
df_startups_csv = pd.read_csv(csv_startups_file)

with sqlite3.connect('data/normalized/ai_ecosystem.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ai_startups")
    startups_db = cursor.fetchall()

print(f"\n[1] STARTUPS RECORD COUNT CONSISTENCY:")
print(f"  - JSONL count:  {len(startups_jsonl):,}")
print(f"  - CSV count:    {len(df_startups_csv):,}")
print(f"  - SQLite count: {len(startups_db):,}")
assert len(startups_jsonl) == len(df_startups_csv) == len(startups_db), "Startup counts mismatch across formats!"

# Duplicate checks on Startups
startup_ids = [s['content']['data']['startupId'] for s in startups_jsonl]
startup_urls = [s['source']['url'] for s in startups_jsonl]
startup_names = [s['content']['entityName'] for s in startups_jsonl]

print(f"\n  Uniqueness Metrics for Startups:")
print(f"  - Unique startupId:        {len(set(startup_ids)):,}/{len(startup_ids):,}")
print(f"  - Unique source URL:       {len(set(startup_urls)):,}/{len(startup_urls):,}")
print(f"  - Unique entityName:       {len(set(startup_names)):,}/{len(startup_names):,}")

# Missing fields on Startups
missing_emp = sum(1 for s in startups_jsonl if s['content']['data']['employeeCount'] is None)
missing_price = sum(1 for s in startups_jsonl if s['content']['data']['pricingModel'] is None)
missing_web = sum(1 for s in startups_jsonl if s['content']['data']['website'] is None)
missing_hq = sum(1 for s in startups_jsonl if s['content']['data']['headquarters'] is None)
missing_batch = sum(1 for s in startups_jsonl if s['content']['data']['batchOrFounded'] is None)

print(f"\n  Missing Values on Startups (out of {len(startups_jsonl):,}):")
print(f"  - Missing employeeCount:  {missing_emp} (Populated: {len(startups_jsonl) - missing_emp:,} / {len(startups_jsonl):,})")
print(f"  - Missing pricingModel:   {missing_price} (Populated: {len(startups_jsonl) - missing_price:,} / {len(startups_jsonl):,})")
print(f"  - Missing website:        {missing_web} (Populated: {len(startups_jsonl) - missing_web:,} / {len(startups_jsonl):,})")
print(f"  - Missing headquarters:   {missing_hq} (Populated: {len(startups_jsonl) - missing_hq:,} / {len(startups_jsonl):,})")
print(f"  - Missing batchOrFounded: {missing_batch} (Populated: {len(startups_jsonl) - missing_batch:,} / {len(startups_jsonl):,})")

# ---------------------------------------------------------
# 2. PRODUCTS AUDIT
# ---------------------------------------------------------
jsonl_products_file = 'data/canonical/canonical_products.jsonl'
csv_products_file = 'data/canonical/canonical_products.csv'

with open(jsonl_products_file, 'r', encoding='utf-8') as f:
    products_jsonl = [json.loads(line) for line in f]
df_products_csv = pd.read_csv(csv_products_file)

with sqlite3.connect('data/normalized/ai_ecosystem.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ai_products")
    products_db = cursor.fetchall()

print(f"\n[2] PRODUCTS RECORD COUNT CONSISTENCY:")
print(f"  - JSONL count:  {len(products_jsonl):,}")
print(f"  - CSV count:    {len(df_products_csv):,}")
print(f"  - SQLite count: {len(products_db):,}")
assert len(products_jsonl) == len(df_products_csv) == len(products_db), "Product counts mismatch across formats!"

product_ids = [p['content']['data']['productId'] for p in products_jsonl]
product_urls = [p['source']['url'] for p in products_jsonl]
product_names = [p['content']['entityName'] for p in products_jsonl]

print(f"\n  Uniqueness Metrics for Products:")
print(f"  - Unique productId:        {len(set(product_ids)):,}/{len(product_ids):,}")
print(f"  - Unique source URL:       {len(set(product_urls)):,}/{len(product_urls):,}")
print(f"  - Unique entityName:       {len(set(product_names)):,}/{len(product_names):,}")

# Investigate product duplicate titles
from collections import Counter
title_counts = Counter(product_names)
rep_titles = {k: v for k, v in title_counts.items() if v > 1}
print(f"  - Distinct titles count:   {len(title_counts):,}")
print(f"  - Repeated titles count:   {len(rep_titles):,} titles appear multiple times (total {sum(rep_titles.values())} records)")

# Verify that every repeated title has different developer or source URL
diff_dev_count = 0
for title, cnt in list(rep_titles.items())[:5]:
    subset = [p for p in products_jsonl if p['content']['entityName'] == title]
    devs = [p['content']['data']['developerOrCompany'] for p in subset]
    urls = [p['source']['url'] for p in subset]
    print(f"    * '{title}' ({cnt} records): devs={devs[:3]}, unique_urls={len(set(urls))}/{len(urls)}")

# ---------------------------------------------------------
# 3. RESEARCH PAPERS AUDIT
# ---------------------------------------------------------
jsonl_papers_file = 'data/canonical/canonical_research_papers.jsonl'
csv_papers_file = 'data/canonical/canonical_research_papers.csv'

with open(jsonl_papers_file, 'r', encoding='utf-8') as f:
    papers_jsonl = [json.loads(line) for line in f]
df_papers_csv = pd.read_csv(csv_papers_file)

with sqlite3.connect('data/normalized/ai_ecosystem.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ai_research_papers")
    papers_db = cursor.fetchall()

print(f"\n[3] RESEARCH PAPERS RECORD COUNT CONSISTENCY:")
print(f"  - JSONL count:  {len(papers_jsonl):,}")
print(f"  - CSV count:    {len(df_papers_csv):,}")
print(f"  - SQLite count: {len(papers_db):,}")
assert len(papers_jsonl) == len(df_papers_csv) == len(papers_db), "Paper counts mismatch across formats!"

paper_ids = [p['content']['data']['paperId'] for p in papers_jsonl]
paper_urls = [p['source']['url'] for p in papers_jsonl]
paper_titles = [p['content']['entityName'] for p in papers_jsonl]

print(f"\n  Uniqueness Metrics for Research Papers:")
print(f"  - Unique paperId:          {len(set(paper_ids)):,}/{len(paper_ids):,}")
print(f"  - Unique paper source URL: {len(set(paper_urls)):,}/{len(paper_urls):,}")
print(f"  - Unique titles:           {len(set(paper_titles)):,}/{len(paper_titles):,}")

# GitHub repo & star analysis
with_github = [p for p in papers_jsonl if p['content']['data']['githubUrl'] is not None]
with_stars = [p for p in papers_jsonl if p['content']['data']['githubStars'] is not None]
print(f"\n  GitHub Code & Star Analysis on Research Papers:")
print(f"  - Papers with GitHub URL:   {len(with_github):,} / {len(papers_jsonl):,}")
print(f"  - Papers with GitHub Stars: {len(with_stars):,} / {len(papers_jsonl):,}")
print(f"  - Papers with GitHub URL but Stars=null: {len(with_github) - len(with_stars)}")

# Provenance breakdown of the 189 with GitHub URLs
hf_prov = [p for p in with_github if 'Hugging Face' in p['source']['name']]
arxiv_prov = [p for p in with_github if 'arXiv' in p['source']['name']]
print(f"    * From Hugging Face Daily Papers: {len(hf_prov)} (with stars: {sum(1 for p in hf_prov if p['content']['data']['githubStars'] is not None)})")
print(f"    * From arXiv abstract/comment:    {len(arxiv_prov)} (with stars: {sum(1 for p in arxiv_prov if p['content']['data']['githubStars'] is not None)})")

# ---------------------------------------------------------
# 4. SUBMISSION ALL-IN-ONE AUDIT
# ---------------------------------------------------------
with open('data/canonical/canonical_submission_all.jsonl', 'r', encoding='utf-8') as f:
    all_jsonl = [json.loads(line) for line in f]

print(f"\n[4] UNIFIED SUBMISSION STREAM (canonical_submission_all.jsonl):")
print(f"  - Total records: {len(all_jsonl):,}")
record_types = Counter(r['recordType'] for r in all_jsonl)
print(f"  - Breakdown by recordType: {dict(record_types)}")
assert len(all_jsonl) == len(startups_jsonl) + len(products_jsonl) + len(papers_jsonl), "Total submission stream count mismatch!"
