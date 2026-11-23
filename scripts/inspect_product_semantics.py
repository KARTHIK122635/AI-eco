import json
import pandas as pd

df_p = pd.read_csv("data/canonical/canonical_products.csv")
print("Product Types:")
print(df_p['product_type'].value_counts())

print("\nCurrent Pricing Models:")
print(df_p['pricing_model'].value_counts())

print("\nTop Licenses:")
print(df_p['license'].value_counts().head(10))
