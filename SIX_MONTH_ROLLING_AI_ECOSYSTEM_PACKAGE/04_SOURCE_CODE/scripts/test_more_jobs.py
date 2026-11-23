import httpx
import json

client = httpx.Client(timeout=10.0, headers={"User-Agent": "AIEcosystemCollector/1.0 (academic-research)"})

greenhouse_candidates = [
    "anthropic", "scaleai", "databricks", "cohere", "elevenlabs", "runwayml", "runway",
    "perplexity", "perplexityai", "mistralai", "glean", "shieldai", "stabilityai",
    "synthesia", "cerebras", "sambanovasystems", "groq", "deepl", "pinecone", "weaviate",
    "wandb", "anyscale", "modal", "togetherai", "lambdalabs", "coreweave", "jasper",
    "characterai", "figure", "appliedintuition", "cursor", "cognition", "poolside"
]

print("=== Testing Greenhouse Boards ===")
gh_results = {}
total_gh_jobs = 0
for b in greenhouse_candidates:
    try:
        r = client.get(f"https://boards-api.greenhouse.io/v1/boards/{b}/jobs")
        if r.status_code == 200:
            jobs = r.json().get("jobs", [])
            gh_results[b] = len(jobs)
            total_gh_jobs += len(jobs)
            print(f"  [GH 200] {b}: {len(jobs)} jobs")
        elif r.status_code != 404:
            print(f"  [GH {r.status_code}] {b}")
    except Exception as e:
        pass

print(f"Total active Greenhouse boards: {len(gh_results)}, total jobs: {total_gh_jobs}")

lever_candidates = [
    "palantir", "writer", "replit", "jasper", "scale", "midjourney", "cohere",
    "huggingface", "openai", "perplexity", "stability", "elevenlabs", "groq",
    "anthropic", "anduril", "nuro", "c3ai", "dataminr"
]

print("\n=== Testing Lever Boards ===")
lever_results = {}
total_lever_jobs = 0
for comp in lever_candidates:
    try:
        r = client.get(f"https://api.lever.co/v0/postings/{comp}?mode=json")
        if r.status_code == 200:
            jobs = r.json()
            if isinstance(jobs, list):
                lever_results[comp] = len(jobs)
                total_lever_jobs += len(jobs)
                print(f"  [Lever 200] {comp}: {len(jobs)} jobs")
    except Exception as e:
        pass

print(f"Total active Lever boards: {len(lever_results)}, total jobs: {total_lever_jobs}")

print("\n=== Testing Arbeitnow Pagination ===")
try:
    r = client.get("https://www.arbeitnow.com/api/job-board-api?page=1")
    if r.status_code == 200:
        d = r.json()
        print(f"Arbeitnow page 1: {len(d.get('data', []))} jobs, next page: {d.get('links', {}).get('next')}")
except Exception as e:
    print(f"Arbeitnow error: {e}")

print("\n=== Testing Jobicy ===")
try:
    r = client.get("https://jobicy.com/api/v2/remote-jobs?count=100")
    if r.status_code == 200:
        d = r.json()
        jobs = d.get("jobs", [])
        print(f"Jobicy jobs: {len(jobs)}")
        if jobs:
            print("Jobicy fields:", list(jobs[0].keys()))
except Exception as e:
    print(f"Jobicy error: {e}")

print("\n=== Testing Remotive ===")
try:
    r = client.get("https://remotive.com/api/remote-jobs")
    if r.status_code == 200:
        d = r.json()
        jobs = d.get("jobs", [])
        print(f"Remotive all jobs: {len(jobs)}")
except Exception as e:
    print(f"Remotive error: {e}")
