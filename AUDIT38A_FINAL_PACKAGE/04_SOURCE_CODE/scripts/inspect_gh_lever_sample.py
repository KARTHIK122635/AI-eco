import httpx
import json

client = httpx.Client(timeout=10.0, headers={"User-Agent": "AIEcosystemCollector/1.0"})

# Check Anthropic job sample
r = client.get("https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true")
if r.status_code == 200:
    jobs = r.json().get("jobs", [])
    print(f"Anthropic returned {len(jobs)} jobs")
    # inspect first job
    if jobs:
        j = jobs[0]
        print("Keys:", list(j.keys()))
        print("Title:", j.get("title"))
        print("Location:", j.get("location"))
        print("Departments:", j.get("departments"))
        print("Updated_at:", j.get("updated_at"))
        print("Absolute_url:", j.get("absolute_url"))
        print("Content preview:", (j.get("content") or "")[:200])

# Check Palantir Lever job sample
r2 = client.get("https://api.lever.co/v0/postings/palantir?mode=json")
if r2.status_code == 200:
    jobs2 = r2.json()
    print(f"\nPalantir returned {len(jobs2)} jobs")
    if jobs2:
        j2 = jobs2[0]
        print("Keys:", list(j2.keys()))
        print("Text:", j2.get("text"))
        print("Categories:", j2.get("categories"))
        print("HostedUrl:", j2.get("hostedUrl"))
        print("CreatedAt:", j2.get("createdAt"))
        print("Description preview:", (j2.get("descriptionPlain") or "")[:200])
