import pandas as pd
import json

df_r = pd.read_csv("data/canonical/canonical_research_papers.csv")
total_papers = len(df_r)
has_github = df_r['github_url'].notnull()
has_stars = df_r['github_stars'].notnull()

print(f"Total papers: {total_papers}")
print(f"Papers with GitHub URL: {has_github.sum()} ({has_github.sum()/total_papers*100:.1f}%)")
print(f"Papers with GitHub stars: {has_stars.sum()} ({has_stars.sum()/total_papers*100:.1f}%)")
print(f"Papers with GitHub URL but null stars: {(has_github & ~has_stars).sum()}")

# Inspect provenance of papers with stars vs null stars
print("\nProvenance breakdown for papers with GitHub URL:")
print(df_r[has_github]['provenance'].value_counts())

print("\nProvenance breakdown for papers with GitHub stars:")
print(df_r[has_stars]['provenance'].value_counts())

print("\nProvenance breakdown for papers with GitHub URL but NULL stars:")
print(df_r[has_github & ~has_stars]['provenance'].value_counts())
