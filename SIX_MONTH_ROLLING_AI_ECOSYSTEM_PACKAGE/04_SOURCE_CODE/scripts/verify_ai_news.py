import json
import sqlite3
import pandas as pd
import re
from urllib.parse import urlparse

def is_valid_url(url):
    if not url or not isinstance(url, str):
        return False
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and bool(parsed.netloc)

def is_valid_iso_date(dt_str):
    if not dt_str or not isinstance(dt_str, str):
        return False
    return bool(re.match(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}.*)?$', dt_str))

print("=" * 70)
print("INDEPENDENT AUDIT: STAGE 1 AI NEWS QUALITY & CONTENT AUDIT")
print("=" * 70)

# 1. Load files
with open("data/canonical/canonical_news.jsonl", "r", encoding="utf-8") as f:
    j_records = [json.loads(line) for line in f]
df_news = pd.read_csv("data/canonical/canonical_news.csv")

conn = sqlite3.connect("data/normalized/ai_ecosystem.db")
c = conn.cursor()
db_news_count = c.execute("SELECT COUNT(*) FROM ai_news").fetchone()[0]

print(f"\n1. RECORD COUNTS & PARITY:")
print(f"   Canonical JSONL Records: {len(j_records):,}")
print(f"   Canonical CSV Rows:      {len(df_news):,}")
print(f"   SQLite 'ai_news' Rows:   {db_news_count:,}")
print(f"   Exact Parity Status:     {len(j_records) == len(df_news) == db_news_count}")

# 2. Key Uniqueness
print(f"\n2. UNIQUENESS & INTEGRITY:")
print(f"   Unique news_id:     {df_news['news_id'].nunique():,} / {len(df_news):,} (Duplicates: {len(df_news) - df_news['news_id'].nunique()})")
print(f"   Unique article_url: {df_news['article_url'].nunique():,} / {len(df_news):,} (Duplicates: {len(df_news) - df_news['article_url'].nunique()})")
print(f"   Unique titles:      {df_news['title'].nunique():,} / {len(df_news):,} (Duplicates: {len(df_news) - df_news['title'].nunique()})")

# 3. Field Completeness
print(f"\n3. FIELD COMPLETENESS (CSV):")
for col in df_news.columns:
    cnt = df_news[col].notnull().sum()
    pct = cnt / len(df_news) * 100
    print(f"   - {col:22}: {cnt:,} / {len(df_news):,} ({pct:.1f}%)")

# 4. Content Status & Summary Type Breakdown
print(f"\n4. CONTENT & SUMMARY STATUS:")
print("   Content Status breakdown:")
for k, v in df_news['content_status'].value_counts().items():
    print(f"     * {k:20}: {v:,} ({v/len(df_news)*100:.1f}%)")
print("   Summary Type breakdown:")
for k, v in df_news['summary_type'].value_counts().items():
    print(f"     * {k:20}: {v:,} ({v/len(df_news)*100:.1f}%)")

# 5. Format & Data Type Validation
invalid_urls = [u for u in df_news['article_url'] if not is_valid_url(u)]
invalid_dates = [d for d in df_news['published_at'] if not is_valid_iso_date(d)]
invalid_colls = [d for d in df_news['collected_at'] if not is_valid_iso_date(d)]
print(f"\n5. FORMAT VALIDATION:")
print(f"   Invalid article URLs:    {len(invalid_urls)}")
print(f"   Invalid published dates: {len(invalid_dates)}")
print(f"   Invalid collected dates: {len(invalid_colls)}")

# 6. Source Distribution
print(f"\n6. SOURCE DISTRIBUTION:")
print(df_news['source_name'].value_counts())

# 7. AI Category Distribution
print(f"\n7. AI CATEGORY DISTRIBUTION:")
print(df_news['category'].value_counts())

# 8. Check Phase I Data Preservation
print(f"\n8. PHASE I DATA INTEGRITY CHECK:")
s_cnt = c.execute("SELECT COUNT(*) FROM ai_startups").fetchone()[0]
p_cnt = c.execute("SELECT COUNT(*) FROM ai_products").fetchone()[0]
r_cnt = c.execute("SELECT COUNT(*) FROM ai_research_papers").fetchone()[0]
print(f"   ai_startups rows:        {s_cnt:,} (Target: 1,307)")
print(f"   ai_products rows:        {p_cnt:,} (Target: 1,316)")
print(f"   ai_research_papers rows: {r_cnt:,} (Target: 1,060)")
print(f"   Phase I Preserved:       {s_cnt == 1307 and p_cnt == 1316 and r_cnt == 1060}")

print("\n" + "=" * 70)
print("STAGE 1 QUALITY AUDIT COMPLETED SUCCESSFULLY")
print("=" * 70)
