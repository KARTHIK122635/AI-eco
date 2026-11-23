import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("WikidataEnricher")


class WikidataEnricher:
    """Fast enrichment client for missing company headcount and website from Wikidata."""
    def __init__(self):
        self.client = httpx.Client(
            headers={"User-Agent": "AIStartupDataEnricher/1.0 (contact@aisolution.internal)"},
            timeout=3.0  # Fast fail to avoid blocking
        )
        self.cache: Dict[str, Optional[Dict[str, Any]]] = {}

    def enrich_company(self, company_name: str) -> Optional[Dict[str, Any]]:
        clean_name = company_name.strip()
        if not clean_name or len(clean_name) < 3:
            return None
        if clean_name in self.cache:
            return self.cache[clean_name]

        try:
            r = self.client.get(
                "https://www.wikidata.org/w/api.php",
                params={
                    "action": "wbsearchentities",
                    "search": clean_name,
                    "language": "en",
                    "format": "json",
                    "limit": 2
                }
            )
            if r.status_code != 200:
                self.cache[clean_name] = None
                return None

            search_results = r.json().get("search", [])
            if not search_results:
                self.cache[clean_name] = None
                return None

            chosen_qid = search_results[0].get("id")
            if not chosen_qid:
                self.cache[clean_name] = None
                return None

            r2 = self.client.get(f"https://www.wikidata.org/wiki/Special:EntityData/{chosen_qid}.json")
            if r2.status_code != 200:
                self.cache[clean_name] = None
                return None

            entities = r2.json().get("entities", {})
            claims = entities.get(chosen_qid, {}).get("claims", {})

            employees = None
            if "P1128" in claims:
                try:
                    snak = claims["P1128"][0]["mainsnak"]["datavalue"]["value"]
                    if isinstance(snak, dict) and "amount" in snak:
                        employees = int(float(snak["amount"]))
                except Exception:
                    pass

            website = None
            if "P856" in claims:
                try:
                    website = claims["P856"][0]["mainsnak"]["datavalue"]["value"]
                except Exception:
                    pass

            result = {
                "qid": chosen_qid,
                "employees": employees,
                "website": website,
                "wikidata_url": f"http://www.wikidata.org/entity/{chosen_qid}"
            }
            self.cache[clean_name] = result
            return result
        except Exception:
            self.cache[clean_name] = None
            return None
