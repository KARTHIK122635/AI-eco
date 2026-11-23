import pandas as pd
import json

df_r = pd.read_csv("data/canonical/canonical_research_papers.csv")
print(f"Total rows: {len(df_r)}")
print(f"Distinct paper titles: {df_r['title'].nunique()}")
print(f"Distinct paper_id: {df_r['paper_id'].nunique()}")
print(f"Distinct paper_url: {df_r['paper_url'].nunique()}")

# Find all titles with count > 1
title_counts = df_r['title'].value_counts()
repeated_titles = title_counts[title_counts > 1]
print(f"\nNumber of repeated titles: {len(repeated_titles)}")
print(f"Total rows with repeated titles: {df_r['title'].isin(repeated_titles.index).sum()}")

print("\n--- Detailed Breakdown of Repeated Titles ---")
for title, cnt in repeated_titles.items():
    sub = df_r[df_r['title'] == title]
    print(f"\nTitle: '{title}' (Count: {cnt})")
    for idx, row in sub.iterrows():
        print(f"  ID: {row['paper_id']} | Prov: {row['provenance']} | PubDate: {row['publication_date']} | URL: {row['paper_url']}")
        print(f"  Authors: {str(row['authors'])[:80]}...")
