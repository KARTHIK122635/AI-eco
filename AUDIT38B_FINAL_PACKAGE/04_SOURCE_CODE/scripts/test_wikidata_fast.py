import httpx
import json

client = httpx.Client(headers={'User-Agent': 'StartupDiscoveryBot/1.0 (test@example.com)'}, timeout=15)

# Fast SPARQL query for AI companies / startups
query = """
SELECT DISTINCT ?company ?companyLabel ?description ?website ?employees ?inception WHERE {
  VALUES ?company { wd:Q116758847 wd:Q118876059 wd:Q110667554 wd:Q120300438 wd:Q108888062 wd:Q506240 wd:Q8805 wd:Q2283 }
  OPTIONAL { ?company schema:description ?description . FILTER(LANG(?description) = "en") }
  OPTIONAL { ?company wdt:P856 ?website . }
  OPTIONAL { ?company wdt:P1128 ?employees . }
  OPTIONAL { ?company wdt:P571 ?inception . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

r = client.get("https://query.wikidata.org/sparql", params={'query': query, 'format': 'json'})
print("Wikidata status:", r.status_code)
if r.status_code == 200:
    results = r.json().get('results', {}).get('bindings', [])
    for row in results:
        print("Name:", row.get('companyLabel', {}).get('value'))
        print("Desc:", row.get('description', {}).get('value'))
        print("Employees:", row.get('employees', {}).get('value'))
        print("Website:", row.get('website', {}).get('value'))
        print("-" * 30)
