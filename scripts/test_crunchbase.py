import httpx

client = httpx.Client(headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
})

url = "https://www.crunchbase.com/robots.txt"
r = client.get(url)
print("Crunchbase robots.txt:")
print(r.text[:1000])

url_org = "https://www.crunchbase.com/organization/openai"
try:
    r_org = client.get(url_org)
    print("\nCrunchbase org OpenAI status:", r_org.status_code)
    print("Crunchbase org OpenAI headers:", dict(r_org.headers))
    print("Crunchbase snippet:", r_org.text[:400])
except Exception as e:
    print("Error querying crunchbase org:", e)
