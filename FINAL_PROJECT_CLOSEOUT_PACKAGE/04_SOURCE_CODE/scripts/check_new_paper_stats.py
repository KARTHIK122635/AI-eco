import pandas as pd

df_r = pd.read_csv("data/canonical/canonical_research_papers.csv")
print(f"Total papers: {len(df_r)}")
print(f"Unique titles: {df_r['title'].nunique()}")
print(f"Unique paper_id: {df_r['paper_id'].nunique()}")
print(f"Unique paper_url: {df_r['paper_url'].nunique()}")

has_gh = df_r['github_url'].notnull()
has_stars = df_r['github_stars'].notnull()
print(f"Papers with GitHub URL: {has_gh.sum()}")
print(f"Papers with GitHub Stars: {has_stars.sum()}")
print(f"Papers with GitHub URL but Null Stars: {(has_gh & ~has_stars).sum()}")

print("\nStar Provenance breakdown:")
print(df_r[has_gh]['github_star_source'].value_counts(dropna=False))
