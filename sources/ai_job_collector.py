"""
AI Job Acquisition Collector.
Phase II - Stage 2: Ingests, normalizes, categorizes, and deduplicates AI/ML vacancies
from legitimate public ATS and job APIs (Greenhouse, Lever, Arbeitnow, Jobicy, Remotive).
"""

import os
import sys
import re
import html
import logging
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone, timedelta
import httpx
from bs4 import BeautifulSoup

from core.job_schemas import (
    clean_html,
    normalize_employment_type,
    normalize_remote_type,
    normalize_experience_level,
    categorize_ai_job,
    extract_salary,
    extract_skills,
    generate_job_id,
    SUPPORTED_AI_CATEGORIES
)

logger = logging.getLogger("ai_job_collector")

PURE_PLAY_AI_COMPANIES = {
    "anthropic": "Anthropic",
    "scaleai": "Scale AI",
    "togetherai": "Together AI",
    "sambanovasystems": "SambaNova Systems",
    "cresta": "Cresta",
    "snorkelai": "Snorkel AI",
    "figure": "Figure AI",
    "stabilityai": "Stability AI",
    "labelbox": "Labelbox",
    "coreweave": "CoreWeave",
    "zilliz": "Zilliz"
}

GENERAL_TECH_COMPANIES = {
    "databricks": "Databricks",
    "palantir": "Palantir Technologies"
}

AI_ROLE_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
    "data scientist", "data science", "nlp", "natural language", "computer vision",
    "generative ai", "genai", "llm", "large language model", "foundation model",
    "mlops", "reinforcement learning", "robotics", "neural", "research scientist",
    "applied scientist", "prompt engineer", "ai safety", "alignment", "inference",
    "vector", "embedding", "rag", "cuda", "triton", "kernel", "gpu", "accelerator"
]


def is_ai_job(title: str, description: Optional[str] = None, tags: Optional[List[str]] = None, is_pure_play_ai: bool = False) -> bool:
    """Determine whether a job vacancy is AI/ML related."""
    t_lower = title.lower()
    
    # Exclude obvious non-technical roles unless title mentions AI
    non_tech_terms = ["recruiter", "account executive", "sales development", "workplace", "payroll", "facilities", "counsel", "legal", "hr ", "human resources"]
    if any(nt in t_lower for nt in non_tech_terms) and not any(k in t_lower for k in ["ai", "machine learning", "data", "ml"]):
        return False
        
    if is_pure_play_ai:
        return True

    text_to_check = f"{t_lower} {' '.join(str(t) for t in (tags or [])).lower()}"
    for kw in AI_ROLE_KEYWORDS:
        if len(kw) <= 3:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_to_check):
                return True
        else:
            if kw in text_to_check:
                return True
                
    if description:
        d_lower = description[:1500].lower()
        ai_matches = sum(1 for kw in AI_ROLE_KEYWORDS if kw in d_lower)
        if ai_matches >= 3:
            return True

    return False


