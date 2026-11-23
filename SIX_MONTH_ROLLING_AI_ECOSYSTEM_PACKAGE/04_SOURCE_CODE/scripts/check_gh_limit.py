import httpx

try:
    r = httpx.get("https://api.github.com/rate_limit", headers={"User-Agent": "AntigravityDataVerification/1.0"})
    print("GitHub API Rate Limit Status:")
    print("Status code:", r.status_code)
    data = r.json()
    core = data.get("resources", {}).get("core", {})
    print(f"Limit: {core.get('limit')}, Remaining: {core.get('remaining')}, Reset timestamp: {core.get('reset')}")
except Exception as e:
    print("Error querying GitHub API:", e)
