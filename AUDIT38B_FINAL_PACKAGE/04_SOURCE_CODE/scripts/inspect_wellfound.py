import httpx
from bs4 import BeautifulSoup

client = httpx.Client(headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}, follow_redirects=True)

r = client.get("https://wellfound.com/startups")
soup = BeautifulSoup(r.text, 'html.parser')

print("Page Title:", soup.title.string if soup.title else None)
links = soup.find_all('a', href=True)
company_links = [l['href'] for l in links if '/company/' in l['href']]
print("Found company links:", len(company_links))
print("Sample company links:", list(set(company_links))[:10])

# Check stripe page
r_stripe = client.get("https://wellfound.com/company/stripe")
soup_stripe = BeautifulSoup(r_stripe.text, 'html.parser')
print("\nStripe page title:", soup_stripe.title.string if soup_stripe.title else None)
# Check for json-ld or next data
scripts = soup_stripe.find_all('script')
for s in scripts:
    if s.get('type') == 'application/ld+json':
        print("JSON-LD found:", s.string[:200] if s.string else '')
    if s.get('id') == '__NEXT_DATA__':
        print("__NEXT_DATA__ found, length:", len(s.string) if s.string else 0)
