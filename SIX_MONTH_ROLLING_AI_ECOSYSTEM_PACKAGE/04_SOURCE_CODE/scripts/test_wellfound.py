import httpx

client = httpx.Client(headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}, follow_redirects=True)

url = "https://wellfound.com/robots.txt"
r = client.get(url)
print("Wellfound robots.txt status:", r.status_code)
print("Wellfound robots.txt:")
print(r.text[:800])

for path in ["https://wellfound.com/companies", "https://wellfound.com/startups", "https://wellfound.com/company/stripe"]:
    try:
        r2 = client.get(path)
        print(f"\nPath: {path}")
        print("Status:", r2.status_code)
        print("Headers:", dict(r2.headers).get('cf-mitigated'), dict(r2.headers).get('server'))
        if "<title>" in r2.text:
            title = r2.text.split("<title>")[1].split("</title>")[0]
            print("Title:", title)
    except Exception as e:
        print(f"Error on {path}:", e)
