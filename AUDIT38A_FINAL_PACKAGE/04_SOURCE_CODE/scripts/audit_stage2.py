import json
import pandas as pd
from collections import Counter

# 1. Inspect Products
df_prod = pd.read_csv('data/normalized/ai_products.csv')
print(f"Total products in CSV: {len(df_prod)}")
print(f"Unique product names in CSV: {df_prod['name'].nunique()}")
print(f"Unique product_ids in CSV: {df_prod['product_id'].nunique()}")
print(f"Unique original_source_urls in CSV: {df_prod['original_source_url'].nunique()}")

dup_counts = df_prod['name'].value_counts()
dups = dup_counts[dup_counts > 1]
print(f"Total repeated product titles: {len(dups)}")
print("\nTop 10 repeated product titles:")
for name, count in dups.head(10).items():
    print(f"  - '{name}': {count} occurrences")

print(f"\nDetailed inspection of top 3 repeated titles:")
for name in dups.head(3).index:
    print(f"\n--- Product Title: '{name}' ---")
    rows = df_prod[df_prod['name'] == name]
    for _, r in rows.iterrows():
        print(f"  ID: {r['product_id']} | Dev: {r['developer_or_company']} | Type: {r['product_type']} | URL: {r['original_source_url']}")

# 2. Inspect Startups missing employee counts and pricing
df_startups = pd.read_csv('data/normalized/ai_startups.csv')
print(f"\n==========================================")
print(f"Total startups in CSV: {len(df_startups)}")
missing_emp = df_startups[df_startups['employee_count'].isnull()]
print(f"Startups with missing employee_count: {len(missing_emp)}")
print("Sample startups with missing employee_count:")
for _, r in missing_emp.head(10).iterrows():
    print(f"  - {r['name']} ({r['startup_id']}) | Source: {r['provenance_sources']} | URL: {r['primary_source_url']}")

missing_price = df_startups[df_startups['pricing_model'].isnull()]
print(f"\nStartups with missing pricing_model: {len(missing_price)}")
print("Sample startups with missing pricing_model:")
for _, r in missing_price.head(10).iterrows():
    print(f"  - {r['name']} | Focus: {r['ai_focus_area']} | Desc: {str(r['description'])[:60]}...")

# 3. Check website coverage
missing_web = df_startups[df_startups['website'].isnull()]
print(f"\nStartups with missing website: {len(missing_web)}")
