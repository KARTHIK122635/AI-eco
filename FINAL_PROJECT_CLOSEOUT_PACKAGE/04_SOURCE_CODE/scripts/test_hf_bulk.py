import httpx
import time

client = httpx.Client(headers={'User-Agent': 'ProductDataCollector/2.0'}, timeout=15)

# Test fetching spaces
t0 = time.time()
r_sp = client.get("https://huggingface.co/api/spaces?limit=500&full=true")
t1 = time.time()
print(f"HF Spaces status: {r_sp.status_code}, count: {len(r_sp.json()) if r_sp.status_code==200 else 0}, time: {t1-t0:.2f}s")

# Test fetching models
t2 = time.time()
r_mod = client.get("https://huggingface.co/api/models?limit=500&full=true&sort=trendingScore&direction=-1")
t3 = time.time()
print(f"HF Models status: {r_mod.status_code}, count: {len(r_mod.json()) if r_mod.status_code==200 else 0}, time: {t3-t2:.2f}s")
