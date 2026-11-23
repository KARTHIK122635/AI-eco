import pandas as pd
import json

df_s = pd.read_csv("data/canonical/canonical_startups.csv")
df_p = pd.read_csv("data/canonical/canonical_products.csv")
df_r = pd.read_csv("data/canonical/canonical_research_papers.csv")

print("=== STARTUP SOURCES ===")
print(df_s['provenance_sources'].value_counts())

print("\n=== PRODUCT SOURCES ===")
print(df_p['provenance_source'].value_counts())

print("\n=== RESEARCH PAPER SOURCES ===")
print(df_r['provenance'].value_counts())
