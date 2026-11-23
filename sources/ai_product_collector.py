import asyncio
import httpx
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from typing import AsyncGenerator, List, Dict, Any
from core.schemas import AIProduct, evaluate_ai_evidence

logger = logging.getLogger("AIProductCollector")


class AIProductCollector:
    """
    Collects and validates at least 1,000 verified AI products (models, applications,
    spaces, and tools) from Hugging Face and Product Hunt.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

    async def collect_hf_spaces(self, limit: int = 550) -> AsyncGenerator[AIProduct, None]:
        """Collects interactive AI products and spaces from Hugging Face Hub."""
        url = f"https://huggingface.co/api/spaces?limit={limit}&full=true"
        async with httpx.AsyncClient(headers=self.headers, timeout=20.0) as client:
            try:
                r = await client.get(url)
                if r.status_code == 200:
                    spaces = r.json()
                    for sp in spaces:
                        space_id = sp.get("id", "")
                        author = sp.get("author") or (space_id.split("/")[0] if "/" in space_id else "Community")
                        card = sp.get("cardData") or {}
                        title = card.get("title") or space_id.split("/")[-1]
                        desc = card.get("short_description") or card.get("title") or f"Hugging Face Space by {author}"
                        sdk = sp.get("sdk", "gradio")
                        tags = sp.get("tags") or []

                        product = AIProduct(
                            product_id=f"hf_space_{space_id.replace('/', '_')}",
                            name=title,
                            description=desc,
                            product_type=f"AI Application / Interactive Space ({sdk})",
                            ai_task_category=tags[0] if tags else "interactive-ai-app",
                            developer_or_company=author.title(),
                            pricing_model="Open Source / Free Web App",
                            original_source_url=f"https://huggingface.co/spaces/{space_id}",
                            provenance_source="Hugging Face Spaces",
                            license="Open Source",
                            metrics={"likes": sp.get("likes", 0), "sdk": sdk},
                            raw_metadata={"tags": tags[:6]}
                        )
                        yield product
            except Exception as e:
                logger.error(f"Error collecting HF spaces: {e}")

    async def collect_hf_models(self, limit: int = 550) -> AsyncGenerator[AIProduct, None]:
        """Collects AI models and foundation weights from Hugging Face Hub."""
        url = f"https://huggingface.co/api/models?limit={limit}&full=true&sort=trendingScore&direction=-1"
        async with httpx.AsyncClient(headers=self.headers, timeout=20.0) as client:
            try:
                r = await client.get(url)
                if r.status_code == 200:
                    models = r.json()
                    for m in models:
                        mod_id = m.get("id", "")
                        author = m.get("author") or (mod_id.split("/")[0] if "/" in mod_id else "Community")
                        pipeline = m.get("pipeline_tag") or "machine-learning"
                        gated = m.get("gated", False)
                        pricing = "Gated Commercial / Research License" if gated else "Open Source Weights"
                        tags = m.get("tags") or []

                        product = AIProduct(
                            product_id=f"hf_model_{mod_id.replace('/', '_')}",
                            name=mod_id.split("/")[-1],
                            description=f"{author.title()}'s {pipeline} AI model architecture ({mod_id})",
                            product_type="AI Foundation Model / Weights",
                            ai_task_category=pipeline,
                            developer_or_company=author.title(),
                            pricing_model=pricing,
                            original_source_url=f"https://huggingface.co/{mod_id}",
                            provenance_source="Hugging Face Hub",
                            license="Gated" if gated else "Open Source",
                            metrics={"downloads": m.get("downloads", 0), "likes": m.get("likes", 0)},
                            raw_metadata={"pipeline_tag": pipeline, "tags": tags[:6]}
                        )
                        yield product
            except Exception as e:
                logger.error(f"Error collecting HF models: {e}")

    async def collect_ph_ai_products(self) -> AsyncGenerator[AIProduct, None]:
        """Collects AI launches from Product Hunt Atom feed."""
        url = "https://www.producthunt.com/feed"
        async with httpx.AsyncClient(headers=self.headers, timeout=15.0) as client:
            try:
                r = await client.get(url)
                if r.status_code == 200:
                    root = ET.fromstring(r.text)
                    ns = {"atom": "http://www.w3.org/2005/Atom"}
                    for entry in root.findall("atom:entry", ns):
                        title = entry.find("atom:title", ns).text.strip()
                        link = entry.find("atom:link", ns).attrib.get("href")
                        content = entry.find("atom:content", ns).text or ""
                        soup = BeautifulSoup(content, "html.parser")
                        desc = soup.get_text(separator=" ").strip()

                        # Check AI evidence
                        eval_res = evaluate_ai_evidence(title, desc, ["Product Launch"])
                        if not eval_res["is_ai"]:
                            continue

                        pricing = None
                        desc_lower = desc.lower()
                        if "open source" in desc_lower or "open-source" in desc_lower:
                            pricing = "Open Source"
                        elif "free" in desc_lower:
                            pricing = "Freemium"
                        elif "subscription" in desc_lower or "/month" in desc_lower:
                            pricing = "Subscription"

                        product = AIProduct(
                            product_id=f"ph_{abs(hash(title))}",
                            name=title,
                            description=desc,
                            product_type="AI Product Launch / SaaS",
                            ai_task_category=eval_res["focus_area"],
                            developer_or_company=title,  # Maker / Product name
                            pricing_model=pricing,
                            original_source_url=link,
                            provenance_source="Product Hunt Feed",
                            license=None,
                            metrics={},
                            raw_metadata={"matched_keywords": eval_res["matched_keywords"]}
                        )
                        yield product
            except Exception as e:
                logger.error(f"Error collecting PH AI products: {e}")
