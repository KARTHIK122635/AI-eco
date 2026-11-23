import httpx

client = httpx.Client(headers={
    'User-Agent': 'StartupDiscoveryBot/1.0 (test@example.com)'
}, timeout=10.0)

# 1. Wikidata SPARQL: AI startups and companies
sparql_query = """
SELECT ?company ?companyLabel ?description ?employees ?website ?countryLabel WHERE {
  ?company wdt:P31/wdt:P279* wd:Q4830453 ; # Instance/subclass of business enterprise
           wdt:P101 wd:Q11660 .             # Field of work: Artificial Intelligence
  OPTIONAL { ?company wdt:P1128 ?employees . } # Employees count
  OPTIONAL { ?company wdt:P856 ?website . }     # Website
  OPTIONAL { ?company schema:description ?description . FILTER(LANG(?description) = "en") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 5
"""

try:
    r = client.get("https://query.wikidata.org/sparql", params={'query': sparql_query, 'format': 'json'})
    print("Wikidata SPARQL Status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        bindings = data.get('results', {}).get('bindings', [])
        print("Wikidata results count:", len(bindings))
        for b in bindings[:2]:
            print("Company:", b.get('companyLabel', {}).get('value'))
            print("Desc:", b.get('description', {}).get('value'))
            print("Employees:", b.get('employees', {}).get('value'))
            print("Website:", b.get('website', {}).get('value'))
            print("-" * 20)
except Exception as e:
    print("Wikidata error:", e)

# 2. GitHub API: AI Startups / Organizations
try:
    r_gh = client.get("https://api.github.com/search/repositories?q=topic:ai-product+OR+topic:startup&per_page=5")
    print("GitHub API Status:", r_gh.status_code)
    if r_gh.status_code == 200:
        items = r_gh.json().get('items', [])
        print("GitHub repos count:", len(items))
        if items:
            print("Sample repo:", items[0].get('full_name'), items[0].get('description'))
except Exception as e:
    print("GitHub error:", e)
