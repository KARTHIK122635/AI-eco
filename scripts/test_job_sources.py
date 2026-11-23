import httpx
import json
import feedparser

client = httpx.Client(timeout=15.0, headers={"User-Agent": "AIEcosystemCollector/1.0 (academic-research)"})

print("=== 1. Testing Remotive API ===")
try:
    r = client.get("https://remotive.com/api/remote-jobs?category=software-dev&limit=50")
    print(f"Remotive software-dev status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        jobs = data.get("jobs", [])
        print(f"Remotive returned {len(jobs)} jobs. Total job-count: {data.get('job-count')}")
        # Let's count AI/ML jobs
        ai_terms = ["ai", "machine learning", "ml", "deep learning", "nlp", "computer vision", "data scientist", "llm"]
        ai_jobs = [j for j in jobs if any(t in j.get("title", "").lower() or t in " ".join(j.get("tags", [])).lower() for t in ai_terms)]
        print(f"Sample Remotive AI jobs in first 50: {len(ai_jobs)}")
        if ai_jobs:
            print("Sample job:", ai_jobs[0]["title"], "at", ai_jobs[0]["company_name"], "url:", ai_jobs[0]["url"])
except Exception as e:
    print(f"Remotive error: {e}")

print("\n=== 2. Testing Arbeitnow API ===")
try:
    r = client.get("https://www.arbeitnow.com/api/job-board-api")
    print(f"Arbeitnow status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        jobs = data.get("data", [])
        print(f"Arbeitnow returned {len(jobs)} jobs.")
        ai_jobs = [j for j in jobs if any(t in j.get("title", "").lower() or t in " ".join(j.get("tags", [])).lower() for t in ["ai", "machine learning", "ml", "data"])]
        print(f"Sample Arbeitnow AI jobs in first batch: {len(ai_jobs)}")
        if ai_jobs:
            print("Sample job:", ai_jobs[0]["title"], "at", ai_jobs[0]["company_name"], "url:", ai_jobs[0]["url"])
except Exception as e:
    print(f"Arbeitnow error: {e}")

print("\n=== 3. Testing Jobicy API ===")
try:
    r = client.get("https://jobicy.com/api/v2/remote-jobs?count=50&industry=engineering")
    print(f"Jobicy status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        jobs = data.get("jobs", [])
        print(f"Jobicy returned {len(jobs)} jobs.")
        ai_jobs = [j for j in jobs if any(t in j.get("jobTitle", "").lower() for t in ["ai", "machine learning", "data", "ml"])]
        print(f"Sample Jobicy AI jobs: {len(ai_jobs)}")
        if ai_jobs:
            print("Sample job:", ai_jobs[0]["jobTitle"], "at", ai_jobs[0]["companyName"], "url:", ai_jobs[0]["jobUrl"])
except Exception as e:
    print(f"Jobicy error: {e}")

print("\n=== 4. Testing Greenhouse Public API ===")
sample_boards = ["openai", "anthropic", "scaleai", "databricks", "huggingface", "cohere", "elevenlabs", "runway", "perplexity", "mistral", "glean", "shieldai"]
for board in sample_boards[:5]:
    try:
        r = client.get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true")
        print(f"Greenhouse {board} status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            jobs = data.get("jobs", [])
            print(f"  {board}: {len(jobs)} total jobs posted")
            if jobs:
                print(f"  Sample job: {jobs[0].get('title')} (id: {jobs[0].get('id')})")
    except Exception as e:
        print(f"Greenhouse {board} error: {e}")

print("\n=== 5. Testing Lever Public API ===")
sample_lever = ["palantir", "character-ai", "writer", "replit"]
for company in sample_lever:
    try:
        r = client.get(f"https://api.lever.co/v0/postings/{company}?mode=json")
        print(f"Lever {company} status: {r.status_code}")
        if r.status_code == 200:
            jobs = r.json()
            print(f"  {company}: {len(jobs)} jobs posted")
            if jobs:
                print(f"  Sample job: {jobs[0].get('text')}")
    except Exception as e:
        print(f"Lever {company} error: {e}")
