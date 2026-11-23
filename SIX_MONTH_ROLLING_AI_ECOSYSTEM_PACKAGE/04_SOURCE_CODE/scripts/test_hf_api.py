import httpx
import json

client = httpx.Client(headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}, timeout=10.0)

# Test Spaces (AI applications/products)
r_spaces = client.get("https://huggingface.co/api/spaces?limit=5&full=true")
print("HF Spaces status:", r_spaces.status_code)
if r_spaces.status_code == 200:
    spaces = r_spaces.json()
    print("Found spaces:", len(spaces))
    if spaces:
        print("Sample space keys:", list(spaces[0].keys()))
        print("Sample space:", json.dumps(spaces[0], indent=2)[:400])

# Test Organization (Company/Startup)
sample_org = "meta-llama" # or "deepseek-ai", "mistralai", "cohere", "stabilityai"
r_org = client.get(f"https://huggingface.co/api/organizations/{sample_org}")
print(f"\nHF Org {sample_org} status:", r_org.status_code)
if r_org.status_code == 200:
    print("Org data:", json.dumps(r_org.json(), indent=2)[:400])

# Test Models (AI Products/Weights)
r_models = client.get("https://huggingface.co/api/models?limit=5&full=true")
print("\nHF Models status:", r_models.status_code)
if r_models.status_code == 200:
    models = r_models.json()
    if models:
        print("Sample model keys:", list(models[0].keys()))
