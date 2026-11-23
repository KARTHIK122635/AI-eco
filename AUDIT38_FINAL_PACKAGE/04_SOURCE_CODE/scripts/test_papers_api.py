import httpx
import xml.etree.ElementTree as ET
import time

print("Testing arXiv API...")
arxiv_url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.CV&start=0&max_results=10"
t0 = time.time()
r_arxiv = httpx.get(arxiv_url, timeout=15)
t1 = time.time()
print(f"arXiv status: {r_arxiv.status_code}, time: {t1-t0:.2f}s, len: {len(r_arxiv.text)}")

if r_arxiv.status_code == 200:
    root = ET.fromstring(r_arxiv.text)
    ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
    entries = root.findall('atom:entry', ns)
    print(f"arXiv entries returned: {len(entries)}")
    if entries:
        e = entries[0]
        title = e.find('atom:title', ns).text.strip().replace('\n', ' ')
        link = e.find('atom:id', ns).text.strip()
        pub = e.find('atom:published', ns).text.strip()
        authors = [a.find('atom:name', ns).text.strip() for a in e.findall('atom:author', ns)]
        summary = e.find('atom:summary', ns).text.strip().replace('\n', ' ')[:100]
        comment = e.find('arxiv:comment', ns)
        comment_text = comment.text if comment is not None else ""
        print(f"Sample title: {title}")
        print(f"Sample link: {link}")
        print(f"Sample pub: {pub}")
        print(f"Sample authors: {authors[:3]}")
        print(f"Sample comment: {comment_text}")

print("\nTesting Papers with Code API...")
pwc_url = "https://paperswithcode.com/api/v1/papers/?page=1"
try:
    r_pwc = httpx.get(pwc_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
    print(f"PwC status: {r_pwc.status_code}")
    if r_pwc.status_code == 200:
        data = r_pwc.json()
        print(f"PwC count: {data.get('count')}, results: {len(data.get('results', []))}")
        if data.get('results'):
            print("PwC sample paper:", data['results'][0])
except Exception as e:
    print(f"PwC error: {e}")
