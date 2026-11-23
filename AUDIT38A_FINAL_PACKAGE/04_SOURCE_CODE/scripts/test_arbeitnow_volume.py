import httpx
import json

client = httpx.Client(timeout=10.0, headers={"User-Agent": "AIEcosystemCollector/1.0"})

total_jobs = 0
ai_jobs = 0

keywords = [
    "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
    "data scientist", "data science", "nlp", "natural language", "computer vision",
    "llm", "generative ai", "neural", "mlops", "robotics", "reinforcement learning"
]

for page in range(1, 10):
    url = f"https://www.arbeitnow.com/api/job-board-api?page={page}"
    r = client.get(url)
    if r.status_code != 200:
        print(f"Page {page} status: {r.status_code}")
        break
    data = r.json()
    jobs = data.get("data", [])
    if not jobs:
        break
    total_jobs += len(jobs)
    for j in jobs:
        text = (j.get("title", "") + " " + " ".join(j.get("tags", []))).lower()
        if any(k in text for k in keywords):
            ai_jobs += 1
    print(f"Page {page}: {len(jobs)} jobs (running total AI jobs: {ai_jobs})")
    if not data.get("links", {}).get("next"):
        break

print(f"Arbeitnow check finished. Total jobs inspected: {total_jobs}, AI jobs found: {ai_jobs}")
