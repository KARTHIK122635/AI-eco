import pandas as pd
import json

df_p = pd.read_csv("data/canonical/canonical_products.csv")
dupe_names = df_p[df_p.duplicated(subset=["entity_name"], keep=False)].sort_values("entity_name")
print(f"Total product records with shared entity_name: {len(dupe_names)}")
print(f"Distinct entity_names that repeat: {dupe_names['entity_name'].nunique()}")

top_dupes = dupe_names['entity_name'].value_counts()
print("\nTop repeated entity names:")
for name, cnt in top_dupes.head(15).items():
    sub = dupe_names[dupe_names['entity_name'] == name]
    devs = sub['developer_or_company'].tolist()
    types = sub['product_type'].tolist()
    urls = sub['original_source_url'].tolist()
    print(f"\nName: '{name}' ({cnt} instances)")
    for d, t, u in zip(devs, types, urls):
        print(f"   Developer: {d:25} | Type: {t:22} | URL: {u}")
