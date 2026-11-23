import httpx

client = httpx.Client(headers={'User-Agent': 'StartupDataCollector/2.0 (research@example.com)'}, timeout=15)

# Fast targeted query on Wikidata for AI companies
query = """
SELECT ?company ?companyLabel ?description ?employees ?website ?inception WHERE {
  ?company wdt:P31/wdt:P279* wd:Q4830453 ; # Business enterprise
           wdt:P101 wd:Q11660 .             # Field of work: Artificial Intelligence
  OPTIONAL { ?company wdt:P1128 ?employees . }
  OPTIONAL { ?company wdt:P856 ?website . }
  OPTIONAL { ?company wdt:P571 ?inception . }
  OPTIONAL { ?company schema:description ?description . FILTER(LANG(?description) = "en") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 20
"""

r = client.get("https://query.wikidata.org/sparql", params={'query': query, 'format': 'json'})
print("Wikidata status:", r.status_code)
if r.status_code == 200:
    results = r.json().get('results', {}).get('bindings', [])
    print(f"Wikidata sample bindings count: {len(results)}")
    for b in results[:5]:
        name = b.get('companyLabel', {}).get('value')
        emp = b.get('employees', {}).get('value')
        web = b.get('website', {}).get('value')
        desc = b.get('description', {}).get('value')
        print(f"- {name} | Emp: {emp} | Web: {web} | Desc: {desc}")
