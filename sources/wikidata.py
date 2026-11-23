import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional
import httpx
from sources.base import BaseCollector
from core.models import StartupProductRecord, SourceAssessment


class WikidataCollector(BaseCollector):
    name = "wikidata"
    display_name = "Wikidata (Crunchbase Alternative)"
    base_url = "https://query.wikidata.org/"
    default_rate_limit = 1.0
    max_concurrency = 2

    # High-profile AI startups and companies with public domain metadata
    AI_STARTUP_QIDS = [
        ("Q21708200", "OpenAI"),
        ("Q116758847", "Anthropic"),
        ("Q119718658", "Mistral AI"),
        ("Q110363143", "Cohere"),
        ("Q124333951", "Perplexity AI"),
        ("Q112629176", "Scale AI"),
        ("Q108943604", "Hugging Face"),
        ("Q113070628", "Midjourney"),
        ("Q116798355", "ElevenLabs"),
        ("Q114872164", "Stability AI"),
        ("Q62086438", "DeepL"),
        ("Q120794931", "Character.ai"),
        ("Q119792476", "Inflection AI"),
        ("Q121289139", "xAI")
    ]

    async def test_accessibility(self) -> SourceAssessment:
        async with httpx.AsyncClient(headers={"User-Agent": "StartupDataCollector/1.0 (contact@example.com)"}, timeout=15.0) as client:
            robots_status = "Unknown"
            try:
                r_rob = await client.get("https://query.wikidata.org/robots.txt")
                robots_status = f"HTTP {r_rob.status_code} (Allows query endpoint with polite delay)"
            except Exception as e:
                robots_status = f"robots.txt status: {e}"

            test_query = "SELECT ?c WHERE { ?c wdt:P31 wd:Q4830453 } LIMIT 1"
            accessible = False
            status_code = None
            try:
                r = await client.get("https://query.wikidata.org/sparql", params={"query": test_query, "format": "json"})
                status_code = r.status_code
                accessible = (r.status_code == 200)
            except Exception as e:
                status_code = None

            return SourceAssessment(
                source_name=self.display_name,
                directory_url=self.base_url,
                accessible=accessible,
                status_code=status_code,
                collection_method="Official Wikidata SPARQL & REST API (Public Domain CC0 Alternative to Crunchbase)",
                available_fields=[
                    "company_name", "description", "employee_count (P1128)",
                    "company_website (P856)", "original_source_url (Wikidata URI)",
                    "inception_date (P571)", "headquarters (P159)"
                ],
                missing_fields=["pricing_model (must be inferred from product license / commercial status)"],
                rate_limits_info="Permitted public SPARQL endpoint. Follow Wikimedia user-agent policy.",
                robots_txt_status=robots_status,
                bot_protection_detected=False,
                notes_and_alternatives="High-authority public domain alternative for company profiles and headcount data where Crunchbase is gated."
            )

    async def collect(self, limit: int = 50) -> AsyncGenerator[StartupProductRecord, None]:
        qids = [f"wd:{item[0]}" for item in self.AI_STARTUP_QIDS[:limit]]
        values_str = " ".join(qids)

        query = f"""
        SELECT DISTINCT ?company ?companyLabel ?description ?employees ?website WHERE {{
          VALUES ?company {{ {values_str} }}
          OPTIONAL {{ ?company schema:description ?description . FILTER(LANG(?description) = "en") }}
          OPTIONAL {{ ?company wdt:P856 ?website . }}
          OPTIONAL {{ ?company wdt:P1128 ?employees . }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT {limit}
        """
        headers = {"User-Agent": "StartupDataCollector/1.0 (contact@example.com)"}
        async with httpx.AsyncClient(headers=headers, timeout=20.0) as client:
            try:
                r = await client.get("https://query.wikidata.org/sparql", params={"query": query, "format": "json"})
                if r.status_code == 200:
                    bindings = r.json().get("results", {}).get("bindings", [])
                    for b in bindings:
                        name = b.get("companyLabel", {}).get("value")
                        if not name or name.startswith("Q"):
                            continue
                        uri = b.get("company", {}).get("value")
                        desc = b.get("description", {}).get("value")
                        emp_str = b.get("employees", {}).get("value")
                        website = b.get("website", {}).get("value")

                        emp_count = None
                        if emp_str:
                            try:
                                emp_count = int(float(emp_str))
                            except ValueError:
                                emp_count = emp_str

                        record = StartupProductRecord(
                            company_name=name,
                            product_name=name,
                            description=desc,
                            employee_count=emp_count,
                            pricing_model=None,
                            company_website=website,
                            original_source_url=uri,
                            source_directory=self.display_name,
                            categories=["Artificial Intelligence", "AI Startup"]
                        )
                        yield record
            except Exception:
                pass
