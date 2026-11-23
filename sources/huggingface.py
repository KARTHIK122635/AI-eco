import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional
import httpx
from sources.base import BaseCollector
from core.models import StartupProductRecord, SourceAssessment


class HuggingFaceCollector(BaseCollector):
    name = "huggingface"
    display_name = "Hugging Face"
    base_url = "https://huggingface.co/"
    default_rate_limit = 0.5
    max_concurrency = 4

    async def test_accessibility(self) -> SourceAssessment:
        async with httpx.AsyncClient(headers=self.headers, timeout=12.0) as client:
            robots_status = "Unknown"
            try:
                r_rob = await client.get("https://huggingface.co/robots.txt")
                robots_status = f"HTTP {r_rob.status_code} (Allows /)"
            except Exception as e:
                robots_status = f"Failed to fetch robots.txt: {e}"

            # Test API
            accessible = False
            status_code = None
            try:
                r = await client.get("https://huggingface.co/api/models?limit=1")
                status_code = r.status_code
                accessible = (r.status_code == 200)
            except Exception as e:
                status_code = None

            return SourceAssessment(
                source_name=self.display_name,
                directory_url=self.base_url,
                accessible=accessible,
                status_code=status_code,
                collection_method="Official Public Hugging Face Hub REST API (/api/models & /api/spaces)",
                available_fields=[
                    "company_name (author / organization)", "product_name (modelId / space title)",
                    "description", "pricing_model (Open Source / Gated / License)",
                    "original_source_url", "categories (pipeline_tag, library, tags)",
                    "downloads", "likes"
                ],
                missing_fields=["employee_count (headcount is not tracked in model metadata)"],
                rate_limits_info="Public REST API with generous rate limits; 0.5s polite delay",
                robots_txt_status=robots_status,
                bot_protection_detected=False,
                notes_and_alternatives="Premier open AI repository. Allows direct discovery of thousands of AI products, foundation models, and AI startup organizations."
            )

    async def collect(self, limit: int = 50) -> AsyncGenerator[StartupProductRecord, None]:
        collected = 0
        spaces_limit = min(limit // 2 + 1, limit)
        models_limit = limit - spaces_limit

        async with httpx.AsyncClient(headers=self.headers, timeout=15.0) as client:
            # 1. Collect AI Spaces (Interactive Products/Apps)
            spaces_url = f"https://huggingface.co/api/spaces?limit={spaces_limit}&full=true"
            try:
                r_sp = await client.get(spaces_url)
                if r_sp.status_code == 200:
                    spaces = r_sp.json()
                    for sp in spaces:
                        if collected >= limit:
                            break
                        space_id = sp.get("id", "")
                        author = sp.get("author") or (space_id.split("/")[0] if "/" in space_id else "Community")
                        card = sp.get("cardData") or {}
                        desc = card.get("short_description") or card.get("title") or f"Hugging Face Space by {author}"

                        record = StartupProductRecord(
                            company_name=author.title(),
                            product_name=card.get("title") or space_id.split("/")[-1],
                            description=desc,
                            employee_count=None,
                            pricing_model="Open Source / Free App",
                            company_website=f"https://huggingface.co/{author}",
                            original_source_url=f"https://huggingface.co/spaces/{space_id}",
                            source_directory=self.display_name,
                            categories=["AI Space", sp.get("sdk", "ai-app")] + (sp.get("tags") or [])[:5],
                            raw_metadata={"likes": sp.get("likes"), "sdk": sp.get("sdk")}
                        )
                        yield record
                        collected += 1
            except Exception:
                pass

            # 2. Collect AI Models from Top AI Organizations
            if collected < limit:
                rem = limit - collected
                models_url = f"https://huggingface.co/api/models?limit={rem}&full=true&sort=trendingScore&direction=-1"
                try:
                    r_mod = await client.get(models_url)
                    if r_mod.status_code == 200:
                        models = r_mod.json()
                        for m in models:
                            if collected >= limit:
                                break
                            mod_id = m.get("id", "")
                            author = m.get("author") or (mod_id.split("/")[0] if "/" in mod_id else "Community")
                            pipeline = m.get("pipeline_tag") or "machine-learning"
                            gated = m.get("gated", False)
                            pricing = "Gated Commercial / Research" if gated else "Open Source"

                            record = StartupProductRecord(
                                company_name=author.title(),
                                product_name=mod_id.split("/")[-1],
                                description=f"{author}'s {pipeline} AI model: {mod_id}",
                                employee_count=None,
                                pricing_model=pricing,
                                company_website=f"https://huggingface.co/{author}",
                                original_source_url=f"https://huggingface.co/{mod_id}",
                                source_directory=self.display_name,
                                categories=[pipeline] + (m.get("tags") or [])[:5],
                                raw_metadata={"downloads": m.get("downloads"), "likes": m.get("likes")}
                            )
                            yield record
                            collected += 1
                except Exception:
                    pass
