import sqlite3

conn = sqlite3.connect('file:data/working/candidate_rolling_ai_ecosystem.db?mode=ro', uri=True)
cursor = conn.cursor()

# Papers with github_url
cursor.execute("SELECT count(*) FROM ai_research_papers WHERE github_url IS NOT NULL AND github_url != ''")
print("Papers with github_url:", cursor.fetchone()[0])

# Papers with github in abstract or paper_url but no github_url
cursor.execute("SELECT count(*) FROM ai_research_papers WHERE (abstract LIKE '%github.com%' OR paper_url LIKE '%github.com%') AND (github_url IS NULL OR github_url = '')")
print("Papers with github in abstract/url but not github_url:", cursor.fetchone()[0])

# Products with github in developer_profile_url or original_source_url
cursor.execute("SELECT count(*) FROM ai_products WHERE developer_profile_url LIKE '%github.com%' OR original_source_url LIKE '%github.com%'")
print("Products with github URLs:", cursor.fetchone()[0])

# Startups with github in website or primary_source_url
cursor.execute("SELECT count(*) FROM ai_startups WHERE website LIKE '%github.com%' OR primary_source_url LIKE '%github.com%'")
print("Startups with github URLs:", cursor.fetchone()[0])

# Repositories check
cursor.execute("SELECT count(*), count(associated_paper_id) FROM github_repositories")
print("github_repositories total, with associated_paper_id:", cursor.fetchone())

# Sample of products with github
cursor.execute("SELECT product_id, entity_name, developer_profile_url, original_source_url FROM ai_products WHERE developer_profile_url LIKE '%github.com%' OR original_source_url LIKE '%github.com%' LIMIT 5")
print("\nSample Products with GitHub:")
for r in cursor.fetchall():
    print(r)

# Sample of startups with github
cursor.execute("SELECT startup_id, entity_name, website, primary_source_url FROM ai_startups WHERE website LIKE '%github.com%' OR primary_source_url LIKE '%github.com%' LIMIT 5")
print("\nSample Startups with GitHub:")
for r in cursor.fetchall():
    print(r)

# Check unique repos in github_repositories
cursor.execute("SELECT count(DISTINCT repo_id), count(DISTINCT html_url) FROM github_repositories")
print("\nUnique repo_id and html_url in github_repositories:", cursor.fetchone())

conn.close()

def inspect_abstract_mention():
    conn = sqlite3.connect('file:data/working/candidate_rolling_ai_ecosystem.db?mode=ro', uri=True)
    cursor = conn.cursor()
    cursor.execute("SELECT paper_id, title, paper_url, abstract FROM ai_research_papers WHERE (abstract LIKE '%github.com%' OR paper_url LIKE '%github.com%') AND (github_url IS NULL OR github_url = '')")
    print("Paper with abstract GitHub mention:")
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Title: {row[1]}, URL: {row[2]}")
        print(f"Abstract snippet: {row[3][:300]}...")
    conn.close()

if __name__ == '__main__':
    inspect_abstract_mention()
