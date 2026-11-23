import asyncio
import httpx
import re
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator

logger = logging.getLogger("ResearchPaperCollector")


class ResearchPaperCollector:
    """
    Collects at least 1,000 unique AI research papers from arXiv API
    and Hugging Face Daily Papers, cross-referencing GitHub code repositories
    and star metrics.
    """
    ARXIV_BASE_URL = "https://export.arxiv.org/api/query"

    def __init__(self):
        self.http_client = httpx.AsyncClient(
            headers={"User-Agent": "AcademicAIResearchHarvester/1.0 (academic-research@aisolution.internal)"},
            follow_redirects=True,
            timeout=15.0
        )
        self.github_stars_cache: Dict[str, Optional[int]] = {}
        self.github_rate_limited: bool = False

    async def close(self):
        await self.http_client.aclose()

    def _extract_github_url(self, text: str) -> Optional[str]:
        """Extracts valid GitHub repository URL from text if present."""
        if not text:
            return None
        match = re.search(r'https?://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)', text)
        if match:
            owner = match.group(1)
            repo = match.group(2).rstrip('.').rstrip(')').rstrip('/')
            if owner.lower() not in ['sponsors', 'topics', 'features', 'site', 'about', 'blog']:
                return f"https://github.com/{owner}/{repo}"
        return None

    async def fetch_github_stars(self, github_url: str) -> Optional[int]:
        """Fetches live stargazers count from official GitHub REST API with rate limit safety."""
        if not github_url or self.github_rate_limited:
            return None
        match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
        if not match:
            return None
        owner, repo = match.group(1), match.group(2).rstrip('.git').rstrip('/')
        repo_key = f"{owner}/{repo}"

        if repo_key in self.github_stars_cache:
            return self.github_stars_cache[repo_key]

        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            r = await self.http_client.get(api_url, timeout=2.5)
            if r.status_code == 200:
                stars = r.json().get("stargazers_count")
                self.github_stars_cache[repo_key] = stars
                return stars
            elif r.status_code == 403:
                # Rate limited by GitHub unauthenticated quota
                self.github_rate_limited = True
                logger.info("GitHub API unauthenticated rate limit reached. Retaining repo URLs with null stars.")
                return None
        except Exception:
            pass

        self.github_stars_cache[repo_key] = None
        return None

    async def collect_daily_papers_hf(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Collects verified daily AI research papers from Hugging Face Daily Papers API (limit <= 100)."""
        papers = []
        safe_limit = min(limit, 100)
        try:
            r = await self.http_client.get(f"https://huggingface.co/api/daily_papers?limit={safe_limit}")
            if r.status_code == 200:
                items = r.json()
                for it in items:
                    p = it.get("paper", {})
                    paper_id = p.get("id")
                    title = p.get("title") or it.get("title")
                    if not title or not paper_id:
                        continue
                    authors = [a.get("name") for a in p.get("authors", []) if isinstance(a, dict) and a.get("name")]
                    github_repo = p.get("githubRepo")
                    github_stars = p.get("githubStars")

                    papers.append({
                        "paper_id": f"arxiv_{paper_id.replace('.', '_')}",
                        "title": title.strip().replace("\n", " "),
                        "authors": authors,
                        "paper_url": f"https://arxiv.org/abs/{paper_id}",
                        "publication_date": p.get("publishedAt") or it.get("publishedAt"),
                        "categories": ["cs.AI", "cs.LG", "cs.CL"],
                        "abstract": p.get("summary", "").strip().replace("\n", " "),
                        "github_url": github_repo if github_repo else None,
                        "github_stars": github_stars if github_stars is not None else None,
                        "provenance": "Hugging Face Daily Papers & arXiv"
                    })
        except Exception as e:
            logger.error(f"Error collecting HF daily papers: {e}")
        return papers

    async def collect_arxiv_papers(self, target_count: int = 1050) -> AsyncGenerator[Dict[str, Any], None]:
        """Collects AI papers from arXiv API with batch pagination across cs.AI, cs.LG, cs.CL, cs.CV."""
        query = "cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.CV"
        batch_size = 250
        start = 0
        yielded_urls = set()

        # 1. First yield verified HF daily papers with pre-linked code
        hf_papers = await self.collect_daily_papers_hf(limit=150)
        for hp in hf_papers:
            yielded_urls.add(hp["paper_url"])
            yield hp

        # 2. Query arXiv API in fast 250-item pages
        while len(yielded_urls) < target_count:
            url = f"{self.ARXIV_BASE_URL}?search_query={query}&start={start}&max_results={batch_size}&sortBy=submittedDate&sortOrder=descending"
            try:
                r = await self.http_client.get(url, timeout=20.0)
                if r.status_code != 200:
                    break

                root = ET.fromstring(r.text)
                ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
                entries = root.findall("atom:entry", ns)
                if not entries:
                    break

                for entry in entries:
                    id_elem = entry.find("atom:id", ns)
                    paper_url = id_elem.text.strip().replace("http://", "https://") if id_elem is not None else ""
                    if not paper_url or paper_url in yielded_urls:
                        continue

                    title_elem = entry.find("atom:title", ns)
                    title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else "Untitled"

                    summary_elem = entry.find("atom:summary", ns)
                    abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else ""

                    published_elem = entry.find("atom:published", ns)
                    pub_date = published_elem.text.strip() if published_elem is not None else ""

                    authors = []
                    for a in entry.findall("atom:author", ns):
                        name_elem = a.find("atom:name", ns)
                        if name_elem is not None and name_elem.text:
                            authors.append(name_elem.text.strip())

                    categories = []
                    for c in entry.findall("atom:category", ns):
                        term = c.attrib.get("term")
                        if term:
                            categories.append(term)

                    comment_elem = entry.find("arxiv:comment", ns)
                    comment_text = comment_elem.text if comment_elem is not None else ""

                    # Correlate GitHub repo
                    github_url = self._extract_github_url(f"{comment_text} {abstract}")
                    github_stars = None
                    if github_url and not self.github_rate_limited:
                        github_stars = await self.fetch_github_stars(github_url)

                    raw_id = paper_url.split("/abs/")[-1] if "/abs/" in paper_url else paper_url.split("/")[-1]
                    canonical_id = f"arxiv_{raw_id.replace('.', '_').replace('/', '_')}"

                    record = {
                        "paper_id": canonical_id,
                        "title": title,
                        "authors": authors,
                        "paper_url": paper_url,
                        "publication_date": pub_date,
                        "categories": categories,
                        "abstract": abstract,
                        "github_url": github_url,
                        "github_stars": github_stars,
                        "provenance": "arXiv API"
                    }

                    yielded_urls.add(paper_url)
                    yield record
                    if len(yielded_urls) >= target_count:
                        break

                start += batch_size
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Error querying arXiv start={start}: {e}")
                break
