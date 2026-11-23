import httpx
import json
from bs4 import BeautifulSoup

def extract_wellfound_company(slug: str):
    url = f"https://wellfound.com/company/{slug}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    r = httpx.get(url, headers=headers, follow_redirects=True, timeout=15)
    if r.status_code != 200:
        return {"status": r.status_code, "error": "Failed to fetch"}
    
    soup = BeautifulSoup(r.text, 'html.parser')
    script = soup.find('script', id='__NEXT_DATA__')
    if not script or not script.string:
        return {"status": r.status_code, "error": "No __NEXT_DATA__"}
    
    data = json.loads(script.string)
    apollo = data.get('props', {}).get('pageProps', {}).get('apolloState', {}).get('data', {})
    
    # Find the main startup
    startup_data = None
    for k, v in apollo.items():
        if isinstance(v, dict) and v.get('__typename') == 'Startup' and v.get('slug') == slug:
            startup_data = v
            break
    
    # If not matched by slug, find the one with companySize
    if not startup_data:
        for k, v in apollo.items():
            if isinstance(v, dict) and v.get('__typename') == 'Startup' and v.get('companySize'):
                startup_data = v
                break
                
    if not startup_data:
        return {"status": 200, "error": "Startup entity not found in Apollo"}
        
    # Extract tags
    tags = []
    for k, v in apollo.items():
        if isinstance(v, dict) and v.get('__typename') == 'NewTag' and v.get('name'):
            tags.append(v.get('name'))

    return {
        "status": 200,
        "name": startup_data.get('name'),
        "slug": startup_data.get('slug'),
        "high_concept": startup_data.get('highConcept'),
        "company_size": startup_data.get('companySize'),
        "website_url": startup_data.get('websiteUrl'),
        "tags": tags[:8],
        "url": url
    }

print("Testing Wellfound extraction for 'stripe':")
res = extract_wellfound_company("stripe")
print(json.dumps(res, indent=2))

print("\nTesting Wellfound extraction for 'labelbox':")
res2 = extract_wellfound_company("labelbox")
print(json.dumps(res2, indent=2))