class AIJobCollector:
    """Orchestrates multi-source collection of AI jobs."""

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "AIEcosystemCollector/1.0 (academic-research; contact: researcher@ecosystem.ai)"
        }
        self.collected_jobs: List[Dict[str, Any]] = []

    async def collect_greenhouse_board(self, client: httpx.AsyncClient, board_token: str, company_name: str, is_pure_play: bool) -> List[Dict[str, Any]]:
        """Collect vacancies from an official Greenhouse public API board."""
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
        jobs_found = []
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            r = await client.get(url, timeout=self.timeout)
            if r.status_code != 200:
                logger.warning(f"Greenhouse {board_token} returned {r.status_code}")
                return []
            data = r.json()
            raw_jobs = data.get("jobs", [])
            logger.info(f"Greenhouse [{company_name}]: {len(raw_jobs)} total listings fetched")

            for item in raw_jobs:
                title = (item.get("title") or "").strip()
                if not title:
                    continue

                raw_content = item.get("content") or ""
                desc_text = clean_html(raw_content)

                if not is_ai_job(title, desc_text, is_pure_play_ai=is_pure_play):
                    continue

                source_id = str(item.get("id", ""))
                app_url = item.get("absolute_url") or f"https://job-boards.greenhouse.io/{board_token}/jobs/{source_id}"

                loc_data = item.get("location") or {}
                location_name = loc_data.get("name") if isinstance(loc_data, dict) else str(loc_data)
                location_name = location_name.strip() if location_name else "Unspecified"

                remote_type = normalize_remote_type(None, location_name)
                category = categorize_ai_job(title, desc_text, company_name)
                exp_level = normalize_experience_level(title, desc_text)
                emp_type = normalize_employment_type(title)
                skills = extract_skills(f"{title} {desc_text}")
                sal_min, sal_max, currency = extract_salary(desc_text)

                # Posted timestamp
                updated_raw = item.get("updated_at")
                posted_dt = now_dt
                posted_at = now_iso
                if updated_raw:
                    try:
                        posted_dt = datetime.fromisoformat(updated_raw.replace("Z", "+00:00")).astimezone(timezone.utc)
                        posted_at = posted_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    except:
                        posted_at = now_iso

                # Vacancy Status determination (ACTIVE vs EXPIRED)
                # Postings older than 90 days are classified as EXPIRED
                age_days = (now_dt - posted_dt).days
                vacancy_status = "EXPIRED" if age_days > 90 else "ACTIVE"

                job_id = generate_job_id(f"Greenhouse: {company_name}", source_id, app_url)

                job_record = {
                    "jobId": job_id,
                    "jobTitle": title,
                    "companyName": company_name,
                    "category": category,
                    "jobDescription": desc_text,
                    "requiredSkills": skills,
                    "experienceLevel": exp_level,
                    "location": location_name,
                    "remoteType": remote_type,
                    "salaryMin": sal_min,
                    "salaryMax": sal_max,
                    "currency": currency,
                    "employmentType": emp_type,
                    "vacancyStatus": vacancy_status,
                    "applicationUrl": app_url,
                    "postedAt": posted_at,
                    "sourceName": f"Greenhouse: {company_name}",
                    "provenance": url,
                    "collectedAt": now_iso
                }
                jobs_found.append(job_record)

        except Exception as e:
            logger.error(f"Error collecting Greenhouse {board_token}: {e}")

        logger.info(f"Greenhouse [{company_name}]: {len(jobs_found)} valid AI vacancies extracted")
        return jobs_found

    async def collect_lever_board(self, client: httpx.AsyncClient, company_slug: str, company_name: str, is_pure_play: bool) -> List[Dict[str, Any]]:
        """Collect vacancies from an official Lever public API board."""
        url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
        jobs_found = []
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            r = await client.get(url, timeout=self.timeout)
            if r.status_code != 200:
                logger.warning(f"Lever {company_slug} returned {r.status_code}")
                return []
            raw_jobs = r.json()
            if not isinstance(raw_jobs, list):
                return []
            logger.info(f"Lever [{company_name}]: {len(raw_jobs)} total listings fetched")

            for item in raw_jobs:
                title = (item.get("text") or "").strip()
                if not title:
                    continue

                desc_plain = item.get("descriptionPlain") or clean_html(item.get("description"))

                if not is_ai_job(title, desc_plain, is_pure_play_ai=is_pure_play):
                    continue

                source_id = str(item.get("id", ""))
                app_url = item.get("applyUrl") or item.get("hostedUrl") or f"https://jobs.lever.co/{company_slug}/{source_id}"

                cats = item.get("categories") or {}
                location_name = cats.get("location") or "Unspecified"
                commitment = cats.get("commitment") or "Full-time"
                workplace = item.get("workplaceType")

                remote_type = normalize_remote_type(workplace, location_name)
                category = categorize_ai_job(title, desc_plain, company_name)
                exp_level = normalize_experience_level(title, desc_plain)
                emp_type = normalize_employment_type(commitment)
                skills = extract_skills(f"{title} {desc_plain}")
                sal_min, sal_max, currency = extract_salary(desc_plain)

                created_ts = item.get("createdAt")
                posted_dt = now_dt
                posted_at = now_iso
                if created_ts:
                    try:
                        posted_dt = datetime.fromtimestamp(created_ts / 1000.0, tz=timezone.utc)
                        posted_at = posted_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    except:
                        pass

                age_days = (now_dt - posted_dt).days
                vacancy_status = "EXPIRED" if age_days > 90 else "ACTIVE"

                job_id = generate_job_id(f"Lever: {company_name}", source_id, app_url)

                job_record = {
                    "jobId": job_id,
                    "jobTitle": title,
                    "companyName": company_name,
                    "category": category,
                    "jobDescription": desc_plain,
                    "requiredSkills": skills,
                    "experienceLevel": exp_level,
                    "location": location_name,
                    "remoteType": remote_type,
                    "salaryMin": sal_min,
                    "salaryMax": sal_max,
                    "currency": currency,
                    "employmentType": emp_type,
                    "vacancyStatus": vacancy_status,
                    "applicationUrl": app_url,
                    "postedAt": posted_at,
                    "sourceName": f"Lever: {company_name}",
                    "provenance": url,
                    "collectedAt": now_iso
                }
                jobs_found.append(job_record)

        except Exception as e:
            logger.error(f"Error collecting Lever {company_slug}: {e}")

        logger.info(f"Lever [{company_name}]: {len(jobs_found)} valid AI vacancies extracted")
        return jobs_found

    async def collect_arbeitnow(self, client: httpx.AsyncClient, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Collect AI vacancies from Arbeitnow official open API."""
        base_url = "https://www.arbeitnow.com/api/job-board-api"
        jobs_found = []
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        for page in range(1, max_pages + 1):
            page_url = f"{base_url}?page={page}"
            try:
                r = await client.get(page_url, timeout=self.timeout)
                if r.status_code != 200:
                    break
                data = r.json()
                items = data.get("data", [])
                if not items:
                    break

                for item in items:
                    title = (item.get("title") or "").strip()
                    if not title:
                        continue
                    desc_text = clean_html(item.get("description"))
                    tags = item.get("tags") or []

                    if not is_ai_job(title, desc_text, tags=tags, is_pure_play_ai=False):
                        continue

                    company = (item.get("company_name") or "Tech Employer").strip()
                    app_url = item.get("url") or f"https://www.arbeitnow.com/jobs/{item.get('slug', '')}"
                    source_id = str(item.get("slug") or app_url)
                    loc = item.get("location") or "Europe/Remote"
                    is_remote = item.get("remote", False)

                    remote_type = "REMOTE" if is_remote else normalize_remote_type(None, loc)
                    category = categorize_ai_job(title, desc_text, company)
                    exp_level = normalize_experience_level(title, desc_text)
                    job_types = item.get("job_types") or []
                    emp_type = normalize_employment_type(" ".join(str(jt) for jt in job_types) if job_types else "full_time")
                    skills = extract_skills(f"{title} {' '.join(str(t) for t in tags)} {desc_text}")
                    sal_min, sal_max, currency = extract_salary(desc_text)

                    created_ts = item.get("created_at")
                    posted_dt = now_dt
                    posted_at = now_iso
                    if created_ts:
                        try:
                            posted_dt = datetime.fromtimestamp(created_ts, tz=timezone.utc)
                            posted_at = posted_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                        except:
                            pass

                    age_days = (now_dt - posted_dt).days
                    vacancy_status = "EXPIRED" if age_days > 90 else "ACTIVE"

                    job_id = generate_job_id("Arbeitnow API", source_id, app_url)

                    job_record = {
                        "jobId": job_id,
                        "jobTitle": title,
                        "companyName": company,
                        "category": category,
                        "jobDescription": desc_text,
                        "requiredSkills": skills,
                        "experienceLevel": exp_level,
                        "location": loc,
                        "remoteType": remote_type,
                        "salaryMin": sal_min,
                        "salaryMax": sal_max,
                        "currency": currency,
                        "employmentType": emp_type,
                        "vacancyStatus": vacancy_status,
                        "applicationUrl": app_url,
                        "postedAt": posted_at,
                        "sourceName": "Arbeitnow API",
                        "provenance": page_url,
                        "collectedAt": now_iso
                    }
                    jobs_found.append(job_record)

                if not data.get("links", {}).get("next"):
                    break
            except Exception as e:
                logger.error(f"Error on Arbeitnow page {page}: {e}")
                break

        logger.info(f"Arbeitnow API: {len(jobs_found)} valid AI vacancies extracted")
        return jobs_found

    async def collect_jobicy(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Collect AI vacancies from Jobicy open remote jobs API."""
        url = "https://jobicy.com/api/v2/remote-jobs?count=100"
        jobs_found = []
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            r = await client.get(url, timeout=self.timeout)
            if r.status_code == 200:
                data = r.json()
                items = data.get("jobs", [])
                for item in items:
                    title = (item.get("jobTitle") or "").strip()
                    if not title:
                        continue
                    desc_text = clean_html(item.get("jobDescription"))
                    ind = item.get("jobIndustry") or []
                    ind_tags = ind if isinstance(ind, list) else [str(ind)]

                    if not is_ai_job(title, desc_text, tags=ind_tags, is_pure_play_ai=False):
                        continue

                    company = (item.get("companyName") or "Remote Employer").strip()
                    app_url = item.get("url") or f"https://jobicy.com/jobs/{item.get('jobSlug', '')}"
                    source_id = str(item.get("id") or item.get("jobSlug") or app_url)
                    loc = item.get("jobGeo") or "Remote"

                    remote_type = "REMOTE"
                    category = categorize_ai_job(title, desc_text, company)
                    exp_level = normalize_experience_level(title, desc_text)
                    emp_type = normalize_employment_type(str(item.get("jobType") or ""))
                    skills = extract_skills(f"{title} {desc_text}")
                    sal_min, sal_max, currency = extract_salary(desc_text)

                    pub_raw = item.get("pubDate")
                    posted_dt = now_dt
                    posted_at = now_iso
                    if pub_raw:
                        try:
                            posted_dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00")).astimezone(timezone.utc)
                            posted_at = posted_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                        except:
                            pass

                    age_days = (now_dt - posted_dt).days
                    vacancy_status = "EXPIRED" if age_days > 90 else "ACTIVE"

                    job_id = generate_job_id("Jobicy API", source_id, app_url)

                    job_record = {
                        "jobId": job_id,
                        "jobTitle": title,
                        "companyName": company,
                        "category": category,
                        "jobDescription": desc_text,
                        "requiredSkills": skills,
                        "experienceLevel": exp_level,
                        "location": loc,
                        "remoteType": remote_type,
                        "salaryMin": sal_min,
                        "salaryMax": sal_max,
                        "currency": currency,
                        "employmentType": emp_type,
                        "vacancyStatus": vacancy_status,
                        "applicationUrl": app_url,
                        "postedAt": posted_at,
                        "sourceName": "Jobicy API",
                        "provenance": url,
                        "collectedAt": now_iso
                    }
                    jobs_found.append(job_record)
        except Exception as e:
            logger.error(f"Error on Jobicy: {e}")

        logger.info(f"Jobicy API: {len(jobs_found)} valid AI vacancies extracted")
        return jobs_found

    async def collect_remotive(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Collect AI vacancies from Remotive open API."""
        url = "https://remotive.com/api/remote-jobs"
        jobs_found = []
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            r = await client.get(url, timeout=self.timeout)
            if r.status_code == 200:
                data = r.json()
                items = data.get("jobs", [])
                for item in items:
                    title = (item.get("title") or "").strip()
                    if not title:
                        continue
                    desc_text = clean_html(item.get("description"))
                    tags = item.get("tags") or []

                    if not is_ai_job(title, desc_text, tags=tags, is_pure_play_ai=False):
                        continue

                    company = (item.get("company_name") or "Remote Employer").strip()
                    app_url = item.get("url") or f"https://remotive.com/remote-jobs/{item.get('id', '')}"
                    source_id = str(item.get("id", ""))
                    loc = item.get("candidate_required_location") or "Remote"

                    remote_type = "REMOTE"
                    category = categorize_ai_job(title, desc_text, company)
                    exp_level = normalize_experience_level(title, desc_text)
                    emp_type = normalize_employment_type(str(item.get("job_type") or ""))
                    skills = extract_skills(f"{title} {' '.join(str(t) for t in tags)} {desc_text}")
                    sal_min, sal_max, currency = extract_salary(desc_text)

                    pub_raw = item.get("publication_date")
                    posted_dt = now_dt
                    posted_at = now_iso
                    if pub_raw:
                        try:
                            posted_dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00")).astimezone(timezone.utc)
                            posted_at = posted_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                        except:
                            pass

                    age_days = (now_dt - posted_dt).days
                    vacancy_status = "EXPIRED" if age_days > 90 else "ACTIVE"

                    job_id = generate_job_id("Remotive API", source_id, app_url)

                    job_record = {
                        "jobId": job_id,
                        "jobTitle": title,
                        "companyName": company,
                        "category": category,
                        "jobDescription": desc_text,
                        "requiredSkills": skills,
                        "experienceLevel": exp_level,
                        "location": loc,
                        "remoteType": remote_type,
                        "salaryMin": sal_min,
                        "salaryMax": sal_max,
                        "currency": currency,
                        "employmentType": emp_type,
                        "vacancyStatus": vacancy_status,
                        "applicationUrl": app_url,
                        "postedAt": posted_at,
                        "sourceName": "Remotive API",
                        "provenance": url,
                        "collectedAt": now_iso
                    }
                    jobs_found.append(job_record)
        except Exception as e:
            logger.error(f"Error on Remotive: {e}")

        logger.info(f"Remotive API: {len(jobs_found)} valid AI vacancies extracted")
        return jobs_found

    async def verify_sample_closed_status(self, client: httpx.AsyncClient, jobs: List[Dict[str, Any]], sample_size: int = 150):
        """Spot check sample jobs to detect actual CLOSED status (404, redirect to error=true)."""
        logger.info(f"Spot checking {min(sample_size, len(jobs))} jobs for closed status...")
        sem = asyncio.Semaphore(15)

        async def check_url(job: Dict[str, Any]):
            async with sem:
                u = job["applicationUrl"]
                try:
                    r = await client.get(u, timeout=5.0, follow_redirects=True)
                    if (r.status_code in (404, 410)) or ("error=true" in str(r.url)) or ("no longer available" in r.text.lower()) or ("job not found" in r.text.lower()):
                        job["vacancyStatus"] = "CLOSED"
                except:
                    pass

        tasks = [check_url(j) for j in jobs[:sample_size]]
        await asyncio.gather(*tasks, return_exceptions=True)

    def deduplicate_and_filter(self, raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate records by jobId, canonical URL, and (company, title, location)."""
        unique_records = []
        seen_ids = set()
        seen_urls = set()
        seen_signatures = set()

        for r in raw_records:
            jid = r["jobId"]
            url = r["applicationUrl"].strip().rstrip("/").lower()
            sig = f"{r['companyName'].strip().lower()}|{r['jobTitle'].strip().lower()}|{r['location'].strip().lower()}"

            if jid in seen_ids or url in seen_urls or sig in seen_signatures:
                continue

            if not (url.startswith("http://") or url.startswith("https://")):
                continue

            seen_ids.add(jid)
            seen_urls.add(url)
            seen_signatures.add(sig)
            unique_records.append(r)

        return unique_records

    async def run(self) -> List[Dict[str, Any]]:
        """Execute all collector routines asynchronously."""
        all_raw_jobs: List[Dict[str, Any]] = []

        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            tasks = []

            for token, name in PURE_PLAY_AI_COMPANIES.items():
                tasks.append(self.collect_greenhouse_board(client, token, name, is_pure_play=True))

            for token, name in GENERAL_TECH_COMPANIES.items():
                if token != "palantir":
                    tasks.append(self.collect_greenhouse_board(client, token, name, is_pure_play=False))

            tasks.append(self.collect_lever_board(client, "palantir", "Palantir Technologies", is_pure_play=False))
            tasks.append(self.collect_lever_board(client, "zilliz", "Zilliz", is_pure_play=True))
            tasks.append(self.collect_arbeitnow(client, max_pages=10))
            tasks.append(self.collect_jobicy(client))
            tasks.append(self.collect_remotive(client))

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in batch_results:
                if isinstance(res, list):
                    all_raw_jobs.extend(res)
                elif isinstance(res, Exception):
                    logger.error(f"Task encountered exception: {res}")

            logger.info(f"Total raw candidate vacancies collected: {len(all_raw_jobs)}")
            deduped = self.deduplicate_and_filter(all_raw_jobs)
            logger.info(f"Total unique AI job records after deduplication: {len(deduped)}")

            # Spot-check sample for CLOSED status
            await self.verify_sample_closed_status(client, deduped, sample_size=150)

        return deduped
