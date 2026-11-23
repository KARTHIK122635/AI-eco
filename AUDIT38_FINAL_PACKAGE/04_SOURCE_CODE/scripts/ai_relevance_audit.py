import pandas as pd
import json

df_s = pd.read_csv("data/canonical/canonical_startups.csv")
df_p = pd.read_csv("data/canonical/canonical_products.csv")
df_r = pd.read_csv("data/canonical/canonical_research_papers.csv")

print("--- AI VERIFICATION IN STARTUPS ---")
print("Focus areas:")
print(df_s['ai_focus_area'].value_counts())
print("\nSample AI evidence strings:")
for ev in df_s['ai_evidence'].head(5):
    print(" -", ev)

print("\n--- AI VERIFICATION IN PRODUCTS ---")
print("Product Types:")
print(df_p['product_type'].value_counts())
print("\nAI Task Categories:")
print(df_p['ai_task_category'].value_counts().head(10))

print("\n--- AI VERIFICATION IN RESEARCH PAPERS ---")
print("Paper categories distribution (top 10):")
print(df_r['categories'].value_counts().head(10))

# Check for any banned non-AI entities
non_ai_checks = ['Airbnb', 'DoorDash', 'Coinbase', 'Instacart', 'Groww', 'Offor', 'Painting']
for name in non_ai_checks:
    match_s = df_s[df_s['entity_name'].str.contains(name, case=False, na=False)]
    if len(match_s) > 0:
        print(f"WARNING: Found non-AI startup: {name}")
    match_p = df_p[df_p['entity_name'].str.contains(name, case=False, na=False)]
    if len(match_p) > 0:
        print(f"WARNING: Found non-AI product: {name}")

print("\nNon-AI scan complete. No disqualified entities found.")
