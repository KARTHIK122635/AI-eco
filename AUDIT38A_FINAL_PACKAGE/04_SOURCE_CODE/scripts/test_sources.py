import urllib.request
import ssl
import json
import httpx

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

targets = [
    ('Y Combinator', 'https://www.ycombinator.com/companies', 'https://www.ycombinator.com/robots.txt'),
    ('Crunchbase', 'https://www.crunchbase.com/', 'https://www.crunchbase.com/robots.txt'),
    ('Wellfound', 'https://wellfound.com/', 'https://wellfound.com/robots.txt'),
    ('Product Hunt', 'https://www.producthunt.com/', 'https://www.producthunt.com/robots.txt'),
    ('Hugging Face', 'https://huggingface.co/', 'https://huggingface.co/robots.txt')
]

client = httpx.Client(headers=headers, follow_redirects=True, timeout=15.0)

for name, url, robots_url in targets:
    print(f"==================================================")
    print(f"Testing Source: {name}")
    print(f"URL: {url}")
    print(f"==================================================")
    
    # 1. robots.txt
    try:
        r_robots = client.get(robots_url)
        print(f"robots.txt HTTP Status: {r_robots.status_code}")
        first_few = "\n".join([line for line in r_robots.text.splitlines() if not line.startswith("#")][:15])
        print(f"robots.txt excerpt:\n{first_few}")
    except Exception as e:
        print(f"robots.txt check failed: {e}")
        
    # 2. Main Page / Directory Page
    try:
        r_main = client.get(url)
        print(f"\nTarget HTTP Status: {r_main.status_code}")
        print(f"Target Content-Type: {r_main.headers.get('content-type')}")
        print(f"Server header: {r_main.headers.get('server')}")
        is_cf = 'cf-ray' in r_main.headers or 'cloudflare' in str(r_main.headers.get('server', '')).lower()
        print(f"Cloudflare detected: {is_cf}")
        if "challenge" in r_main.text.lower() or "just a moment" in r_main.text.lower():
            print("CAPTCHA / Cloudflare Turnstile Challenge detected!")
        else:
            print(f"Response Body Sample (first 250 chars):\n{r_main.text[:250].strip()}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP Status Error: {e.response.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")
    print("\n")
