import pandas as pd
import json

df_s = pd.read_csv("data/canonical/canonical_startups.csv")
total_startups = len(df_s)
pricing_notnull = df_s['pricing_model'].notnull().sum()
pricing_null = df_s['pricing_model'].isnull().sum()

print(f"Total startups: {total_startups}")
print(f"Pricing populated: {pricing_notnull} ({pricing_notnull/total_startups*100:.1f}%)")
print(f"Pricing null/missing: {pricing_null} ({pricing_null/total_startups*100:.1f}%)")

print("\nPricing breakdown:")
print(df_s['pricing_model'].value_counts(dropna=False))
